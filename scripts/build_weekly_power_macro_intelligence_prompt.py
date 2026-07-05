#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path


OUTPUT_ROOT = Path("outputs/weekly-power-macro-intelligence")

MONTHS = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--week-end", default=dt.date.today().isoformat())
    parser.add_argument("--output-root", default=str(OUTPUT_ROOT))
    parser.add_argument("--max-items", type=int, default=120)
    parser.add_argument("--prompt-file")
    return parser.parse_args()


def read_items(path: Path, max_items: int) -> list[dict]:
    items: list[dict] = []
    if not path.exists():
        return items
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if len(items) >= max_items:
                break
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


def current_evidence(items: list[dict]) -> list[dict]:
    return [item for item in items if item.get("is_current_evidence")]


def source_coverage(items: list[dict]) -> list[dict]:
    return [item for item in items if not item.get("is_current_evidence")]


def compact_items(items: list[dict]) -> str:
    def prompt_field(name: str, value: object) -> str:
        text = str(value or "")
        return f"  {name}: {text}" if text else f"  {name}:"

    blocks: list[str] = []
    for item in items:
        links = ", ".join(item.get("asset_linkage") or [])
        metric_tags = ", ".join(item.get("metric_tags") or [])
        blocks.append(
            "- "
            f"title: {item.get('title', '')}\n"
            f"{prompt_field('source', item.get('source', ''))}\n"
            f"{prompt_field('layer', item.get('layer', ''))}\n"
            f"{prompt_field('source_class', item.get('source_class', ''))}\n"
            f"{prompt_field('importance', item.get('importance', ''))}\n"
            f"{prompt_field('region', item.get('region', ''))}\n"
            f"{prompt_field('asset_linkage', links)}\n"
            f"{prompt_field('metric_tags', metric_tags)}\n"
            f"{prompt_field('kafka_use', ', '.join(item.get('kafka_use') or []))}\n"
            f"{prompt_field('published_date', item.get('published_date', ''))}\n"
            f"{prompt_field('author', item.get('author', ''))}\n"
            f"{prompt_field('url', item.get('url', ''))}\n"
            f"{prompt_field('body_status', item.get('body_status', ''))}\n"
            f"{prompt_field('evidence_level', item.get('evidence_level', ''))}\n"
            f"{prompt_field('is_current_evidence', item.get('is_current_evidence', False))}\n"
            f"{prompt_field('snippet', item.get('snippet', ''))}"
        )
    return "\n".join(blocks)


def redact_future_dates(text: str, week_end: dt.date) -> str:
    def redact_iso(match: re.Match[str]) -> str:
        try:
            found = dt.date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        except ValueError:
            return match.group(0)
        return "[future date redacted]" if found > week_end else match.group(0)

    def redact_jp(match: re.Match[str]) -> str:
        try:
            found = dt.date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        except ValueError:
            return match.group(0)
        return "[future date redacted]" if found > week_end else match.group(0)

    def redact_en(match: re.Match[str]) -> str:
        month = MONTHS.get(match.group(1))
        if not month:
            return match.group(0)
        try:
            found = dt.date(int(match.group(3)), month, int(match.group(2)))
        except ValueError:
            return match.group(0)
        return "[future date redacted]" if found > week_end else match.group(0)

    text = re.sub(r"(20\d{2})[-/](\d{1,2})[-/](\d{1,2})", redact_iso, text)
    text = re.sub(r"(20\d{2})年\s*(\d{1,2})月\s*(\d{1,2})日", redact_jp, text)
    text = re.sub(r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),\s+(20\d{2})", redact_en, text)
    return text


def compact_current_items(items: list[dict], week_end: dt.date) -> str:
    sanitized: list[dict] = []
    for item in items:
        out = dict(item)
        for key in ("title", "snippet"):
            out[key] = redact_future_dates(str(out.get(key, "")), week_end)
        sanitized.append(out)
    return compact_items(sanitized)


def compact_coverage(items: list[dict]) -> str:
    blocks: list[str] = []
    for item in items:
        blocks.append(
            "- "
            f"source: {item.get('source', '')}\n"
            f"  layer: {item.get('layer', '')}\n"
            f"  source_class: {item.get('source_class', '')}\n"
            f"  url: {item.get('url', '')}\n"
            f"  body_status: {item.get('body_status', '')}\n"
            f"  evidence_level: {item.get('evidence_level', '')}\n"
            f"  fetch_status: {item.get('fetch_status', '')}\n"
            f"  observed_date: {item.get('observed_date', '')}\n"
            f"  note: not usable as current-week factual evidence"
        )
    return "\n".join(blocks)


