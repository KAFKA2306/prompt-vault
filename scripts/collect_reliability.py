#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

API = "https://api.github.com"
OWNER = "KAFKA2306"


def gh_get(path: str, token: str | None = None):
    req = urllib.request.Request(f"{API}{path}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2026-03-10")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)


def classify_workflow(name: str, path: str) -> str:
    text = f"{name} {path}".lower()
    if "pages" in text or "deploy" in text or "publish" in text:
        return "deploy"
    if "live" in text or "smoke" in text:
        return "post_deploy_verification"
    return "ci"


def aggregate(repo: str, workflows: list[dict], runs: list[dict], since: datetime, generated_at: datetime) -> dict:
    active = [w for w in workflows if w.get("state") == "active"]
    active_ids = {w["id"] for w in active}
    scoped = [r for r in runs if r.get("workflow_id") in active_ids]
    by_workflow: dict[int, list[dict]] = defaultdict(list)
    for run in scoped:
        by_workflow[run["workflow_id"]].append(run)

    workflow_rows = []
    repo_counts = Counter()
    first_attempt_total = 0
    first_attempt_success = 0
    retry_total = 0
    retry_success = 0

    for wf in active:
        wf_runs = by_workflow.get(wf["id"], [])
        counts = Counter((r.get("conclusion") or r.get("status") or "unknown") for r in wf_runs)
        first = [r for r in wf_runs if int(r.get("run_attempt") or 1) == 1]
        retries = [r for r in wf_runs if int(r.get("run_attempt") or 1) > 1]
        first_attempt_total += len(first)
        first_attempt_success += sum(r.get("conclusion") == "success" for r in first)
        retry_total += len(retries)
        retry_success += sum(r.get("conclusion") == "success" for r in retries)
        repo_counts.update(counts)
        workflow_rows.append({
            "workflow_id": wf["id"],
            "name": wf["name"],
            "path": wf["path"],
            "state": wf["state"],
            "measurement_class": classify_workflow(wf["name"], wf["path"]),
            "runs_total": len(wf_runs),
            "success": counts["success"],
            "failure": counts["failure"],
            "cancelled": counts["cancelled"],
            "timed_out": counts["timed_out"],
            "skipped": counts["skipped"],
            "other_raw_statuses": {k: v for k, v in sorted(counts.items()) if k not in {"success", "failure", "cancelled", "timed_out", "skipped"}},
            "first_attempt": {
                "total": len(first),
                "success": sum(r.get("conclusion") == "success" for r in first),
            },
            "retry": {
                "total": len(retries),
                "success": sum(r.get("conclusion") == "success" for r in retries),
            },
            "provenance": [
                {
                    "run_id": r["id"],
                    "run_url": r["html_url"],
                    "head_sha": r.get("head_sha"),
                    "event": r.get("event"),
                    "status": r.get("status"),
                    "conclusion": r.get("conclusion"),
                    "run_attempt": r.get("run_attempt"),
                    "created_at": r.get("created_at"),
                }
                for r in wf_runs
            ],
        })

    return {
        "schema_version": "kafka.results.reliability.v1",
        "repository": repo,
        "window": {"days": 30, "since": since.isoformat(), "generated_at": generated_at.isoformat()},
        "active_workflows": len(active),
        "inactive_workflows": len(workflows) - len(active),
        "runs": {
            "total": len(scoped),
            "success": repo_counts["success"],
            "failure": repo_counts["failure"],
            "cancelled": repo_counts["cancelled"],
            "timed_out": repo_counts["timed_out"],
            "skipped": repo_counts["skipped"],
        },
        "first_attempt_success_rate": None if first_attempt_total == 0 else first_attempt_success / first_attempt_total,
        "retry_success_rate": None if retry_total == 0 else retry_success / retry_total,
        "post_deploy_verification": {
            "status": "not_instrumented",
            "note": "Only workflows explicitly classified as live/smoke are counted separately; a successful deploy is never treated as a live verification pass.",
        },
        "scheduled_job_missed_or_stale": "not_computable_from_workflow_runs_alone",
        "artifact_verification_failures": "not_instrumented",
        "residue_cleanup_failures": "not_instrumented",
        "regression_gate_rejections": "not_instrumented",
        "workflows": workflow_rows,
    }


def collect_owner(owner: str, out_dir: Path, token: str | None = None) -> list[Path]:
    now = datetime.now(timezone.utc).replace(microsecond=0)
    since = now - timedelta(days=30)
    repos = gh_get(f"/users/{owner}/repos?per_page=100&type=owner&sort=full_name", token)
    written = []
    out_dir.mkdir(parents=True, exist_ok=True)
    for repo in repos:
        if repo.get("archived"):
            continue
        name = repo["name"]
        workflows_payload = gh_get(f"/repos/{owner}/{name}/actions/workflows?per_page=100", token)
        workflows = workflows_payload.get("workflows", [])
        created = urllib.parse.quote(f">={since.strftime('%Y-%m-%dT%H:%M:%SZ')}")
        runs_payload = gh_get(f"/repos/{owner}/{name}/actions/runs?per_page=100&created={created}", token)
        report = aggregate(f"{owner}/{name}", workflows, runs_payload.get("workflow_runs", []), since, now)
        path = out_dir / f"{name}.json"
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        written.append(path)
    return written


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--owner", default=OWNER)
    parser.add_argument("--out", default="results/reliability")
    args = parser.parse_args()
    written = collect_owner(args.owner, Path(args.out), os.getenv("GITHUB_TOKEN"))
    print(json.dumps({"repositories": len(written), "output": args.out}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
