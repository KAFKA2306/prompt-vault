import hashlib
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
ICON_DIR = ROOT / "icons"
REQUIRED_ACTIONS = {
    "commit",
    "merge",
    "branch",
    "release",
    "deploy",
    "test",
    "build",
    "package",
    "tag",
    "comment",
    "review",
}


class IconManifestTests(unittest.TestCase):
    def setUp(self):
        self.index = json.loads((ICON_DIR / "index.json").read_text(encoding="utf-8"))
        self.manifest = json.loads((ICON_DIR / "manifest.json").read_text(encoding="utf-8"))
        self.sprite_path = ICON_DIR / "sprite.svg"
        self.asset = self.manifest["assets"][0]
        self.root = ET.parse(self.sprite_path).getroot()

    def test_required_action_icons_are_canonical(self):
        self.assertTrue(REQUIRED_ACTIONS.issubset(set(self.index["icons"])))
        self.assertTrue(REQUIRED_ACTIONS.issubset(set(self.asset["symbols"])))
        self.assertEqual(
            self.asset["action_symbols"][:5],
            ["commit", "pull-request", "workflow", "merge", "deploy"],
        )

    def test_sprite_symbols_match_index_and_manifest(self):
        symbols = [
            element.attrib["id"].removeprefix("ks-")
            for element in self.root
            if element.tag.endswith("symbol")
        ]
        self.assertEqual(len(symbols), len(set(symbols)))
        self.assertEqual(symbols, self.index["icons"])
        self.assertEqual(symbols, self.asset["symbols"])
        self.assertTrue(all(element.attrib.get("viewBox") == "0 0 24 24" for element in self.root))

    def test_manifest_sha256_matches_sprite(self):
        actual = hashlib.sha256(self.sprite_path.read_bytes()).hexdigest()
        self.assertEqual(actual, self.asset["sha256"])

    def test_accessibility_and_distribution_contract_is_explicit(self):
        policy = self.index["policy"].lower()
        notes = self.asset["notes"].lower()
        self.assertIn("visible text", policy)
        self.assertIn("immutable", notes)
        self.assertIn("vendor", notes)
        self.assertIn("must not hotlink mutable main", notes)


if __name__ == "__main__":
    unittest.main()
