import hashlib
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "assets" / "agent-world-props" / "manifest.json"
REQUIRED = {
    "prop.server-rack.v1", "prop.build-terminal.v1", "prop.review-board.v1", "prop.issue-board.v1",
    "prop.data-crate.v1", "prop.deploy-gate.v1", "prop.database.v1", "prop.chart-wall.v1",
    "prop.package-box.v1", "prop.warning-cone.v1", "prop.composition.v1",
}


class AgentWorldPropTests(unittest.TestCase):
    def setUp(self):
        self.registry = json.loads((ROOT / "assets" / "registry.json").read_text(encoding="utf-8"))
        self.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    def test_collection_and_stable_ids_are_registered(self):
        collections = {row["id"]: row for row in self.registry["collections"]}
        self.assertEqual(collections["agent-world-props"]["manifest"], "assets/agent-world-props/manifest.json")
        ids = {asset["id"] for asset in self.manifest["assets"]}
        self.assertEqual(ids, REQUIRED)

    def test_prop_assets_are_transparent_predictable_and_hashed(self):
        for asset in self.manifest["assets"]:
            path = (MANIFEST_PATH.parent / asset["file"]).resolve()
            self.assertTrue(path.is_file())
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), asset["sha256"])
            root = ET.parse(path).getroot()
            expected = "0 0 384 192" if asset["id"] == "prop.composition.v1" else "0 0 128 128"
            self.assertEqual(root.attrib.get("viewBox"), expected)
            self.assertNotIn("style", root.attrib)

    def test_consumer_contract_keeps_canonical_state_in_ui(self):
        note = self.manifest["note"].lower()
        defaults = self.manifest["defaults"]
        self.assertTrue(defaults["visible_label_required"])
        self.assertFalse(defaults["mutable_main_hotlink"])
        self.assertIn("canonical role and state remain visible", note)
        self.assertIn("immutable", note)
        self.assertIn("artwork is unavailable", note)
        composition = (ROOT / "assets" / "agent-world" / "prop-composition.svg").read_text(encoding="utf-8")
        self.assertIn("canonical state remains visible", composition)


if __name__ == "__main__":
    unittest.main()
