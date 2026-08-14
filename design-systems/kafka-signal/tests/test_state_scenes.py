import hashlib
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
SCENES = ROOT / "assets" / "state-scenes"
REQUIRED = {
    "empty.no-activity.v1",
    "empty.no-issues.v1",
    "success.all-green.v1",
    "waiting.approval.v1",
    "failure.ci.v1",
    "deploy.completed.v1",
    "state-scenes.fixture.v1",
}


class StateSceneTests(unittest.TestCase):
    def setUp(self):
        self.registry = json.loads((ROOT / "assets" / "registry.json").read_text(encoding="utf-8"))
        self.manifest = json.loads((SCENES / "manifest.json").read_text(encoding="utf-8"))

    def test_dedicated_collection_and_design_decision_are_recorded(self):
        collections = {row["id"]: row for row in self.registry["collections"]}
        self.assertEqual(collections["state-scenes"]["manifest"], "assets/state-scenes/manifest.json")
        readme = (SCENES / "README.md").read_text(encoding="utf-8")
        self.assertIn("dedicated collection", readme)
        self.assertIn("site-basics", readme)
        self.assertIn("State is selected only from canonical consumer data", readme)

    def test_stable_ids_semantics_and_fallback_contract(self):
        assets = self.manifest["assets"]
        self.assertEqual({asset["id"] for asset in assets}, REQUIRED)
        self.assertTrue(all(len(asset["semantic"].strip()) > 40 for asset in assets))
        defaults = self.manifest["defaults"]
        self.assertTrue(defaults["visible_heading_required"])
        self.assertTrue(defaults["visible_description_required"])
        self.assertTrue(defaults["asset_failure_keeps_information_ui"])
        self.assertFalse(defaults["mutable_main_hotlink"])
        note = self.manifest["note"].lower()
        self.assertIn("canonical data", note)
        self.assertIn("asset failure", note)

    def test_assets_parse_match_hashes_and_use_predictable_viewboxes(self):
        for asset in self.manifest["assets"]:
            path = SCENES / asset["file"]
            self.assertTrue(path.is_file())
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), asset["sha256"])
            root = ET.parse(path).getroot()
            expected = "0 0 576 176" if asset["id"] == "state-scenes.fixture.v1" else "0 0 192 128"
            self.assertEqual(root.attrib.get("viewBox"), expected)

    def test_fixture_reviews_empty_success_and_failure_with_visible_labels(self):
        fixture = (SCENES / "fixture.svg").read_text(encoding="utf-8")
        for label in ("No activity", "All green", "CI failed"):
            self.assertIn(f">{label}<", fixture)


if __name__ == "__main__":
    unittest.main()
