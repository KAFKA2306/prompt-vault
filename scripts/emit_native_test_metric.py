#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import platform
import unittest
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = "kafka.results.native-tool-metric.v1"


def run_suite(start_dir: str, pattern: str) -> unittest.TestResult:
    # top_level_dir keeps the repository root importable even when this file is
    # executed as `python scripts/emit_native_test_metric.py`.
    suite = unittest.defaultTestLoader.discover(
        start_dir=start_dir,
        pattern=pattern,
        top_level_dir=".",
    )
    return unittest.TextTestRunner(verbosity=2).run(suite)


def build_evidence(
    result: unittest.TestResult,
    repository: str,
    source_commit: str,
    run_url: str,
    scope: str,
) -> dict:
    failures = len(result.failures) + len(result.errors)
    return {
        "schema_version": SCHEMA_VERSION,
        "repository": repository,
        "scope": scope,
        "captured_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "source_commit": source_commit,
        "run_url": run_url,
        "tool": "python-unittest",
        "tool_version": platform.python_version(),
        "metrics": {
            "failing_tests": {
                "value": failures,
                "status": "measured",
                "tests_run": result.testsRun,
                "failures": len(result.failures),
                "errors": len(result.errors),
                "skipped": len(result.skipped),
            }
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-dir", default="tests")
    parser.add_argument("--pattern", default="test_collect_code_quality.py")
    parser.add_argument("--repository", default=os.getenv("GITHUB_REPOSITORY", "KAFKA2306/prompt-vault"))
    parser.add_argument("--source-commit", default=os.getenv("GITHUB_SHA", ""))
    parser.add_argument("--run-url", default="")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    run_url = args.run_url or (
        f"{os.getenv('GITHUB_SERVER_URL', 'https://github.com')}/{args.repository}/actions/runs/{os.getenv('GITHUB_RUN_ID', '')}"
    )
    if not args.source_commit or len(args.source_commit) != 40:
        raise SystemExit("source commit must be a 40-character Git SHA")
    if not run_url.rstrip("/").split("/")[-1]:
        raise SystemExit("run URL must include a run id")

    result = run_suite(args.start_dir, args.pattern)
    evidence = build_evidence(
        result,
        repository=args.repository,
        source_commit=args.source_commit,
        run_url=run_url,
        scope=f"unittest discover -s {args.start_dir} -p {args.pattern}",
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"tests_run": result.testsRun, "failing_tests": evidence["metrics"]["failing_tests"]["value"]}))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
