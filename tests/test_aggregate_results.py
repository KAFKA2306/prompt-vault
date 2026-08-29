import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "results" / "aggregate.py"
spec = importlib.util.spec_from_file_location("aggregate_results", MODULE_PATH)
agg = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(agg)


def write(root: Path, category: str, name: str, payload: dict) -> Path:
    directory = root / category
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{name}.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


class AggregateResultsTests(unittest.TestCase):
    def test_unknown_and_zero_remain_distinct(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, "data-quality", "repo", {
                "schema_version": "kafka.results.data-quality.v1",
                "repository": "KAFKA2306/repo",
                "metrics": {
                    "duplicate_records": {"value": 0, "status": "measured"},
                    "verified_added_30d": {"value": None, "status": "unknown"},
                },
                "provenance": {"source_commit": "abc", "evidence": []},
            })
            rows = agg.load_inputs(root)
            result = agg.build_result(rows)
            self.assertFalse(result["contract"]["unknown_is_zero"])
            self.assertIsNone(result["summary_kpis"]["verified_data_added_30d"]["value"])
            self.assertEqual(result["summary_kpis"]["verified_data_added_30d"]["status"], "not_instrumented")
            self.assertEqual(rows[0]["payload"]["metrics"]["duplicate_records"]["value"], 0)

    def test_conflicting_duplicate_canonical_result_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            payload = {
                "schema_version": "kafka.results.adoption.v1",
                "repository": "KAFKA2306/repo",
                "metrics": {},
                "provenance": {"repository_url": "https://github.com/KAFKA2306/repo"},
            }
            write(root, "adoption", "a", payload)
            payload2 = dict(payload)
            payload2["extra"] = "different"
            write(root, "adoption", "b", payload2)
            with self.assertRaisesRegex(ValueError, "conflicting duplicate canonical result id"):
                agg.load_inputs(root)

    def test_require_all_validates_six_domain_inputs_and_outputs_are_deterministic(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for category, schema in agg.CATEGORIES.items():
                payload = {
                    "schema_version": schema,
                    "repository": f"KAFKA2306/{category}",
                    "generated_at": "2026-08-12T00:00:00+00:00",
                    "metrics": {},
                    "provenance": {"url": f"https://github.com/KAFKA2306/{category}"},
                }
                if category == "reliability":
                    payload["window"] = {"days": 30, "generated_at": "2026-08-12T00:00:00+00:00"}
                    payload["workflows"] = [{"first_attempt": {"total": 2, "success": 1}}]
                if category == "automation":
                    payload["manual_start_actions_avoided"] = {"observed": 3}
                if category == "code-quality":
                    payload["ratchet"] = {"status": "IMPROVED"}
                    payload["bugs"] = {}
                write(root, category, category, payload)

            rows = agg.load_inputs(root, require_all=True)
            first = agg.build_result(rows)
            second = agg.build_result(rows)
            self.assertEqual(first, second)
            self.assertEqual(len(first["results"]), 6)
            self.assertEqual(first["summary_kpis"]["workflow_first_attempt_success_rate"]["value"], 0.5)
            self.assertEqual(first["summary_kpis"]["scheduled_automated_starts"]["value"], 3)
            self.assertEqual(first["views"]["by_trend"]["IMPROVED"], 1)
            self.assertEqual(first["views"]["by_period"]["30d"]["status_counts"]["observed"], 1)
            markdown = agg.render_markdown(first)
            self.assertIn("Unknown, not-instrumented", markdown)
            self.assertIn("https://github.com/KAFKA2306/reliability", markdown)

    def test_snapshot_is_immutable_and_correction_creates_revision(self):
        with tempfile.TemporaryDirectory() as tmp:
            snapshots = Path(tmp)
            result = {
                "schema_version": agg.SCHEMA_VERSION,
                "generated_at": "2026-08-12T00:00:00+00:00",
                "contract": {}, "summary_kpis": {}, "views": {}, "results": [],
            }
            first = agg.write_snapshot(result, snapshots)
            same = agg.write_snapshot(result, snapshots)
            self.assertEqual(first, same)
            corrected = dict(result)
            corrected["contract"] = {"revision": True}
            revision = agg.write_snapshot(corrected, snapshots)
            self.assertEqual(revision.name, "2026-08-12-r2.json")
            self.assertTrue(first.exists())
            self.assertNotEqual(first.read_text(), revision.read_text())

    def test_url_status_is_metadata_not_an_evidence_url(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, "adoption", "repo", {
                "schema_version": "kafka.results.adoption.v1",
                "repository": "KAFKA2306/repo",
                "metrics": {},
                "inventory": {"url_status": "not_resolved_from_repository_metadata"},
                "provenance": {"repository_url": "https://github.com/KAFKA2306/repo"},
            })
            rows = agg.load_inputs(root)
            self.assertEqual(rows[0]["evidence_urls"], ["https://github.com/KAFKA2306/repo"])

    def test_invalid_evidence_url_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, "business", "repo", {
                "schema_version": "kafka.results.business.v1",
                "repository": "KAFKA2306/repo",
                "metrics": {},
                "provenance": {"repository_url": "not-a-url"},
            })
            with self.assertRaisesRegex(ValueError, "invalid evidence URL"):
                agg.load_inputs(root)


if __name__ == "__main__":
    unittest.main()
