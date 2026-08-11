#!/usr/bin/env python3
"""Deterministic lexical retrieval over canonical KAFKA SIGNAL component metadata.

The current component manifest has capability text but does not yet contain the
quality scorecard/provenance fields requested by Issue #28. This command never
invents those values: requested filters fail closed when metadata is absent.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
COMPONENTS_MANIFEST = ROOT / "components.manifest.json"
SYSTEM_MANIFEST = ROOT / "manifest.json"

# Query vocabulary only. These aliases improve Japanese/English recall without
# changing canonical component facts or manufacturing quality scores.
ALIASES: dict[str, tuple[str, ...]] = {
    "検索": ("search", "filter"),
    "絞り込み": ("filter", "scope"),
    "比較": ("comparison", "selected", "changed", "previous", "current"),
    "履歴": ("history", "previous", "current", "changed"),
    "差分": ("diff", "changed", "previous", "current"),
    "証拠": ("evidence", "source", "status", "correction"),
    "出典": ("source", "evidence"),
    "更新日時": ("data-as-of", "source"),
    "状態": ("status", "state", "semantic"),
    "空": ("empty", "missing"),
    "エラー": ("error", "missing", "next"),
    "タイムライン": ("timeline", "ordered", "stage"),
    "時系列": ("timeline", "ordered", "history"),
    "アクセシビリティ": ("accessibility", "semantic", "non-color"),
    "a11y": ("accessibility", "semantic", "non-color"),
    "evidence": ("source", "status", "correction"),
    "comparison": ("selected", "scope", "changed"),
    "history": ("previous", "current", "changed"),
    "empty": ("missing", "next"),
    "timeline": ("ordered", "stage"),
}


def _tokens(value: str) -> set[str]:
    return {
        token
        for token in re.split(r"[^0-9a-zA-Z_\-]+", value.casefold())
        if token
    }


def _query_terms(query: str) -> set[str]:
    terms = _tokens(query)
    lowered = query.casefold()
    for alias, expansions in ALIASES.items():
        if alias.casefold() in lowered:
            terms.update(expansions)
    return terms


def _source_commit(root: Path = ROOT) -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    value = result.stdout.strip()
    return value or None


def load_index(root: Path = ROOT) -> dict[str, Any]:
    components_path = root / "components.manifest.json"
    system_path = root / "manifest.json"
    components_payload = json.loads(components_path.read_text(encoding="utf-8"))
    system_payload = json.loads(system_path.read_text(encoding="utf-8"))

    components = components_payload.get("components")
    if not isinstance(components, dict):
        raise ValueError("components.manifest.json: components must be an object")

    canonical_repository = system_payload.get("canonical_repository")
    canonical_path = system_payload.get("canonical_path")
    if not isinstance(canonical_repository, str) or not canonical_repository:
        raise ValueError("manifest.json: canonical_repository is required")
    if not isinstance(canonical_path, str) or not canonical_path:
        raise ValueError("manifest.json: canonical_path is required")

    records: list[dict[str, Any]] = []
    for component_id, raw_capabilities in sorted(components.items()):
        if not isinstance(component_id, str) or not component_id:
            raise ValueError("component id must be a non-empty string")
        if not isinstance(raw_capabilities, list) or not all(
            isinstance(item, str) and item for item in raw_capabilities
        ):
            raise ValueError(f"{component_id}: capabilities must be non-empty strings")
        records.append(
            {
                "component_id": component_id,
                "canonical": True,
                "capabilities": raw_capabilities,
                # These fields intentionally remain unknown until the upstream
                # scorecard/component provenance provides measured values.
                "grade": None,
                "frameworks": None,
                "responsive": None,
                "accessibility": None,
                "known_limitations": None,
                "source": {
                    "repository": canonical_repository,
                    "path": f"{canonical_path}/components.manifest.json",
                    "commit": _source_commit(root),
                    "manifest_version": components_payload.get("version"),
                },
            }
        )

    return {
        "schema_version": "kafka-signal-retrieval.v1",
        "records": records,
        "measurement_boundary": {
            "grade": "not_instrumented",
            "frameworks": "not_instrumented",
            "responsive": "not_instrumented",
            "accessibility": "not_instrumented",
            "original_source_provenance": "not_instrumented",
        },
    }


def _text_terms(record: dict[str, Any]) -> set[str]:
    terms = _tokens(record["component_id"])
    terms.update(_tokens(record["component_id"].replace("_", " ")))
    for capability in record["capabilities"]:
        terms.update(_tokens(capability))
    return terms


def _requested_filter_matches(value: Any, requested: str | None) -> bool:
    if requested is None:
        return True
    if value is None:
        return False
    if isinstance(value, list):
        return requested.casefold() in {str(item).casefold() for item in value}
    if isinstance(value, bool):
        normalized = requested.casefold()
        if normalized not in {"true", "false"}:
            return False
        return value is (normalized == "true")
    return str(value).casefold() == requested.casefold()


def search(
    index: dict[str, Any],
    query: str,
    *,
    grade: str | None = None,
    framework: str | None = None,
    responsive: str | None = None,
    accessibility: str | None = None,
    canonical_only: bool = True,
    limit: int = 5,
) -> dict[str, Any]:
    query_terms = _query_terms(query)
    ranked: list[dict[str, Any]] = []

    for record in index["records"]:
        if canonical_only and record.get("canonical") is not True:
            continue
        if not _requested_filter_matches(record.get("grade"), grade):
            continue
        if not _requested_filter_matches(record.get("frameworks"), framework):
            continue
        if not _requested_filter_matches(record.get("responsive"), responsive):
            continue
        if not _requested_filter_matches(
            record.get("accessibility"), accessibility
        ):
            continue

        record_terms = _text_terms(record)
        overlap = sorted(query_terms & record_terms)
        normalized_id = record["component_id"].casefold()
        exact_id = query.strip().casefold() == normalized_id
        substring_id = query.strip().casefold() in normalized_id and bool(query.strip())
        score = (100 if exact_id else 0) + (30 if substring_id else 0) + 10 * len(overlap)
        if score <= 0:
            continue
        reasons: list[str] = []
        if exact_id:
            reasons.append("exact component id")
        elif substring_id:
            reasons.append("component id substring")
        if overlap:
            reasons.append("matched terms: " + ", ".join(overlap))
        ranked.append({**record, "score": score, "reasons": reasons})

    ranked.sort(key=lambda item: (-item["score"], item["component_id"].casefold()))
    return {
        "schema_version": "kafka-signal-retrieval-result.v1",
        "query": query,
        "filters": {
            "grade": grade,
            "framework": framework,
            "responsive": responsive,
            "accessibility": accessibility,
            "canonical_only": canonical_only,
        },
        "results": ranked[: max(limit, 0)],
        "measurement_boundary": index["measurement_boundary"],
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="purpose/capability query (Japanese or English)")
    parser.add_argument("--grade")
    parser.add_argument("--framework")
    parser.add_argument("--responsive", choices=("true", "false"))
    parser.add_argument("--accessibility", choices=("true", "false"))
    parser.add_argument("--include-noncanonical", action="store_true")
    parser.add_argument("--limit", type=int, default=5)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    options = _parser().parse_args(argv)
    result = search(
        load_index(),
        options.query,
        grade=options.grade,
        framework=options.framework,
        responsive=options.responsive,
        accessibility=options.accessibility,
        canonical_only=not options.include_noncanonical,
        limit=options.limit,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
