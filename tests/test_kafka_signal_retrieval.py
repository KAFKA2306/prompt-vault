from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "design-systems" / "kafka-signal" / "scripts" / "retrieve_components.py"
SPEC = importlib.util.spec_from_file_location("retrieve_components", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
retrieval = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(retrieval)


class KafkaSignalRetrievalTests(unittest.TestCase):
    def test_japanese_evidence_query_finds_evidence_meta(self) -> None:
        result = retrieval.search(retrieval.load_index(), "証拠 出典 更新日時")
        ids = [item["component_id"] for item in result["results"]]
        self.assertIn("EvidenceMeta", ids)
        top = result["results"][0]
        self.assertGreater(top["score"], 0)
        self.assertTrue(top["reasons"])

    def test_history_query_is_bilingual(self) -> None:
        ja = retrieval.search(retrieval.load_index(), "履歴 差分")
        en = retrieval.search(retrieval.load_index(), "history changed")
        self.assertEqual(ja["results"][0]["component_id"], "HistoryDiff")
        self.assertEqual(en["results"][0]["component_id"], "HistoryDiff")

    def test_uninstrumented_quality_filter_fails_closed(self) -> None:
        result = retrieval.search(
            retrieval.load_index(),
            "evidence",
            grade="A",
            framework="astro",
        )
        self.assertEqual(result["results"], [])
        self.assertEqual(result["measurement_boundary"]["grade"], "not_instrumented")
        self.assertEqual(
            result["measurement_boundary"]["frameworks"], "not_instrumented"
        )

    def test_index_does_not_invent_quality_or_original_provenance(self) -> None:
        index = retrieval.load_index()
        self.assertTrue(index["records"])
        for record in index["records"]:
            self.assertIsNone(record["grade"])
            self.assertIsNone(record["frameworks"])
            self.assertIsNone(record["responsive"])
            self.assertIsNone(record["accessibility"])
            self.assertEqual(record["source"]["repository"], "KAFKA2306/prompt-vault")
            self.assertTrue(record["source"]["path"].endswith("components.manifest.json"))

    def test_invalid_manifest_shape_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "components.manifest.json").write_text(
                json.dumps({"version": "1", "components": {"Bad": "not-a-list"}}),
                encoding="utf-8",
            )
            (root / "manifest.json").write_text(
                json.dumps(
                    {
                        "canonical_repository": "KAFKA2306/prompt-vault",
                        "canonical_path": "design-systems/kafka-signal",
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                retrieval.load_index(root)

    def test_machine_readable_output_contains_traceability_fields(self) -> None:
        result = retrieval.search(retrieval.load_index(), "timeline")
        item = result["results"][0]
        self.assertEqual(item["component_id"], "Timeline")
        self.assertIn("repository", item["source"])
        self.assertIn("path", item["source"])
        self.assertIn("commit", item["source"])
        self.assertEqual(result["schema_version"], "kafka-signal-retrieval-result.v1")


if __name__ == "__main__":
    unittest.main()
