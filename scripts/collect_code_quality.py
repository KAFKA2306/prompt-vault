#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from pathlib import Path

API = "https://api.github.com"
OWNER = "KAFKA2306"
QUALITY_HINTS = ("quality", "lint", "type", "test", "smoke", "validate", "check")
MAX_WORKERS = 8


def gh_get(path: str, token: str | None = None):
    req = urllib.request.Request(f"{API}{path}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2026-03-10")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)


def list_owner_repositories(owner: str, token: str | None = None) -> list[dict]:
    repositories: list[dict] = []
    page = 1
    while True:
        batch = gh_get(f"/users/{owner}/repos?per_page=100&type=owner&sort=full_name&page={page}", token)
        repositories.extend(batch)
        if len(batch) < 100:
            return repositories
        page += 1


def list_repository_runs(owner: str, repo: str, since: datetime, token: str | None = None) -> list[dict]:
    runs: list[dict] = []
    created = urllib.parse.quote(f">={since.strftime('%Y-%m-%dT%H:%M:%SZ')}")
    page = 1
    while True:
        payload = gh_get(
            f"/repos/{owner}/{repo}/actions/runs?per_page=100&page={page}&created={created}",
            token,
        )
        batch = payload.get("workflow_runs", [])
        runs.extend(batch)
        if len(batch) < 100:
            return runs
        page += 1


def is_quality_run(run: dict) -> bool:
    text = f"{run.get('name', '')} {run.get('path', '')}".lower()
    return any(hint in text for hint in QUALITY_HINTS)


def summarize_window(runs: list[dict], start: datetime, end: datetime) -> dict:
    scoped = []
    for run in runs:
        created = run.get("created_at")
        if not created:
            continue
        ts = datetime.fromisoformat(created.replace("Z", "+00:00"))
        if start <= ts < end and is_quality_run(run):
            scoped.append(run)

    first_attempt = [r for r in scoped if int(r.get("run_attempt") or 1) == 1]
    rejected = [r for r in first_attempt if r.get("conclusion") in {"failure", "timed_out", "action_required"}]
    successful = [r for r in first_attempt if r.get("conclusion") == "success"]
    cancelled = [r for r in first_attempt if r.get("conclusion") == "cancelled"]
    return {
        "quality_gate_runs": len(first_attempt),
        "quality_gate_success": len(successful),
        "regression_gate_rejections": len(rejected),
        "cancelled": len(cancelled),
        "success_rate": None if not first_attempt else len(successful) / len(first_attempt),
        "provenance": [
            {
                "run_id": r.get("id"),
                "run_url": r.get("html_url"),
                "workflow_name": r.get("name"),
                "head_sha": r.get("head_sha"),
                "event": r.get("event"),
                "status": r.get("status"),
                "conclusion": r.get("conclusion"),
                "run_attempt": r.get("run_attempt"),
                "created_at": r.get("created_at"),
            }
            for r in scoped
        ],
    }


def unknown_metric(reason: str = "not_instrumented") -> dict:
    return {"value": None, "status": reason}


def aggregate(repo: str, runs: list[dict], generated_at: datetime) -> dict:
    current_start = generated_at - timedelta(days=30)
    baseline_start = generated_at - timedelta(days=60)
    baseline = summarize_window(runs, baseline_start, current_start)
    current = summarize_window(runs, current_start, generated_at)
    return {
        "schema_version": "kafka.results.code-quality.v1",
        "repository": repo,
        "window": {
            "baseline": {"days": 30, "start": baseline_start.isoformat(), "end": current_start.isoformat()},
            "current": {"days": 30, "start": current_start.isoformat(), "end": generated_at.isoformat()},
            "generated_at": generated_at.isoformat(),
        },
        "quality_gates": {
            "baseline": baseline,
            "current": current,
            "delta": {
                "regression_gate_rejections": current["regression_gate_rejections"] - baseline["regression_gate_rejections"],
                "quality_gate_runs": current["quality_gate_runs"] - baseline["quality_gate_runs"],
            },
            "definition": "Observed first-attempt GitHub Actions runs whose workflow name/path is quality-oriented. A failed gate is not counted as a product bug without separate reproduction evidence.",
        },
        "tool_metrics": {
            "lint_errors": unknown_metric(),
            "lint_warnings": unknown_metric(),
            "type_errors": unknown_metric(),
            "failing_tests": unknown_metric(),
            "flaky_tests": unknown_metric(),
            "dead_code": unknown_metric(),
            "duplicates": unknown_metric(),
            "complexity": unknown_metric(),
        },
        "bugs": {
            "reproducible_bugs_fixed": unknown_metric("requires_repo_owned_reproduction_evidence"),
            "regressions_prevented": unknown_metric("requires_repo_owned_regression_evidence"),
        },
        "evidence_boundary": {
            "gate_failure_is_bug": False,
            "unknown_is_zero": False,
            "note": "Workflow outcomes are observable evidence of gate acceptance/rejection only. Tool violation counts remain unknown until a repository emits machine-readable native tool output.",
        },
    }


def collect_owner(owner: str, out_dir: Path, token: str | None = None) -> list[Path]:
    now = datetime.now(timezone.utc).replace(microsecond=0)
    since = now - timedelta(days=60)
    repos = [repo for repo in list_owner_repositories(owner, token) if not repo.get("archived")]
    out_dir.mkdir(parents=True, exist_ok=True)

    reports: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(list_repository_runs, owner, repo["name"], since, token): repo["name"]
            for repo in repos
        }
        for future in as_completed(futures):
            name = futures[future]
            runs = future.result()
            reports[name] = aggregate(f"{owner}/{name}", runs, now)

    written: list[Path] = []
    for name in sorted(reports):
        path = out_dir / f"{name}.json"
        path.write_text(json.dumps(reports[name], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        written.append(path)
    return written


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--owner", default=OWNER)
    parser.add_argument("--out", default="results/code-quality")
    args = parser.parse_args()
    written = collect_owner(args.owner, Path(args.out), os.getenv("GITHUB_TOKEN"))
    print(json.dumps({"repositories": len(written), "output": args.out}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
