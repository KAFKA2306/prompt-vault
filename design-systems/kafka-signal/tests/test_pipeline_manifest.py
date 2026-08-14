import hashlib
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "assets" / "pipeline"
STAGES = ["source", "ingest", "normalize", "validate", "model", "publish", "deploy", "monitor"]


class PipelineManifestTests(unittest.TestCase):
    def setUp(self):
        self.registry = json.loads((ROOT / "assets" / "registry.json").read_text(encoding="utf-8"))
        self.manifest = json.loads((ASSET_DIR / "manifest.json").read_text(encoding="utf-8"))
        self.icon_index = json.loads((ROOT / "icons" / "index.json").read_text(encoding="utf-8"))
        self.icon_manifest = json.loads((ROOT / "icons" / "manifest.json").read_text(encoding="utf-8"))["assets"][0]

    def test_pipeline_collection_is_registered(self):
        collections = {row["id"]: row for row in self.registry["collections"]}
        self.assertEqual(collections["pipeline"]["manifest"], "assets/pipeline/manifest.json")

    def test_pipeline_stage_order_and_reuse_contract(self):
        self.assertEqual(self.icon_manifest["pipeline_stage_symbols"], STAGES)
        self.assertEqual(len(self.icon_index["icons"]), len(set(self.icon_index["icons"])))
        for reused in ("source", "model", "deploy"):
            self.assertEqual(self.icon_index["icons"].count(reused), 1)

    def test_pipeline_assets_exist_parse_and_match_hashes(self):
        ids = {asset["id"] for asset in self.manifest["assets"]}
        self.assertIn("pipeline.connector.horizontal.v1", ids)
        self.assertIn("pipeline.connector.vertical.v1", ids)
        for asset in self.manifest["assets"]:
            path = ASSET_DIR / asset["file"]
            self.assertTrue(path.is_file())
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), asset["sha256"])
            root = ET.parse(path).getroot()
            self.assertTrue(root.attrib.get("viewBox"))

    def test_example_flow_keeps_visible_stage_labels(self):
        text = (ASSET_DIR / "example-flow.svg").read_text(encoding="utf-8")
        for stage in STAGES:
            self.assertIn(f">{stage}<", text)
        self.assertIn("Labels are required", text)


if __name__ == "__main__":
    unittest.main()
