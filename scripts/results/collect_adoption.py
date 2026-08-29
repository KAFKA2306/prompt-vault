#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API = "https://api.github.com"
OWNER = "KAFKA2306"
API_VERSION = "2026-03-10"


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


def normalize_homepage(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    value = value.strip()
    return value or None


def aggregate(repo: dict, generated_at: datetime) -> dict:
    homepage = normalize_homepage(repo.get("homepage"))
    has_pages = bool(repo.get("has_pages"))
    public_surface_detected = bool(homepage or has_pages)

    surfaces: list[dict] = []
    if homepage:
        surfaces.append(
            {
                "kind": "repository_homepage",
                "url": homepage,
                "source": "GitHub repository metadata.homepage",
            }
        )
    if has_pages:
        surfaces.append(
            {
                "kind": "github_pages",
                "url": None,
                "url_status": "not_resolved_from_repository_metadata",
                "source": "GitHub repository metadata.has_pages",
            }
        )

    observed_usage = {
        "page_views": {"value": None, "status": "not_instrumented"},
        "unique_visitors": {"value": None, "status": "not_instrumented"},
        "api_requests": {"value": None, "status": "not_instrumented"},
        "successful_api_requests": {"value": None, "status": "not_instrumented"},
        "mcp_calls": {"value": None, "status": "not_instrumented"},
        "returning_users": {"value": None, "status": "not_instrumented"},
        "task_completion_events": {"value": None, "status": "not_instrumented"},
    }

    return {
        "schema_version": "kafka.results.adoption.v1",
        "repository": repo["full_name"],
        "data_as_of": generated_at.isoformat(),
        "service_inventory": {
            "status": "public_surface_detected" if public_surface_detected else "no_public_surface_detected",
            "public": not bool(repo.get("private")),
            "archived": bool(repo.get("archived")),
            "repository_url": repo.get("html_url"),
            "surfaces": surfaces,
            "classification_limit": "Repository metadata can identify a declared homepage or Pages deployment, but does not prove external usage or discover every API/MCP endpoint.",
        },
        "observed_usage": observed_usage,
        "periods": {
            "7d": {"status": "not_instrumented", "observed_usage": None},
            "30d": {"status": "not_instrumented", "observed_usage": None},
        },
        "proxy_metrics": {
            "github_stars": {
                "value": int(repo.get("stargazers_count") or 0),
                "kind": "proxy",
                "not_equivalent_to": "users_or_usage",
            },
            "github_forks": {
                "value": int(repo.get("forks_count") or 0),
                "kind": "proxy",
                "not_equivalent_to": "users_or_usage",
            },
            "clones": {
                "value": None,
                "status": "not_collected",
                "reason": "Repository-list metadata does not contain clone traffic and cross-repository traffic access is not assumed.",
            },
            "downloads": {
                "value": None,
                "status": "not_collected",
                "reason": "Release/download semantics are product-specific and are not inferred from repository metadata.",
            },
        },
        "measurement_contract": {
            "real_usage_and_proxy_separated": True,
            "unobserved_usage_is_zero": False,
            "privacy": "No private analytics, user identifiers, IP addresses, or browser histories are collected by this collector.",
            "bot_crawler_limit": "No page-view metric is emitted; therefore bot/crawler filtering is not falsely claimed.",
        },
        "provenance": {
            "source_system": "GitHub REST API",
            "endpoint": f"/users/{repo['owner']['login']}/repos",
            "api_version": API_VERSION,
            "repository_node_id": repo.get("node_id"),
            "repository_id": repo.get("id"),
            "repository_url": repo.get("html_url"),
            "updated_at": repo.get("updated_at"),
            "pushed_at": repo.get("pushed_at"),
        },
    }


def collect_owner(owner: str, out_dir: Path, token: str | None = None) -> list[Path]:
    now = datetime.now(timezone.utc).replace(microsecond=0)
    repos = list_owner_repositories(owner, token)
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for repo in repos:
        if repo.get("archived") or repo.get("private"):
            continue
        report = aggregate(repo, now)
        path = out_dir / f"{repo['name']}.json"
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        written.append(path)
    return written


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--owner", default=OWNER)
    parser.add_argument("--out", default="results/adoption")
    args = parser.parse_args()
    written = collect_owner(args.owner, Path(args.out), os.getenv("GITHUB_TOKEN"))
    print(json.dumps({"repositories": len(written), "output": args.out}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