def build_prompt(week_end: str, items: list[dict], _collection: str) -> str:
    week_end_date = dt.date.fromisoformat(week_end)
    evidence_items = current_evidence(items)
    return f"""# Objective
あなたはKAFKA向けの権力中枢・マクロ・AIテーマ意思決定OSです。
以下の収集結果を使い、単なる要約ではなく、金利、国家政策、AI産業、AI権力思想、資本配分、研究テーマ、発信テーマの前提がどう変わったかを判定してください。

# Week End
{week_end}

# Non-Negotiable Rules
- URLの無い事実主張は禁止。根拠URLが無い内容は書かない。
- 固有名詞、モデル名、製品名、事件、数値、日付、レポート名は、Current Evidence Items の title または snippet に文字列として存在するものだけ使う。
- Current Evidence Items に存在しない具体名を補完・推測・創作してはいけない。
- Source Coverage / Fetch Failures は監視状況の記録であり、事実主張、レジーム判定、投資仮説、行動リストの根拠に使ってはいけない。
- body_status が list_metadata 以外、または is_current_evidence が false の項目から本文内容を推測しない。
- 公式ページのカテゴリ名やランディングページ文言を、今週の新規発表として扱ってはいけない。
- 日銀、Fed、政府、関税、AI企業、AI思想の各節で Current Evidence Items が無い場合は、本文を作文せず「今週の適格根拠なし」と1行で止める。
- 「本文未取得」「未確認」「取得失敗」を列挙してレポート本文を水増ししてはいけない。
- Source Coverage / Fetch Failures / 取得失敗一覧の節を出力してはいけない。
- L1-L4は「世界を動かす側」、L5は「世界を読む側」、L6は「市場参加者の物語化・ナラティブ検出」として扱う。
- 公式マクロ、中央銀行、国家政策、AI基幹企業、AI権力思想、企業業績、市場期待、個人公開マクロ解説を必ず分類する。
- 個人公開マクロ解説は公式レポートと同格扱いしない。
- FactSetをfactsetsと誤記しない。
- FedWatchはCME FedWatchと表記する。
- YardeniはYardeni Researchと表記する。
- 売買推奨ではなく、監視条件・反証条件・行動候補として書く。
- 十分な根拠がない節は「今週の適格根拠なし」とだけ書き、空想で埋めない。
- FactSet / S&P Global / Yardeni Research の company_earnings, index_earnings, revenue, index_level は米株スイングと重要ソースに必ず反映する。
- S&P Global XLSが古い場合は、data_as_ofを明示し、現在値ではなく公式基準値として扱う。
- Week End より後の日付、イベント、予定、数値を本文に書いてはいけない。Current Evidence Items 内の [future date redacted] は無視する。

# Source Hierarchy
- L0: 市場価格、CME FedWatch、決算
- L1: 中央銀行、Fed、日銀
- L2: 国家政策、日本政府、米国政権、USTR、Commerce、Treasury、METI、MOF
- L3: AI基幹企業、OpenAI、Anthropic、NVIDIA、Microsoft、Amazon、Google
- L4: AI権力者の思想・政策文書、Sam Altman、Dario Amodei
- L5: アナリスト解釈、Yardeni Research、FactSet、第一ライフ研、日本総研、NRI、みずほ、大和総研
- L6: 個人マクロ・ナラティブ、Shenmacro、人文科学アカデミー

# KAFKA Themes
- 米株スイング
- 日経/日本株
- SoftBank Group / NAV
- AI・半導体・電力・データセンター
- 製造業・素材・設備投資
- 金利、為替、流動性
- ブログ、note、YouTube、Scrapboxへの発信材料

# Required Output
# Weekly Power & Macro Intelligence - {week_end}

## 0. 今週の支配的レジーム
- 中央銀行:
- 財政・政府:
- 関税・地政学:
- AI産業:
- AI統治思想:

## 1. 日銀/Fed: 割引率と為替
- 日銀の変化:
- Fedの変化:
- CME FedWatchとの乖離:
- 円金利・ドル円・日本株への示唆:

## 2. 日本政府/トランプ政権: 国家政策ショック
- 日本の財政・産業政策:
- JGB需給:
- AI・半導体政策:
- 米国関税・輸出管理:
- 日本企業への波及:

## 3. OpenAI/Anthropic: AI産業カーブ
- モデル/製品の進化:
- enterprise adoption:
- AI safety / regulation:
- compute需要:
- SBG NAV / AI株への示唆:

## 4. Altman/Dario: AI権力思想
- 今週の思想的変化:
- 国家との距離:
- 規制への姿勢:
- 民主化/集中/安全保障の論点:
- 投資テーマへの意味:

## 5. 投資仮説の更新
- 米株スイング:
- 日経/日本株:
- SBG NAV:
- AI半導体:
- 製造業・素材:
- 為替・金利:

## 6. 反証リスト
- 既存仮説と矛盾した情報:
- 重み:
- 対応:

## 7. 来週の行動
- 売買:
- 調査:
- 発信:

## 8. 重要ソースTop 10
各項目は title / source / layer / source_class / published_date / url / KAFKAにとっての意味 / 投資・研究・記事化のどれに使えるか、で書く。

## 9. コンテンツ化候補
ブログ、note、YouTube、Scrapboxに使える論点を、タイトル案 / 根拠URL / 切り口 / 想定読者 / 1段落要旨で出す。

## 10. Market Metrics Coverage
FactSet / S&P Global / Yardeni Research から、企業利益、指数利益、収益、指数水準を箇条書きで確認する。

# Current Evidence Items
{compact_current_items(evidence_items, week_end_date)}
"""


def main() -> int:
    args = parse_args()
    out_dir = Path(args.output_root) / args.week_end
    items = read_items(out_dir / "items.jsonl", args.max_items)
    collection_path = out_dir / "collection.md"
    collection = collection_path.read_text(encoding="utf-8") if collection_path.exists() else ""
    prompt = build_prompt(args.week_end, items, collection)
    prompt_path = Path(args.prompt_file) if args.prompt_file else out_dir / "prompt.md"
    prompt_path.write_text(prompt, encoding="utf-8")
    print(prompt_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
