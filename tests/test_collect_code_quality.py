import unittest
from datetime import datetime, timezone

from scripts.collect_code_quality import aggregate, is_quality_run, ratchet_status


class CodeQualityCollectorTests(unittest.TestCase):
    def test_quality_classifier(self):
        self.assertTrue(is_quality_run({"name": "Quality", "path": ".github/workflows/quality.yml"}))
        self.assertTrue(is_quality_run({"name": "Smoke", "path": ".github/workflows/smoke.yml"}))
        self.assertFalse(is_quality_run({"name": "Deploy Pages", "path": ".github/workflows/pages.yml"}))

    def test_ratchet_status(self):
        self.assertEqual(ratchet_status(2), "WORSENED")
        self.assertEqual(ratchet_status(0), "UNCHANGED")
        self.assertEqual(ratchet_status(-1), "IMPROVED")

    def test_baseline_current_and_unknown_semantics(self):
        now = datetime(2026, 8, 12, tzinfo=timezone.utc)
        runs = [
            {
                "id": 1,
                "html_url": "https://github.com/example/r/actions/runs/1",
                "name": "Quality",
                "path": ".github/workflows/quality.yml",
                "head_sha": "a" * 40,
                "event": "pull_request",
                "status": "completed",
                "conclusion": "failure",
                "run_attempt": 1,
                "created_at": "2026-07-01T00:00:00Z",
            },
            {
                "id": 2,
                "html_url": "https://github.com/example/r/actions/runs/2",
                "name": "Quality",
                "path": ".github/workflows/quality.yml",
                "head_sha": "b" * 40,
                "event": "pull_request",
                "status": "completed",
                "conclusion": "success",
                "run_attempt": 1,
                "created_at": "2026-07-20T00:00:00Z",
            },
            {
                "id": 3,
                "html_url": "https://github.com/example/r/actions/runs/3",
                "name": "Smoke",
                "path": ".github/workflows/smoke.yml",
                "head_sha": "c" * 40,
                "event": "pull_request",
                "status": "completed",
                "conclusion": "failure",
                "run_attempt": 1,
                "created_at": "2026-08-10T00:00:00Z",
            },
            {
                "id": 4,
                "html_url": "https://github.com/example/r/actions/runs/4",
                "name": "Smoke",
                "path": ".github/workflows/smoke.yml",
                "head_sha": "c" * 40,
                "event": "pull_request",
                "status": "completed",
                "conclusion": "success",
                "run_attempt": 2,
                "created_at": "2026-08-10T00:05:00Z",
            },
            {
                "id": 5,
                "html_url": "https://github.com/example/r/actions/runs/5",
                "name": "Deploy Pages",
                "path": ".github/workflows/pages.yml",
                "head_sha": "d" * 40,
                "event": "push",
                "status": "completed",
                "conclusion": "failure",
                "run_attempt": 1,
                "created_at": "2026-08-11T00:00:00Z",
            },
        ]
        report = aggregate("example/r", runs, now)
        self.assertEqual(report["quality_gates"]["baseline"]["regression_gate_rejections"], 1)
        self.assertEqual(report["quality_gates"]["current"]["regression_gate_rejections"], 1)
        self.assertEqual(report["quality_gates"]["delta"]["regression_gate_rejections"], 0)
        self.assertEqual(report["quality_gates"]["current"]["quality_gate_runs"], 2)
        self.assertEqual(report["quality_gates"]["current"]["quality_gate_success"], 1)
        self.assertEqual(report["ratchet"]["before"], 1)
        self.assertEqual(report["ratchet"]["after"], 1)
        self.assertEqual(report["ratchet"]["delta"], 0)
        self.assertEqual(report["ratchet"]["status"], "UNCHANGED")
        self.assertFalse(report["ratchet"]["worsened"])
        self.assertEqual(report["measurement"]["tool"], "github-actions-workflow-runs-rest-api")
        self.assertEqual(report["measurement"]["tool_version"], "2026-03-10")
        self.assertEqual(report["measurement"]["source_commits"], ["c" * 40])
        self.assertEqual(
            report["measurement"]["run_urls"],
            [
                "https://github.com/example/r/actions/runs/3",
                "https://github.com/example/r/actions/runs/4",
            ],
        )
        self.assertIsNone(report["tool_metrics"]["lint_errors"]["value"])
        self.assertEqual(report["tool_metrics"]["lint_errors"]["status"], "not_instrumented")
        self.assertFalse(report["evidence_boundary"]["gate_failure_is_bug"])
        self.assertFalse(report["evidence_boundary"]["unknown_is_zero"])


if __name__ == "__main__":
    unittest.main()
