import importlib.util
import unittest
from unittest.mock import Mock, patch
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("collect_automation", Path("scripts/results/collect_automation.py"))
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class AutomationCollectorTests(unittest.TestCase):
    def test_gh_get_retries_transient_gateway_error(self):
        response = Mock()
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        response.read = Mock(return_value=b'{"ok": true}')
        error = urllib.error.HTTPError("url", 504, "gateway timeout", {}, None)
        with patch.object(mod.urllib.request, "urlopen", side_effect=[error, response]) as urlopen, patch.object(mod.time, "sleep") as sleep:
            self.assertEqual(mod.gh_get("/test"), {"ok": True})
        self.assertEqual(urlopen.call_count, 2)
        self.assertEqual(urlopen.call_args_list[0].kwargs["timeout"], 60)
        sleep.assert_called_once_with(1)

    def test_gh_get_raises_after_transient_retries_are_exhausted(self):
        errors = [urllib.error.HTTPError("url", 502, "bad gateway", {}, None) for _ in range(5)]
        with patch.object(mod.urllib.request, "urlopen", side_effect=errors) as urlopen, patch.object(mod.time, "sleep") as sleep:
            with self.assertRaises(urllib.error.HTTPError):
                mod.gh_get("/test")
        self.assertEqual(urlopen.call_count, 5)
        self.assertEqual([call.args[0] for call in sleep.call_args_list], [1, 2, 4, 8])

    def test_schedule_and_manual_dispatch_are_separate(self):
        runs = [
            {"id": 1, "html_url": "u1", "workflow_id": 10, "head_sha": "a", "event": "schedule", "status": "completed", "conclusion": "success", "run_attempt": 1, "created_at": "2026-08-01T00:00:00Z"},
            {"id": 2, "html_url": "u2", "workflow_id": 10, "head_sha": "b", "event": "workflow_dispatch", "status": "completed", "conclusion": "success", "run_attempt": 1, "created_at": "2026-08-02T00:00:00Z"},
            {"id": 3, "html_url": "u3", "workflow_id": 11, "head_sha": "c", "event": "push", "status": "completed", "conclusion": "failure", "run_attempt": 1, "created_at": "2026-08-03T00:00:00Z"},
        ]
        now = datetime(2026, 8, 12, tzinfo=timezone.utc)
        report = mod.aggregate("KAFKA2306/example", runs, now, now)
        self.assertEqual(report["runs"]["scheduled_runs"], 1)
        self.assertEqual(report["runs"]["manual_trigger_runs"], 1)
        self.assertEqual(report["runs"]["automated_trigger_runs"], 2)
        self.assertEqual(report["manual_start_actions_avoided"]["observed"], 1)
        self.assertIsNone(report["manual_interventions"]["value"])
        self.assertEqual(report["manual_interventions"]["manual_dispatch_runs"], 1)
        self.assertIsNone(report["failed_automation_requiring_manual_recovery"]["value"])
        self.assertEqual(report["failed_automation_requiring_manual_recovery"]["failed_or_cancelled_automated_runs"], 1)

    def test_unknown_and_zero_are_not_conflated(self):
        now = datetime(2026, 8, 12, tzinfo=timezone.utc)
        report = mod.aggregate("KAFKA2306/empty", [], now, now)
        self.assertEqual(report["runs"]["total"], 0)
        self.assertEqual(report["manual_start_actions_avoided"]["observed"], 0)
        self.assertIsNone(report["hours_saved"]["value"])
        self.assertEqual(report["hours_saved"]["status"], "unknown")
        self.assertIsNone(report["generated_artifacts_without_manual_editing"]["value"])


if __name__ == "__main__":
    unittest.main()
