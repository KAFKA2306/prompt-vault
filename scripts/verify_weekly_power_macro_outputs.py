#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path


OUTPUT_ROOT = Path("outputs/weekly-power-macro-intelligence")
DOCS_ROOT = Path("docs/reports/weekly-power-macro-intelligence")

DATE_PATTERNS = [
    re.compile(r"(?P<year>20\d{2})[./-](?P<month>\d{1,2})[./-](?P<day>\d{1,2})"),
    re.compile(r"(?P<year>20\d{2})年\s*(?P<month>\d{1,2})月\s*(?P<day>\d{1,2})日"),
]

MONTHS = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}

EN_DATE_PATTERNS = [
    re.compile(r"(?P<month_name>[A-Z][a-z]+)\.?\s+(?P<day>\d{1,2}),\s*(?P<year>20\d{2})"),
    re.compile(r"(?P<day>\d{1,2})\s+(?P<month_name>[A-Z][a-z]+)\.?\s+(?P<year>20\d{2})"),
]

FORBIDDEN = re.compile(
    r"本文未取得|未確認|取得失敗|Fetch Failures|Source Coverage|"
    r"HTTP_[0-9]+|FETCH_ERROR|URL_ERROR|ROBOTS_DISALLOW|"
    r"no_in_range_date_found|metadata_only"
)

REQUIRED_GROUPS = {
    "factset": lambda source_id: source_id.startswith("factset"),
    "spglobal": lambda source_id: source_id.startswith("spglobal"),
    "yardeni": lambda source_id: source_id.startswith("yardeni"),
}

REQUIRED_METRIC_TAGS = {
    "company_earnings",
    "index_earnings",
    "revenue",
    "index_level",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--week-end", required=True)
    parser.add_argument("--output-root", default=str(OUTPUT_ROOT))
    parser.add_argument("--docs-root", default=str(DOCS_ROOT))
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def date_arg(value: str) -> dt.date:
    return dt.date.fromisoformat(value)


def parse_dates(text: str) -> list[dt.date]:
    dates: list[dt.date] = []
    for pattern in DATE_PATTERNS:
        for match in pattern.finditer(text):
            try:
                dates.append(dt.date(int(match.group("year")), int(match.group("month")), int(match.group("day"))))
            except ValueError:
                pass
    for pattern in EN_DATE_PATTERNS:
        for match in pattern.finditer(text):
            month = MONTHS.get(match.group("month_name").lower())
            if not month:
                continue
            try:
                dates.append(dt.date(int(match.group("year")), month, int(match.group("day"))))
            except ValueError:
                pass
    return dates


def read_jsonl(path: Path) -> list[dict]:
    items: list[dict] = []
    if not path.exists():
        return items
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
                items.append(item)
    return items


def verify(week_end: dt.date, output_root: Path, docs_root: Path) -> dict:
    out_dir = output_root / week_end.isoformat()
    report_path = out_dir / "report.md"
    docs_path = docs_root / f"{week_end.isoformat()}.md"
    items = read_jsonl(out_dir / "items.jsonl")
    report = report_path.read_text(encoding="utf-8") if report_path.exists() else ""
    docs = docs_path.read_text(encoding="utf-8") if docs_path.exists() else ""
    current_items = [item for item in items if item.get("is_current_evidence")]
    source_ids = {str(item.get("source_id", "")) for item in current_items}
    metric_tags = {
        str(tag)
        for item in current_items
        for tag in (item.get("metric_tags") or [])
    }

    failures: list[str] = []
    future_item_dates = [
        item
        for item in current_items
        if item.get("published_date") and date_arg(str(item["published_date"])) > week_end
    ]
    future_report_dates = sorted({date.isoformat() for date in parse_dates(report) if date > week_end})
    forbidden_matches = sorted(set(FORBIDDEN.findall(report + "\n" + docs)))
    group_presence = {name: any(check(source_id) for source_id in source_ids) for name, check in REQUIRED_GROUPS.items()}
    missing_groups = sorted(name for name, present in group_presence.items() if not present)
    missing_metric_tags = sorted(REQUIRED_METRIC_TAGS - metric_tags)

    if not report_path.exists():
        failures.append("missing_report")
    if not docs_path.exists():
        failures.append("missing_docs_report")
    if future_item_dates:
        failures.append("future_item_dates")
    if future_report_dates:
        failures.append("future_report_dates")
    if forbidden_matches:
        failures.append("forbidden_text")
    if missing_groups:
        failures.append("missing_required_source_groups:" + ",".join(missing_groups))
    if missing_metric_tags:
        failures.append("missing_required_metric_tags:" + ",".join(missing_metric_tags))

    return {
        "week_end": week_end.isoformat(),
        "status": "fail" if failures else "pass",
        "failures": failures,
        "current_evidence_items": len(current_items),
        "required_source_groups": group_presence,
        "metric_tags": sorted(metric_tags),
        "future_report_dates": future_report_dates,
        "future_item_dates": [
            {
                "source_id": item.get("source_id"),
                "title": item.get("title"),
                "published_date": item.get("published_date"),
            }
            for item in future_item_dates[:20]
        ],
        "forbidden_matches": forbidden_matches,
    }


def main() -> int:
    args = parse_args()
    result = verify(date_arg(args.week_end), Path(args.output_root), Path(args.docs_root))
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 1 if result["status"] != "pass" else 0


if __name__ == "__main__":
    raise SystemExit(main())
