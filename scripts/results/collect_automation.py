#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import urllib.parse
import urllib.request
import time
import socket
import urllib.error
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

API = "https://api.github.com"
OWNER = "KAFKA2306"
MANUAL_EVENTS = {"workflow_dispatch", "repository_dispatch"}
TRANSIENT_HTTP = {429, 502, 503, 504}


def gh_get(path: str, token: str | None = None):
    req = urllib.request.Request(f"{API}{path}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2026-03-10")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            if exc.code not in TRANSIENT_HTTP or attempt == 4:
                raise
        except (TimeoutError, socket.timeout, urllib.error.URLError) as exc:
            if isinstance(exc, urllib.error.URLError) and not isinstance(exc.reason, (TimeoutError, socket.timeout)):
                raise
            if attempt == 4:
                raise
        time.sleep(min(2 ** attempt, 16))


def aggregate(repo: str, runs: list[dict], since: datetime, generated_at: datetime) -> dict:
    events = Counter((r.get("event") or "unknown") for r in runs)
    conclusions = Counter((r.get("conclusion") or r.get("status") or "unknown") for r in runs)
    scheduled = [r for r in runs if r.get("event") == "schedule"]
    manual = [r for r in runs if r.get("event") in MANUAL_EVENTS]
    automated = [r for r in runs if r.get("event") not in MANUAL_EVENTS]
    failed_automated = [r for r in automated if r.get("conclusion") in {"failure", "timed_out", "cancelled"}]

    provenance = [
        {
            "run_id": r["id"],
            "run_url": r["html_url"],
            "workflow_id": r.get("workflow_id"),
            "head_sha": r.get("head_sha"),
            "event": r.get("event"),
            "status": r.get("status"),
            "conclusion": r.get("conclusion"),
            "run_attempt": r.get("run_attempt"),
            "created_at": r.get("created_at"),
        }
        for r in runs
    ]

    return {
        "schema_version": "kafka.results.automation.v1",
        "repository": repo,
        "window": {"days": 30, "since": since.isoformat(), "generated_at": generated_at.isoformat()},
        "runs": {
            "total": len(runs),
            "automated_trigger_runs": len(automated),
            "manual_trigger_runs": len(manual),
            "scheduled_runs": len(scheduled),
            "by_event": dict(sorted(events.items())),
            "by_conclusion": dict(sorted(conclusions.items())),
        },
        "manual_start_actions_avoided": {
            "observed": len(scheduled),
            "definition": "One avoided human start action per GitHub Actions run whose recorded event is schedule.",
            "scope_limit": "Does not estimate downstream human work, elapsed time saved, or whether a person would otherwise have run the job.",
        },
        "manual_interventions": {
            "value": None,
            "status": "not_instrumented",
            "manual_dispatch_runs": len(manual),
            "note": "A manual dispatch is an observed manual start, not proof of intervention or recovery; intervention count is therefore not inferred.",
        },
        "failed_automation_requiring_manual_recovery": {
            "value": None,
            "status": "not_computable_from_workflow_runs_alone",
            "failed_or_cancelled_automated_runs": len(failed_automated),
            "note": "Failure is observable, but subsequent human recovery is not encoded in the workflow-run record.",
        },
        "generated_artifacts_without_manual_editing": {"value": None, "status": "not_instrumented"},
        "hours_saved": {"value": None, "status": "unknown", "reason": "No measured before/after elapsed-time evidence."},
        "before_after_contract": {
            "measured_unit": "workflow start action",
            "before": "manual initiation would be required for an equivalent unscheduled run",
            "after": "schedule event initiated the recorded run",
            "counted_only_when": "GitHub reports event=schedule",
        },
        "provenance": provenance,
    }


def collect_owner(owner: str, out_dir: Path, token: str | None = None) -> list[Path]:
    now = datetime.now(timezone.utc).replace(microsecond=0)
    since = now - timedelta(days=30)
    repos = []
    page = 1
    while True:
        batch = gh_get(f"/users/{owner}/repos?per_page=50&type=owner&sort=full_name&page={page}", token)
        repos.extend(batch)
        if len(batch) < 50:
            break
        page += 1
    written: list[Path] = []
    out_dir.mkdir(parents=True, exist_ok=True)
    created = urllib.parse.quote(f">={since.strftime('%Y-%m-%dT%H:%M:%SZ')}")
    for repo in repos:
        if repo.get("archived"):
            continue
        name = repo["name"]
        runs = []
        page = 1
        while True:
            payload = gh_get(f"/repos/{owner}/{name}/actions/runs?per_page=50&page={page}&created={created}", token)
            batch = payload.get("workflow_runs", [])
            runs.extend(batch)
            if len(batch) < 50:
                break
            page += 1
        report = aggregate(f"{owner}/{name}", runs, since, now)
        path = out_dir / f"{name}.json"
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        written.append(path)
    return written


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--owner", default=OWNER)
    parser.add_argument("--out", default="results/automation")
    args = parser.parse_args()
    written = collect_owner(args.owner, Path(args.out), os.getenv("GITHUB_TOKEN"))
    print(json.dumps({"repositories": len(written), "output": args.out}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
