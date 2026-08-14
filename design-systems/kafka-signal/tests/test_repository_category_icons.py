import hashlib
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
ICON_DIR = ROOT / "icons"
CATEGORIES = ["finance", "boardgame", "vr", "avatar", "research", "data", "developer-tool", "media", "automation", "unknown"]


class RepositoryCategoryIconTests(unittest.TestCase):
    def setUp(self):
        self.index = json.loads((ICON_DIR / "index.json").read_text(encoding="utf-8"))
        manifest = json.loads((ICON_DIR / "manifest.json").read_text(encoding="utf-8"))
        self.asset = next(asset for asset in manifest["assets"] if asset["id"] == "icons.repository-categories.v1")
        self.sprite_path = ICON_DIR / "repository-categories.svg"
        root = ET.parse(self.sprite_path).getroot()
        self.symbols = [node.attrib["id"].removeprefix("ks-") for node in root if node.tag.endswith("symbol")]

    def test_index_and_manifest_define_stable_category_mapping(self):
        self.assertEqual(self.index["repositoryCategories"], CATEGORIES)
        expected = {category: f"category-{category}" for category in CATEGORIES}
        self.assertEqual(self.asset["category_mapping"], expected)
        self.assertEqual(self.asset["fallback_category"], "unknown")
        self.assertEqual(self.symbols, list(expected.values()))
        self.assertEqual(self.asset["symbols"], self.symbols)

    def test_category_sprite_hash_and_viewboxes_are_canonical(self):
        self.assertEqual(hashlib.sha256(self.sprite_path.read_bytes()).hexdigest(), self.asset["sha256"])
        root = ET.parse(self.sprite_path).getroot()
        category_symbols = [node for node in root if node.tag.endswith("symbol")]
        self.assertTrue(all(node.attrib.get("viewBox") == "0 0 24 24" for node in category_symbols))

    def test_consumer_contract_forbids_inference_and_requires_visible_text(self):
        policy = self.index["policy"].lower()
        notes = self.asset["notes"].lower()
        usage = set(self.asset["allowed_usage"])
        self.assertIn("canonical repository metadata", policy)
        self.assertIn("never infer", policy)
        self.assertIn("visible text", policy)
        self.assertIn("never infer a category", notes)
        self.assertIn("unknown", notes)
        self.assertIn("immutable", notes)
        self.assertIn("vendor", notes)
        self.assertIn("must not hotlink mutable main", notes)
        self.assertIn("agent-resources-repository-station", usage)
        self.assertIn("agent-resources-repository-list", usage)


if __name__ == "__main__":
    unittest.main()
