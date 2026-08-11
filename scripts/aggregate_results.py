#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "kafka.results.aggregate.v1"
CATEGORIES = {
    "code-quality": "kafka.results.code-quality.v1",
    "data-quality": "kafka.results.data-quality.v1",
    "reliability": "kafka.results.reliability.v1",
    "automation": "kafka.results.automation.v1",
    "adoption": "kafka.results.adoption.v1",
    "business": "kafka.results.business.v1",
}
PERIODS = ("today", "7d", "30d", "all-time")


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def result_id(category: str, repository: str, schema_version: str) -> str:
    raw = f"{category}\0{repository}\0{schema_version}".encode()
    return f"result:{hashlib.sha256(raw).hexdigest()}"


def _walk(value: Any, key: str = ""):
    if isinstance(value, dict):
        for child_key, child in value.items():
            yield from _walk(child, child_key)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child, key)
    else:
        yield key, value


def evidence_urls(payload: dict) -> list[str]:
    urls = set()
    for key, value in _walk(payload):
        lowered = key.lower()
        is_url_field = lowered == "url" or lowered.endswith("_url") or lowered.endswith("_urls")
        if not is_url_field or value is None:
            continue
        if isinstance(value, str):
            if not value.startswith(("https://", "http://")):
                raise ValueError(f"invalid evidence URL in {key}: {value!r}")
            urls.add(value)
    return sorted(urls)


def source_timestamp(payload: dict) -> str | None:
    candidates: list[str] = []
    for key, value in _walk(payload):
        if key in {"generated_at", "data_as_of", "observed_at", "retrieved_at"} and isinstance(value, str):
            try:
                datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                continue
            candidates.append(value)
    return max(candidates) if candidates else None


def trend(payload: dict) -> str:
    status = str(payload.get("ratchet", {}).get("status", "")).upper()
    if status in {"IMPROVED", "WORSENED", "UNCHANGED"}:
        return status
    return "UNKNOWN"


def period_status(payload: dict, period: str) -> str:
    periods = payload.get("periods")
    if isinstance(periods, dict) and period in periods:
        item = periods[period]
        if isinstance(item, dict):
            return str(item.get("status") or "observed")
        return "observed"
    window = payload.get("window")
    if period == "30d" and isinstance(window, dict):
        if window.get("days") == 30:
            return "observed"
        current = window.get("current")
        if isinstance(current, dict) and current.get("days") == 30:
            return "observed"
    return "not_available"


def _metric(value: Any, *, status: str, definition: str) -> dict:
    return {"value": value, "status": status, "definition": definition}


