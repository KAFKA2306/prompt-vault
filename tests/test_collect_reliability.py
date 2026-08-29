import importlib.util
import unittest
from datetime import datetime, timezone
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("collect_reliability", Path("scripts/results/collect_reliability.py"))
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class ReliabilityCollectorTests(unittest.TestCase):
    def test_aggregate_keeps_cancelled_separate_and_preserves_retries(self):
        workflows = [
            {"id": 1, "name": "CI", "path": ".github/workflows/ci.yml", "state": "active"},
            {"id": 2, "name": "Pages deploy", "path": ".github/workflows/pages.yml", "state": "active"},
        ]
        runs = [
            {"id": 10, "workflow_id": 1, "html_url": "https://example/10", "head_sha": "a", "event": "push", "status": "completed", "conclusion": "failure", "run_attempt": 1, "created_at": "2026-08-01T00:00:00Z"},
            {"id": 11, "workflow_id": 1, "html_url": "https://example/11", "head_sha": "a", "event": "push", "status": "completed", "conclusion": "success", "run_attempt": 2, "created_at": "2026-08-01T00:05:00Z"},
            {"id": 12, "workflow_id": 2, "html_url": "https://example/12", "head_sha": "b", "event": "push", "status": "completed", "conclusion": "cancelled", "run_attempt": 1, "created_at": "2026-08-02T00:00:00Z"},
        ]
        now = datetime(2026, 8, 12, tzinfo=timezone.utc)
        report = mod.aggregate("KAFKA2306/example", workflows, runs, now, now)
        self.assertEqual(report["runs"]["failure"], 1)
        self.assertEqual(report["runs"]["cancelled"], 1)
        self.assertEqual(report["runs"]["success"], 1)
        self.assertEqual(report["first_attempt_success_rate"], 0)
        self.assertEqual(report["retry_success_rate"], 1)
        self.assertEqual(report["workflows"][1]["measurement_class"], "deploy")
        self.assertEqual(report["post_deploy_verification"]["status"], "not_instrumented")
        self.assertEqual(report["workflows"][0]["provenance"][0]["run_url"], "https://example/10")

    def test_unknown_conclusion_is_retained_raw(self):
        workflows = [{"id": 1, "name": "CI", "path": "ci.yml", "state": "active"}]
        runs = [{"id": 1, "workflow_id": 1, "html_url": "u", "head_sha": "h", "event": "push", "status": "completed", "conclusion": "neutral", "run_attempt": 1, "created_at": "x"}]
        now = datetime(2026, 8, 12, tzinfo=timezone.utc)
        report = mod.aggregate("r", workflows, runs, now, now)
        self.assertEqual(report["workflows"][0]["other_raw_statuses"], {"neutral": 1})


if __name__ == "__main__":
    unittest.main()
