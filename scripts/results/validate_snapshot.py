#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

SCHEMAS = {
    "code-quality": "kafka.results.code-quality.v1",
    "data-quality": "kafka.results.data-quality.v1",
    "reliability": "kafka.results.reliability.v1",
    "automation": "kafka.results.automation.v1",
    "adoption": "kafka.results.adoption.v1",
    "business": "kafka.results.business.v1",
}


def load_reports(root: Path, category: str) -> list[dict]:
    files = sorted((root / category).glob("*.json"))
    if not files:
        raise AssertionError(f"no {category} reports generated")
    reports = [json.loads(path.read_text(encoding="utf-8")) for path in files]
    expected = SCHEMAS[category]
    for report in reports:
        assert report["schema_version"] == expected
        assert isinstance(report.get("repository"), str) and "/" in report["repository"]
    return reports


def validate_code_quality(root: Path, reports: list[dict]) -> None:
    for data in reports:
        assert data["window"]["baseline"]["days"] == 30
        assert data["window"]["current"]["days"] == 30
        assert data["evidence_boundary"]["gate_failure_is_bug"] is False
        assert data["evidence_boundary"]["unknown_is_zero"] is False
        assert data["ratchet"]["status"] in {"WORSENED", "UNCHANGED", "IMPROVED"}
        assert data["ratchet"]["worsened"] is (data["ratchet"]["delta"] > 0)
        assert data["ratchet"]["before"] == data["quality_gates"]["baseline"]["regression_gate_rejections"]
        assert data["ratchet"]["after"] == data["quality_gates"]["current"]["regression_gate_rejections"]
        assert data["measurement"]["tool"] == "github-actions-workflow-runs-rest-api"
        assert data["measurement"]["tool_version"] == "2026-03-10"
        for metric in data["tool_metrics"].values():
            if metric["status"] == "measured":
                assert isinstance(metric["value"], int) and metric["value"] >= 0
                assert metric["source_commit"] and metric["run_url"]
                assert metric["tool"] and metric["tool_version"] and metric["scope"]
            else:
                assert metric["value"] is None
        for window in ("baseline", "current"):
            for provenance in data["quality_gates"][window]["provenance"]:
                assert provenance["run_url"] and provenance["head_sha"] and provenance["run_attempt"]

    prompt = json.loads((root / "code-quality" / "prompt-vault.json").read_text(encoding="utf-8"))
    failing = prompt["tool_metrics"]["failing_tests"]
    assert failing["status"] == "measured"
    assert failing["value"] == failing["failures"] + failing["errors"] == 0
    assert failing["tool"] == "python-unittest"
    assert failing["tests_run"] > 0


def validate_data_quality(_: Path, reports: list[dict]) -> None:
    measured = []
    for data in reports:
        if data["instrumentation"]["status"] == "measured":
            measured.append(data)
            assert data["canonical_population"]["value"] is not None
            assert data["provenance"]["source_commit"]
            assert data["provenance"]["evidence"]
            for key in ("source_hash_coverage", "rejection_reason_coverage"):
                metric = data["metrics"][key]
                assert "numerator" in metric and "denominator" in metric
        else:
            assert data["canonical_population"]["value"] is None
    assert any(data["repository"] == "KAFKA2306/semiconductor-earnings-model" for data in measured)


def validate_reliability(_: Path, reports: list[dict]) -> None:
    for data in reports:
        assert data["window"]["days"] == 30
        assert set(data["runs"]) >= {"total", "success", "failure", "cancelled"}
        for workflow in data["workflows"]:
            assert workflow["state"] == "active"
            for provenance in workflow["provenance"]:
                assert provenance["run_url"] and provenance["head_sha"] and provenance["run_attempt"]


def validate_automation(_: Path, reports: list[dict]) -> None:
    for data in reports:
        assert data["window"]["days"] == 30
        assert data["runs"]["scheduled_runs"] == data["manual_start_actions_avoided"]["observed"]
        assert data["manual_interventions"]["value"] is None
        assert data["hours_saved"]["value"] is None
        for provenance in data["provenance"]:
            assert provenance["run_url"] and provenance["head_sha"] and provenance["run_attempt"]


def validate_adoption(_: Path, reports: list[dict]) -> None:
    for data in reports:
        contract = data["measurement_contract"]
        assert contract["real_usage_and_proxy_separated"] is True
        assert contract["unobserved_usage_is_zero"] is False
        for metric in data["observed_usage"].values():
            assert metric["value"] is None
            assert metric["status"] == "not_instrumented"
        for key in ("github_stars", "github_forks"):
            metric = data["proxy_metrics"][key]
            assert metric["kind"] == "proxy"
            assert metric["not_equivalent_to"] == "users_or_usage"
        assert data["periods"]["7d"]["status"] == "not_instrumented"
        assert data["periods"]["30d"]["status"] == "not_instrumented"
        assert data["provenance"]["source_system"] == "GitHub REST API"
        assert data["provenance"]["repository_url"]


def validate_business(_: Path, reports: list[dict]) -> None:
    for data in reports:
        contract = data["measurement_contract"]
        assert contract["actual_and_estimate_separated"] is True
        assert contract["revenue_and_profit_separated"] is True
        assert contract["gross_net_fee_tax_separated"] is True
        assert contract["unobserved_business_metric_is_zero"] is False
        assert contract["private_transaction_detail_published"] is False
        assert contract["free_usage_or_downloads_counted_as_revenue"] is False
        for metric in data["metrics"].values():
            assert metric["value"] is None
            assert metric["status"] == "not_instrumented"
        for period in ("7d", "30d", "monthly"):
            assert data["periods"][period]["status"] == "not_instrumented"
        for declaration in data["inventory"]["declarations"]:
            assert declaration["path"].startswith(("docs/business/", "docs/services/"))
            assert declaration["blob_sha"]
            assert declaration["url"].startswith("https://github.com/")
        assert data["provenance"]["source_system"] == "GitHub REST API"
        assert data["provenance"]["repository_url"]


VALIDATORS = {
    "code-quality": validate_code_quality,
    "data-quality": validate_data_quality,
    "reliability": validate_reliability,
    "automation": validate_automation,
    "adoption": validate_adoption,
    "business": validate_business,
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("category", choices=SCHEMAS)
    parser.add_argument("--root", type=Path, default=Path("results"))
    args = parser.parse_args()
    reports = load_reports(args.root, args.category)
    VALIDATORS[args.category](args.root, reports)
    print(f"validated {len(reports)} {args.category} reports")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