def summary_kpis(rows: list[dict]) -> dict:
    reliability = [r for r in rows if r["category"] == "reliability"]
    automation = [r for r in rows if r["category"] == "automation"]
    data_quality = [r for r in rows if r["category"] == "data-quality"]
    code_quality = [r for r in rows if r["category"] == "code-quality"]
    adoption = [r for r in rows if r["category"] == "adoption"]
    business = [r for r in rows if r["category"] == "business"]

    first_total = first_success = 0
    for row in reliability:
        for wf in row["payload"].get("workflows", []):
            first = wf.get("first_attempt", {})
            first_total += int(first.get("total") or 0)
            first_success += int(first.get("success") or 0)
    first_rate = None if first_total == 0 else first_success / first_total

    scheduled = 0
    for row in automation:
        observed = row["payload"].get("manual_start_actions_avoided", {}).get("observed")
        if isinstance(observed, int):
            scheduled += observed

    verified_added_values = []
    for row in data_quality:
        metric = row["payload"].get("metrics", {}).get("verified_added_30d", {})
        if metric.get("status") == "measured" and isinstance(metric.get("value"), (int, float)):
            verified_added_values.append(metric["value"])

    bugs_fixed = []
    regressions_prevented = []
    for row in code_quality:
        bugs = row["payload"].get("bugs", {})
        for name, target in (("reproducible_bugs_fixed", bugs_fixed), ("regressions_prevented", regressions_prevented)):
            metric = bugs.get(name, {})
            if metric.get("status") == "measured" and isinstance(metric.get("value"), (int, float)):
                target.append(metric["value"])

    def any_measured(rows_: list[dict], key: str) -> list[float]:
        values = []
        for row in rows_:
            metric = row["payload"].get("metrics", {}).get(key, {})
            if metric.get("status") == "measured" and isinstance(metric.get("value"), (int, float)):
                values.append(metric["value"])
        return values

    usage_values = any_measured(adoption, "page_views")
    order_values = any_measured(business, "orders")
    revenue_values = any_measured(business, "net_revenue")

    return {
        "verified_data_added_30d": _metric(sum(verified_added_values) if verified_added_values else None, status="measured" if verified_added_values else "not_instrumented", definition="Sum only repository metrics explicitly marked measured for verified_added_30d."),
        "reproducible_bugs_fixed": _metric(sum(bugs_fixed) if bugs_fixed else None, status="measured" if bugs_fixed else "not_instrumented", definition="Sum only repository-owned bug evidence explicitly marked measured."),
        "regressions_prevented": _metric(sum(regressions_prevented) if regressions_prevented else None, status="measured" if regressions_prevented else "not_instrumented", definition="Sum only repository-owned regression evidence explicitly marked measured."),
        "workflow_first_attempt_success_rate": {"value": first_rate, "status": "measured" if first_total else "not_available", "numerator": first_success, "denominator": first_total, "definition": "Weighted success rate across recorded first-attempt workflow runs."},
        "scheduled_automated_starts": _metric(scheduled, status="measured", definition="Observed GitHub Actions runs whose event is schedule; not an estimate of hours saved."),
        "manual_interventions": _metric(None, status="not_instrumented", definition="Manual dispatch is not proof of manual recovery/intervention."),
        "observed_usage": _metric(sum(usage_values) if usage_values else None, status="measured" if usage_values else "not_instrumented", definition="Only adoption metrics explicitly marked measured; proxy stars/forks are excluded."),
        "orders": _metric(sum(order_values) if order_values else None, status="measured" if order_values else "not_instrumented", definition="Only business order metrics explicitly marked measured."),
        "net_revenue": _metric(sum(revenue_values) if revenue_values else None, status="measured" if revenue_values else "not_instrumented", definition="Only business net revenue explicitly marked measured; no price-times-count inference."),
    }


def load_inputs(root: Path, require_all: bool = False) -> list[dict]:
    rows: list[dict] = []
    seen: dict[str, str] = {}
    for category, expected_schema in CATEGORIES.items():
        files = sorted((root / category).glob("*.json"))
        if require_all and not files:
            raise ValueError(f"missing input category: {category}")
        for path in files:
            payload = json.loads(path.read_text(encoding="utf-8"))
            if payload.get("schema_version") != expected_schema:
                raise ValueError(f"{path}: expected {expected_schema}, got {payload.get('schema_version')!r}")
            repository = payload.get("repository")
            if not isinstance(repository, str) or "/" not in repository:
                raise ValueError(f"{path}: invalid repository")
            rid = result_id(category, repository, expected_schema)
            digest = sha256_json(payload)
            if rid in seen:
                if seen[rid] != digest:
                    raise ValueError(f"conflicting duplicate canonical result id: {rid}")
                continue
            seen[rid] = digest
            rows.append({
                "canonical_result_id": rid,
                "category": category,
                "repository": repository,
                "schema_version": expected_schema,
                "input_sha256": digest,
                "source_path": path.as_posix(),
                "source_timestamp": source_timestamp(payload),
                "trend": trend(payload),
                "evidence_urls": evidence_urls(payload),
                "payload": payload,
            })
    return sorted(rows, key=lambda r: (r["repository"], r["category"]))


