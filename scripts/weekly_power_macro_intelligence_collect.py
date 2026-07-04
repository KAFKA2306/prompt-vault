#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from html.parser import HTMLParser
from pathlib import Path


CONFIG_PATH = Path("config/weekly_power_macro_intelligence_sources.json")
OUTPUT_ROOT = Path("outputs/weekly-power-macro-intelligence")
USER_AGENT = "KAFKA Weekly Power Macro Intelligence (+https://github.com/KAFKA2306)"

DATE_PATTERNS = [
    re.compile(r"(?P<year>20\d{2})[./-](?P<month>\d{1,2})[./-](?P<day>\d{1,2})"),
    re.compile(r"(?P<year>20\d{2})年\s*(?P<month>\d{1,2})月\s*(?P<day>\d{1,2})日"),
]


class TextHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self._in_title = False
        self._skip = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript", "svg"}:
            self._skip += 1
        if tag == "title":
            self._in_title = True
        if tag in {"p", "li", "tr", "h1", "h2", "h3", "h4", "div", "br"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript", "svg"} and self._skip:
            self._skip -= 1
        if tag == "title":
            self._in_title = False
        if tag in {"p", "li", "tr", "h1", "h2", "h3", "h4", "div"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip:
            return
        text = html.unescape(data).strip()
        if not text:
            return
        if self._in_title:
            self.title = f"{self.title} {text}".strip()
        self.parts.append(text)

    def text(self) -> str:
        raw = " ".join(self.parts)
        lines = []
        for line in raw.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
            line = " ".join(line.split())
            if line:
                lines.append(line)
        return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--week-end", default=dt.date.today().isoformat())
    parser.add_argument("--start")
    parser.add_argument("--end")
    parser.add_argument("--output-root", default=str(OUTPUT_ROOT))
    parser.add_argument("--max-snippet-chars", type=int, default=900)
    parser.add_argument("--max-source-items", type=int, default=30)
    return parser.parse_args()


def parse_gate_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("gate")
    parser.add_argument("--week-end", required=True)
    parser.add_argument("--output-root", default=str(OUTPUT_ROOT))
    parser.add_argument("--min-items", type=int, default=10)
    parser.add_argument("--min-url-rate", type=float, default=0.95)
    parser.add_argument("--min-date-rate", type=float, default=0.70)
    parser.add_argument("--min-non-metadata-rate", type=float, default=0.30)
    parser.add_argument("--min-layers", type=int, default=4)
    return parser.parse_args()


def date_arg(value: str) -> dt.date:
    return dt.date.fromisoformat(value)


def load_sources() -> list[dict]:
    data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    sources = data.get("sources", [])
    return [src for src in sources if isinstance(src, dict) and src.get("id") and src.get("url")]


def source_layer(source: dict) -> str:
    if source.get("layer"):
        return str(source["layer"])
    source_class = str(source.get("source_class", ""))
    if source_class in {"market_expectation", "earnings"}:
        return "L0_market_price"
    if source_class == "market_narrative":
        return "L6_personal_macro_narrative"
    return "L5_analyst_interpretation"


def robots_lines(url: str) -> list[str] | None:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            raw = response.read(200_000)
    except Exception:
        return None
    try:
        text = raw.decode("utf-8", errors="replace")
    except Exception:
        return None
    return text.splitlines()


def can_fetch(url: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    robots_url = urllib.parse.urlunparse((parsed.scheme, parsed.netloc, "/robots.txt", "", "", ""))
    parser = urllib.robotparser.RobotFileParser()
    parser.set_url(robots_url)
    lines = robots_lines(robots_url)
    if lines is None:
        return True
    parser.parse(lines)
    return parser.can_fetch(USER_AGENT, url) or parser.can_fetch("*", url)


def fetch(url: str) -> tuple[str, str, str]:
    if not can_fetch(url):
        return "", "", "ROBOTS_DISALLOW"
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            content_type = response.headers.get("content-type", "")
            data = response.read(2_000_000)
    except urllib.error.HTTPError as exc:
        return "", "", f"HTTP_{exc.code}"
    except urllib.error.URLError as exc:
        return "", "", f"URL_ERROR_{type(exc.reason).__name__}"
    except Exception as exc:
        return "", "", f"FETCH_ERROR_{type(exc).__name__}"
    if "pdf" in content_type.lower() or url.lower().endswith(".pdf"):
        return "", content_type, "PDF_METADATA_ONLY"
    encoding = "utf-8"
    match = re.search(r"charset=([^;\s]+)", content_type, re.I)
    if match:
        encoding = match.group(1)
    try:
        return data.decode(encoding, errors="replace"), content_type, "OK"
    except LookupError:
        return data.decode("utf-8", errors="replace"), content_type, "OK"


def parse_date(text: str) -> dt.date | None:
    for pattern in DATE_PATTERNS:
        match = pattern.search(text)
        if not match:
            continue
        try:
            return dt.date(int(match.group("year")), int(match.group("month")), int(match.group("day")))
        except ValueError:
            return None
    return None


def title_from_block(lines: list[str], source_name: str) -> str:
    skip = {
        source_name,
        "home",
        "report",
        "reports",
        "レポート",
        "レポート一覧",
        "検索",
        "検索条件",
    }
    for line in lines:
        cleaned = line.strip(" -　")
        if not cleaned or cleaned.lower() in skip:
            continue
        if parse_date(cleaned) and len(cleaned) <= 12:
            continue
        if len(cleaned) > 160:
            continue
        return cleaned
    return source_name


def items_from_text(source: dict, page_title: str, text: str, start: dt.date, end: dt.date, limit: int, snippet_limit: int) -> list[dict]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    records: list[dict] = []
    for idx, line in enumerate(lines):
        found = parse_date(line)
        if not found or found < start or found > end:
            continue
        block: list[str] = [line]
        for next_line in lines[idx + 1: idx + 12]:
            if parse_date(next_line):
                break
            block.append(next_line)
        title = title_from_block(block[1:] or block, source["name"])
        snippet = " / ".join(block)
        if len(snippet) > snippet_limit:
            snippet = snippet[: snippet_limit - 3].rstrip() + "..."
        records.append({
            "source_id": source["id"],
            "source": source["name"],
            "layer": source_layer(source),
            "source_class": source["source_class"],
            "importance": source.get("importance", source.get("priority", "")),
            "kafka_use": source.get("kafka_use", []),
            "region": source["region"],
            "asset_linkage": source["asset_linkage"],
            "language": source["language"],
            "priority": source["priority"],
            "expected_cadence": source["expected_cadence"],
            "title": title,
            "published_date": found.isoformat(),
            "author": "",
            "category": source["source_class"],
            "url": source["url"],
            "snippet": snippet,
            "body_status": "list_metadata",
            "page_title": page_title,
        })
        if len(records) >= limit:
            break
    return records


def fallback_item(source: dict, page_title: str, status: str, week_end: dt.date, text: str, snippet_limit: int) -> dict:
    snippet = text[:snippet_limit].strip() if text else status
    if len(snippet) > snippet_limit:
        snippet = snippet[: snippet_limit - 3].rstrip() + "..."
    return {
        "source_id": source["id"],
        "source": source["name"],
        "layer": source_layer(source),
        "source_class": source["source_class"],
        "importance": source.get("importance", source.get("priority", "")),
        "kafka_use": source.get("kafka_use", []),
        "region": source["region"],
        "asset_linkage": source["asset_linkage"],
        "language": source["language"],
        "priority": source["priority"],
        "expected_cadence": source["expected_cadence"],
        "title": page_title or source["name"],
        "published_date": week_end.isoformat(),
        "author": "",
        "category": source["source_class"],
        "url": source["url"],
        "snippet": snippet or "本文未取得",
        "body_status": "metadata_only" if status != "OK" else "no_in_range_date_found",
        "fetch_status": status,
        "page_title": page_title,
    }


def collect_source(source: dict, start: dt.date, end: dt.date, week_end: dt.date, limit: int, snippet_limit: int) -> list[dict]:
    raw, _content_type, status = fetch(source["url"])
    if status != "OK":
        return [fallback_item(source, source["name"], status, week_end, "", snippet_limit)]
    parser = TextHTMLParser()
    parser.feed(raw)
    text = parser.text()
    records = items_from_text(source, parser.title, text, start, end, limit, snippet_limit)
    if records:
        return records
    return [fallback_item(source, parser.title, "OK", week_end, text, snippet_limit)]


def dedupe(items: list[dict]) -> list[dict]:
    seen: set[tuple[str, str, str]] = set()
    out: list[dict] = []
    for item in items:
        key = (item["source_id"], item["published_date"], item["title"])
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def write_jsonl(path: Path, items: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for item in items:
            handle.write(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n")


def write_markdown(path: Path, items: list[dict], start: dt.date, end: dt.date) -> None:
    by_layer: dict[str, list[dict]] = {}
    for item in items:
        by_layer.setdefault(item["layer"], []).append(item)
    lines = [
        f"# Weekly Power & Macro Intelligence Collection {end.isoformat()}",
        "",
        f"- period: {start.isoformat()} to {end.isoformat()}",
        f"- items: {len(items)}",
        "- note: 本文未取得またはmetadata_onlyの項目は一覧ページ上のメタデータだけを使用。",
        "",
    ]
    layers = [
        "L0_market_price",
        "L1_central_bank",
        "L2_state_policy",
        "L3_frontier_ai_lab",
        "L4_ai_power_ideology",
        "L5_analyst_interpretation",
        "L6_personal_macro_narrative",
    ]
    for layer in layers:
        group = by_layer.get(layer, [])
        if not group:
            continue
        lines.extend([f"## {layer}", ""])
        for item in group:
            links = ", ".join(item.get("asset_linkage") or [])
            uses = ", ".join(item.get("kafka_use") or [])
            lines.extend([
                f"### {item['title']}",
                f"- source: {item['source']}",
                f"- source_class: {item['source_class']}",
                f"- date: {item['published_date']}",
                f"- url: {item['url']}",
                f"- region: {item['region']}",
                f"- asset_linkage: {links}",
                f"- kafka_use: {uses}",
                f"- body_status: {item.get('body_status', '')}",
                f"- snippet: {item.get('snippet', '')}",
                "",
            ])
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def read_jsonl(path: Path) -> list[dict]:
    out: list[dict] = []
    if not path.exists():
        return out
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(item, dict):
                out.append(item)
    return out


def gate_quality() -> int:
    args = parse_gate_args()
    items = read_jsonl(Path(args.output_root) / args.week_end / "items.jsonl")
    total = len(items)
    if total == 0:
        print("quality_gate=fail reason=no_items")
        return 1
    url_rate = sum(1 for item in items if str(item.get("url", "")).startswith(("http://", "https://"))) / total
    date_rate = sum(1 for item in items if parse_date(str(item.get("published_date", "")))) / total
    non_metadata_rate = sum(1 for item in items if item.get("body_status") != "metadata_only") / total
    layers = {str(item.get("layer", "")) for item in items if item.get("layer")}
    metrics = {
        "items": total,
        "url_rate": round(url_rate, 3),
        "date_rate": round(date_rate, 3),
        "non_metadata_rate": round(non_metadata_rate, 3),
        "layers": sorted(layers),
    }
    failures = []
    if total < args.min_items:
        failures.append("items")
    if url_rate < args.min_url_rate:
        failures.append("url_rate")
    if date_rate < args.min_date_rate:
        failures.append("date_rate")
    if non_metadata_rate < args.min_non_metadata_rate:
        failures.append("non_metadata_rate")
    if len(layers) < args.min_layers:
        failures.append("layers")
    print(json.dumps({"quality_gate": "fail" if failures else "pass", "failures": failures, **metrics}, ensure_ascii=False))
    return 1 if failures else 0


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "gate":
        return gate_quality()
    args = parse_args()
    week_end = date_arg(args.week_end)
    start = date_arg(args.start) if args.start else week_end - dt.timedelta(days=6)
    end = date_arg(args.end) if args.end else week_end
    out_dir = Path(args.output_root) / week_end.isoformat()
    out_dir.mkdir(parents=True, exist_ok=True)

    items: list[dict] = []
    for source in load_sources():
        items.extend(collect_source(source, start, end, week_end, args.max_source_items, args.max_snippet_chars))
    items = dedupe(items)
    items.sort(key=lambda item: (item["published_date"], item["source"], item["title"]), reverse=True)

    write_jsonl(out_dir / "items.jsonl", items)
    write_markdown(out_dir / "collection.md", items, start, end)
    print(json.dumps({
        "week_end": week_end.isoformat(),
        "start": start.isoformat(),
        "end": end.isoformat(),
        "items": len(items),
        "output_dir": str(out_dir),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
