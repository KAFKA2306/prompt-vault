#!/usr/bin/env python3
"""Adjudicate KAFKA SIGNAL UI scorecards from explicit evidence-backed inputs.

The scorer intentionally does not invent visual/UX scores. Upstream inventory/review
provides eight integer scores and evidence; this script computes the nominal grade,
applies fail-close browser gates, and emits canonical-candidate decisions.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "audit" / "scoring-policy.json"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def nominal_grade(total: int, policy: dict[str, Any]) -> str:
    for threshold in policy["thresholds"]:
        if threshold["min"] <= total <= threshold["max"]:
            return threshold["grade"]
    raise ValueError(f"score total outside policy range: {total}")


def validate_scores(scores: dict[str, Any], policy: dict[str, Any]) -> None:
    expected = set(policy["dimensions"])
    actual = set(scores)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise ValueError(f"score dimensions mismatch; missing={missing}, extra={extra}")
    for name, value in scores.items():
        if type(value) is not int or not 0 <= value <= 5:
            raise ValueError(f"{name} must be an integer from 0 to 5")


def browser_gate(browser: dict[str, Any], policy: dict[str, Any]) -> tuple[bool, list[str]]:
    defects: list[str] = []
    if not browser.get("verified", False):
        return False, ["browser verification missing"]

    required_viewports = set(policy["required_viewports"])
    actual_viewports = set(browser.get("viewports", []))
    missing_viewports = sorted(required_viewports - actual_viewports)
    if missing_viewports:
        defects.append(f"missing required viewports: {missing_viewports}")

    fail_close = policy["fail_close"]
    if browser.get("console_errors") != fail_close["console_errors_must_equal"]:
        defects.append("browser console errors are not zero")
    if browser.get("unexpected_overflow") != fail_close["unexpected_overflow_must_equal"]:
        defects.append("unexpected horizontal overflow detected")
    if browser.get("keyboard_focus_verified") is not fail_close["keyboard_focus_verified_must_equal"]:
        defects.append("keyboard/focus verification failed")

    screenshots = browser.get("screenshots", [])
    if len(screenshots) < 2:
        defects.append("mobile and desktop screenshot evidence required")
    return not defects, defects


def adjudicate(record: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    for key in ("repo", "element", "path", "source_commit", "scores", "evidence"):
        if key not in record:
            raise ValueError(f"missing required field: {key}")
    if len(record["source_commit"]) != 40 or any(c not in "0123456789abcdef" for c in record["source_commit"]):
        raise ValueError("source_commit must be a lowercase 40-character git SHA")

    scores = record["scores"]
    validate_scores(scores, policy)
    total = sum(scores.values())
    raw_grade = nominal_grade(total, policy)

    browser = record.get("evidence", {}).get("browser", {})
    browser_ok, gate_defects = browser_gate(browser, policy)
    requires_browser = raw_grade in policy["browser_verification_required_for"]

    final_grade = raw_grade
    decision_status = "verified" if browser_ok else "provisional"
    canonical_candidate = raw_grade in policy["canonical_candidate_grades"] and browser_ok

    # S/A are promotion grades. Without required browser evidence they must not flow
    # into the harvester; cap the actionable grade at B while retaining nominal_grade.
    if requires_browser and not browser_ok:
        final_grade = "B"

    defects = list(record.get("defects", []))
    for defect in gate_defects:
        if defect not in defects:
            defects.append(defect)

    result = dict(record)
    result.update(
        {
            "total": total,
            "nominal_grade": raw_grade,
            "grade": final_grade,
            "decision_status": decision_status,
            "canonical_candidate": canonical_candidate,
            "canonical_target": record.get("canonical_target") if canonical_candidate else None,
            "defects": defects,
        }
    )
    return result


def score_document(document: Any, policy: dict[str, Any]) -> dict[str, Any]:
    records = document.get("records") if isinstance(document, dict) else document
    if not isinstance(records, list):
        raise ValueError("input must be a list or an object containing records[]")
    scored = [adjudicate(record, policy) for record in records]
    return {
        "version": policy["version"],
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "records": scored,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Adjudicate KAFKA SIGNAL UI scorecards")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--policy", type=Path, default=POLICY_PATH)
    args = parser.parse_args()

    policy = load_json(args.policy)
    output = score_document(load_json(args.input), policy)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"scored {len(output['records'])} UI elements -> {args.output}")


if __name__ == "__main__":
    main()
