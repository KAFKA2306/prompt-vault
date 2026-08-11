#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API = "https://api.github.com"
OWNER = "KAFKA2306"
API_VERSION = "2026-03-10"
BUSINESS_PREFIXES = ("docs/business/", "docs/services/")


def gh_get(path: str, token: str | None = None):
    req = urllib.request.Request(f"{API}{path}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", API_VERSION)
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)


def list_owner_repositories(owner: str, token: str | None = None) -> list[dict]:
    repositories: list[dict] = []
    page = 1
    while True:
        batch = gh_get(
            f"/users/{owner}/repos?per_page=100&page={page}&type=owner&sort=full_name",
            token,
        )
        if not batch:
            break
        repositories.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return repositories


def list_business_declarations(repo: dict, token: str | None = None) -> list[dict]:
    owner, name = repo["full_name"].split("/", 1)
    ref = urllib.parse.quote(repo.get("default_branch") or "main", safe="")
    tree = gh_get(f"/repos/{owner}/{name}/git/trees/{ref}?recursive=1", token)
    if tree.get("truncated"):
        return []
    declarations = []
    for entry in tree.get("tree", []):
        path = entry.get("path")
        if entry.get("type") != "blob" or not isinstance(path, str):
            continue
        if path.endswith(".md") and path.startswith(BUSINESS_PREFIXES):
            declarations.append(
                {
                    "path": path,
                    "blob_sha": entry.get("sha"),
                    "url": f"https://github.com/{repo['full_name']}/blob/{repo.get('default_branch') or 'main'}/{path}",
                    "kind": "repository_owned_business_declaration",
                }
            )
    return sorted(declarations, key=lambda item: item["path"])


def unknown_metric(reason: str) -> dict:
    return {"value": None, "status": "not_instrumented", "reason": reason}


def aggregate(repo: dict, declarations: list[dict], generated_at: datetime) -> dict:
    source_reason = (
        "No repository-owned machine-readable transaction source is connected. "
        "A business/service document is evidence of a declared offer, not evidence of orders, revenue, customers, or conversion."
    )
    metrics = {
        "orders": unknown_metric(source_reason),
        "paid_orders": unknown_metric(source_reason),
        "gross_revenue": unknown_metric(source_reason),
        "refunds": unknown_metric(source_reason),
        "net_revenue": unknown_metric(source_reason),
        "new_paying_customers": unknown_metric(source_reason),
        "conversion_events": unknown_metric(source_reason),
        "qualified_leads": unknown_metric(source_reason),
    }
    return {
        "schema_version": "kafka.results.business.v1",
        "repository": repo["full_name"],
        "data_as_of": generated_at.isoformat(),
        "inventory": {
            "status": "declared_business_surface_detected" if declarations else "no_declared_business_surface_detected",
            "declarations": declarations,
            "classification_limit": "Only repository-owned docs/business/*.md and docs/services/*.md are inventoried; README prose, prices, stars, downloads, and issue text are not interpreted as sales evidence.",
        },
        "metrics": metrics,
        "periods": {
            "7d": {"status": "not_instrumented", "metrics": None},
            "30d": {"status": "not_instrumented", "metrics": None},
            "monthly": {"status": "not_instrumented", "metrics": None},
        },
        "measurement_contract": {
            "actual_and_estimate_separated": True,
            "revenue_and_profit_separated": True,
            "gross_net_fee_tax_separated": True,
            "unobserved_business_metric_is_zero": False,
            "private_transaction_detail_published": False,
            "free_usage_or_downloads_counted_as_revenue": False,
            "currency": None,
            "currency_status": "not_applicable_until_transaction_evidence_exists",
        },
        "provenance": {
            "source_system": "GitHub REST API",
            "api_version": API_VERSION,
            "repository_url": repo.get("html_url"),
            "repository_id": repo.get("id"),
            "repository_node_id": repo.get("node_id"),
            "default_branch": repo.get("default_branch"),
            "source_commit": repo.get("default_branch"),
            "tree_endpoint": f"/repos/{repo['full_name']}/git/trees/{repo.get('default_branch') or 'main'}?recursive=1",
        },
    }


def collect_owner(owner: str, out_dir: Path, token: str | None = None) -> list[Path]:
    now = datetime.now(timezone.utc).replace(microsecond=0)
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for repo in list_owner_repositories(owner, token):
        if repo.get("archived") or repo.get("private"):
            continue
        declarations = list_business_declarations(repo, token)
        report = aggregate(repo, declarations, now)
        path = out_dir / f"{repo['name']}.json"
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        written.append(path)
    return written


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--owner", default=OWNER)
    parser.add_argument("--out", default="results/business")
    args = parser.parse_args()
    written = collect_owner(args.owner, Path(args.out), os.getenv("GITHUB_TOKEN"))
    print(json.dumps({"repositories": len(written), "output": args.out}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