def build_result(rows: list[dict]) -> dict:
    timestamps = [r["source_timestamp"] for r in rows if r["source_timestamp"]]
    generated_at = max(timestamps) if timestamps else datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    by_category: dict[str, dict] = {}
    by_repo: dict[str, dict] = {}
    trend_counts = Counter(r["trend"] for r in rows)

    for category in CATEGORIES:
        subset = [r for r in rows if r["category"] == category]
        by_category[category] = {
            "result_count": len(subset),
            "repositories": sorted(r["repository"] for r in subset),
            "trend": dict(Counter(r["trend"] for r in subset)),
        }
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row["repository"]].append(row)
    for repo, subset in sorted(grouped.items()):
        by_repo[repo] = {
            "categories": sorted(r["category"] for r in subset),
            "canonical_result_ids": sorted(r["canonical_result_id"] for r in subset),
            "trend": dict(Counter(r["trend"] for r in subset)),
        }

    period_views = {}
    for period in PERIODS:
        statuses = Counter(period_status(r["payload"], period) for r in rows)
        period_views[period] = {"status_counts": dict(sorted(statuses.items()))}

    product_services = []
    for row in rows:
        if row["category"] != "business":
            continue
        for declaration in row["payload"].get("inventory", {}).get("declarations", []):
            path = declaration.get("path")
            if isinstance(path, str):
                product_services.append({"repository": row["repository"], "declaration_path": path, "canonical_result_id": row["canonical_result_id"]})

    public_rows = [{k: v for k, v in row.items() if k != "payload"} for row in rows]
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at,
        "contract": {
            "unknown_is_zero": False,
            "not_available_is_zero": False,
            "cross_metric_score_created": False,
            "markdown_generated_from_json": True,
            "canonical_result_id_deduplicates_repo_category": True,
        },
        "summary_kpis": summary_kpis(rows),
        "views": {
            "by_category": by_category,
            "by_repository": by_repo,
            "by_product_service": sorted(product_services, key=lambda x: (x["repository"], x["declaration_path"])),
            "by_trend": dict(sorted(trend_counts.items())),
            "by_period": period_views,
        },
        "results": public_rows,
    }


def schema_document() -> dict:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://github.com/KAFKA2306/prompt-vault/blob/main/results/schema.json",
        "title": "KAFKA RESULTS aggregate",
        "type": "object",
        "required": ["schema_version", "generated_at", "contract", "summary_kpis", "views", "results"],
        "properties": {
            "schema_version": {"const": SCHEMA_VERSION},
            "generated_at": {"type": "string"},
            "results": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["canonical_result_id", "category", "repository", "schema_version", "input_sha256", "source_path", "trend", "evidence_urls"],
                },
            },
        },
    }


def render_markdown(result: dict) -> str:
    lines = ["# KAFKA RESULTS", "", f"Generated from machine-readable inputs: `{result['generated_at']}`", "", "## Summary", "", "| KPI | Value | Status |", "|---|---:|---|"]
    for name, metric in result["summary_kpis"].items():
        value = metric.get("value")
        shown = "unknown" if value is None else (f"{value:.2%}" if name.endswith("success_rate") else str(value))
        lines.append(f"| `{name}` | {shown} | {metric.get('status', 'unknown')} |")
    lines += ["", "## Categories", "", "| Category | Results |", "|---|---:|"]
    for category, view in result["views"]["by_category"].items():
        lines.append(f"| {category} | {view['result_count']} |")
    lines += ["", "## Evidence", ""]
    linked = 0
    for row in result["results"]:
        if row["evidence_urls"]:
            lines.append(f"- `{row['repository']}` / `{row['category']}`: {row['evidence_urls'][0]}")
            linked += 1
    if linked == 0:
        lines.append("- No URL evidence was present in the current inputs; source paths and SHA-256 hashes remain recorded in `results.json`.")
    lines += ["", "> Unknown, not-instrumented, and not-available values are never converted to zero. Different metric definitions are not collapsed into a composite score.", ""]
    return "\n".join(lines)


def write_snapshot(result: dict, snapshots: Path) -> Path:
    snapshots.mkdir(parents=True, exist_ok=True)
    day = str(result["generated_at"])[:10]
    if not day or day == "None":
        day = date.today().isoformat()
    base = snapshots / f"{day}.json"
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if not base.exists():
        base.write_text(rendered, encoding="utf-8")
        return base
    if base.read_text(encoding="utf-8") == rendered:
        return base
    revision = 2
    while True:
        candidate = snapshots / f"{day}-r{revision}.json"
        if not candidate.exists():
            candidate.write_text(rendered, encoding="utf-8")
            return candidate
        if candidate.read_text(encoding="utf-8") == rendered:
            return candidate
        revision += 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="results")
    parser.add_argument("--require-all", action="store_true")
    args = parser.parse_args()
    root = Path(args.root)
    rows = load_inputs(root, args.require_all)
    if not rows:
        raise SystemExit("no result inputs found")
    result = build_result(rows)
    root.mkdir(parents=True, exist_ok=True)
    (root / "results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (root / "schema.json").write_text(json.dumps(schema_document(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (root / "RESULTS.md").write_text(render_markdown(result), encoding="utf-8")
    snapshot = write_snapshot(result, root / "snapshots")
    print(json.dumps({"results": len(rows), "repositories": len(result["views"]["by_repository"]), "snapshot": snapshot.as_posix()}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
