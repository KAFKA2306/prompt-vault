import base64
import json
import unittest
from unittest.mock import patch

from scripts.collect_data_quality import semiconductor_report, uninstrumented_report


def contents(data, path):
    raw = json.dumps(data).encode()
    return {
        "encoding": "base64",
        "content": base64.b64encode(raw).decode(),
        "sha": f"sha-{path}",
        "html_url": f"https://example.invalid/{path}",
    }


class DataQualityCollectorTest(unittest.TestCase):
    def test_uninstrumented_never_turns_unknown_into_zero(self):
        report = uninstrumented_report("KAFKA2306/example")
        self.assertEqual(report["instrumentation"]["status"], "not_instrumented")
        self.assertIsNone(report["canonical_population"]["value"])
        for metric in report["metrics"].values():
            self.assertIsNone(metric.get("value"))

    def test_semiconductor_adapter_reuses_repository_audits(self):
        docs = {
            "audit_latest.json": {"accepted_events_total": 3, "status": "PASS"},
            "evidence_latest.json": {
                "verified_events": 2,
                "window_start": "2026-08-10T00:00:00Z",
                "window_end": "2026-08-11T00:00:00Z",
                "status": "PASS",
            },
            "lineage_latest.json": {
                "artifacts": [{"sha256": "a"}, {"sha256": "b"}],
                "status": "PASS",
            },
            "semantic_duplicate_audit_latest.json": {"duplicate_count": 1, "status": "PASS"},
            "rejection_reason_audit_latest.json": {
                "rejected_events_total": 4,
                "raw_reason_counts": {"A": 3, "B": 1},
                "status": "PASS",
            },
        }

        def fake_get(path, token=None):
            if "/commits/" in path:
                return {"sha": "abc123"}
            for filename, data in docs.items():
                if filename in path:
                    return contents(data, filename)
            raise AssertionError(path)

        with patch("scripts.collect_data_quality.gh_get", side_effect=fake_get):
            report = semiconductor_report("KAFKA2306/semiconductor-earnings-model", "main", None)

        self.assertEqual(report["canonical_population"]["value"], 3)
        self.assertEqual(report["metrics"]["verified_records"]["value"], 2)
        self.assertEqual(report["metrics"]["duplicate_records"]["value"], 1)
        self.assertEqual(report["metrics"]["source_hash_coverage"]["ratio"], 1.0)
        self.assertEqual(report["metrics"]["rejection_reason_coverage"]["ratio"], 1.0)
        self.assertIsNone(report["metrics"]["record_provenance_coverage"]["value"])
        self.assertIsNone(report["metrics"]["verified_added_30d"]["value"])
        self.assertEqual(report["provenance"]["source_commit"], "abc123")
        self.assertEqual(len(report["provenance"]["evidence"]), 5)


if __name__ == "__main__":
    unittest.main()
