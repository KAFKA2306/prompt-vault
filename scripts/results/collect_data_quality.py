#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import json
import os
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://api.github.com"
API_VERSION = "2026-03-10"
OWNER = "KAFKA2306"
SEMICONDUCTOR = "semiconductor-earnings-model"
AUDIT_PATHS = {
    "ledger": "data/earnings_ledger/audit_latest.json",
    "evidence": "data/earnings_ledger/evidence_latest.json",
    "lineage": "data/earnings_ledger/lineage_latest.json",
    "duplicates": "data/earnings_ledger/semantic_duplicate_audit_latest.json",
    "rejections": "data/earnings_ledger/rejection_reason_audit_latest.json",
}


def gh_get(path: str, token: str | None = None):
    req = urllib.request.Request(f"{API}{path}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", API_VERSION)
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)


def unknown(reason: str = "not_instrumented") -> dict:
    return {"value": None, "status": reason}


def ratio(numerator: int, denominator: int, definition: str) -> dict:
    return {
        "numerator": numerator,
        "denominator": denominator,
        "ratio": (numerator / denominator) if denominator else None,
        "status": "measured",
        "definition": definition,
    }


def decode_json_file(payload: dict) -> dict:
    if payload.get("encoding") != "base64":
        raise ValueError("GitHub contents response must be base64 encoded")
    return json.loads(base64.b64decode(payload["content"]).decode("utf-8"))


def evidence_ref(repo: str, path: str, payload: dict, source_commit: str) -> dict:
    return {
        "repository": repo,
        "path": path,
        "blob_sha": payload.get("sha"),
        "source_commit": source_commit,
        "url": payload.get("html_url") or f"https://github.com/{repo}/blob/{source_commit}/{path}",
    }


def semiconductor_report(repo: str, default_branch: str, token: str | None) -> dict:
    commit = gh_get(f"/repos/{repo}/commits/{urllib.parse.quote(default_branch, safe='')}", token)
    source_commit = commit["sha"]
    documents: dict[str, dict] = {}
    refs: list[dict] = []
    for key, path in AUDIT_PATHS.items():
        encoded_path = urllib.parse.quote(path, safe="/")
        payload = gh_get(f"/repos/{repo}/contents/{encoded_path}?ref={source_commit}", token)
        documents[key] = decode_json_file(payload)
        refs.append(evidence_ref(repo, path, payload, source_commit))

    ledger = documents["ledger"]
    evidence = documents["evidence"]
    lineage = documents["lineage"]
    duplicates = documents["duplicates"]
    rejections = documents["rejections"]
    lineage_artifacts = lineage.get("artifacts", [])
    hash_numerator = sum(bool(row.get("sha256")) for row in lineage_artifacts)
    rejected = int(rejections.get("rejected_events_total", 0))
    raw_reason_total = sum(int(v) for v in rejections.get("raw_reason_counts", {}).values())

    return {
        "schema_version": "kafka.results.data-quality.v1",
        "repository": repo,
        "instrumentation": {"status": "measured", "adapter": "semiconductor-earnings-ledger-audits.v1"},
        "canonical_population": {
            "name": "accepted earnings ledger events",
            "value": int(ledger["accepted_events_total"]),
            "definition_source": AUDIT_PATHS["ledger"],
        },
        "metrics": {
            "verified_records": {
                "value": int(evidence.get("verified_events", 0)),
                "status": "measured_window_only",
                "window_start": evidence.get("window_start"),
                "window_end": evidence.get("window_end"),
                "note": "This is the repository audit's verification window, not lifetime canonical coverage.",
            },
            "primary_source_backed_records": unknown("not_exposed_as_aggregate_by_registered_audit"),
            "record_provenance_coverage": unknown("not_exposed_as_record_level_aggregate_by_registered_audit"),
            "source_hash_coverage": ratio(
                hash_numerator,
                len(lineage_artifacts),
                "Lineage-manifest artifacts carrying a non-empty sha256 divided by all lineage-manifest artifacts.",
            ),
            "freshness": unknown("not_exposed_as_common_stale_count_by_registered_audit"),
            "null_reason_coverage": unknown("not_exposed_as_common_aggregate_by_registered_audit"),
            "schema_validation_failures": unknown("ledger audit issues are not relabelled as schema failures"),
            "duplicate_records": {"value": int(duplicates.get("duplicate_count", 0)), "status": "measured"},
            "conflict_records": unknown("not_exposed_as_common_aggregate_by_registered_audit"),
            "rejected_records": {"value": rejected, "status": "measured"},
            "rejection_reason_coverage": ratio(
                raw_reason_total,
                rejected,
                "Rejected events represented in raw_reason_counts divided by rejected_events_total.",
            ),
            "broken_evidence_urls": unknown("not_measured_by_registered_local_audits"),
            "verified_added_30d": unknown("historical_snapshot_delta_not_yet_instrumented"),
        },
        "audit_status": {
            "ledger": ledger.get("status"),
            "evidence": evidence.get("status"),
            "lineage": lineage.get("status"),
            "duplicates": duplicates.get("status"),
            "rejections": rejections.get("status"),
        },
        "provenance": {
            "source_commit": source_commit,
            "collector": "github-contents-rest-api",
            "api_version": API_VERSION,
            "evidence": refs,
        },
    }


def uninstrumented_report(repo: str) -> dict:
    return {
        "schema_version": "kafka.results.data-quality.v1",
        "repository": repo,
        "instrumentation": {"status": "not_instrumented", "adapter": None},
        "canonical_population": {"name": None, "value": None, "status": "not_defined"},
        "metrics": {
            key: unknown()
            for key in (
                "verified_records",
                "primary_source_backed_records",
                "record_provenance_coverage",
                "source_hash_coverage",
                "freshness",
                "null_reason_coverage",
                "schema_validation_failures",
                "duplicate_records",
                "conflict_records",
                "rejected_records",
                "rejection_reason_coverage",
                "broken_evidence_urls",
                "verified_added_30d",
            )
        },
        "provenance": {"source_commit": None, "evidence": []},
    }


def list_repositories(owner: str, token: str | None = None) -> list[dict]:
    repos: list[dict] = []
    page = 1
    while True:
        batch = gh_get(
            f"/users/{owner}/repos?per_page=100&page={page}&type=owner&sort=full_name",
            token,
        )
        repos.extend(batch)
        if len(batch) < 100:
            return repos
        page += 1


def collect_owner(owner: str, out_dir: Path, token: str | None = None) -> list[Path]:
    repos = list_repositories(owner, token)
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for item in repos:
        if item.get("archived"):
            continue
        name = item["name"]
        repo = f"{owner}/{name}"
        if name == SEMICONDUCTOR:
            report = semiconductor_report(repo, item.get("default_branch") or "main", token)
        else:
            report = uninstrumented_report(repo)
        path = out_dir / f"{name}.json"
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        written.append(path)
    return written


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--owner", default=OWNER)
    parser.add_argument("--out", default="results/data-quality")
    args = parser.parse_args()
    written = collect_owner(args.owner, Path(args.out), os.getenv("GITHUB_TOKEN"))
    print(json.dumps({"repositories": len(written), "output": args.out}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
