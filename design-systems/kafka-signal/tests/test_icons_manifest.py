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
REQUIRED_STATUSES = {
    "live",
    "snapshot",
    "refresh",
    "waiting",
    "blocked",
    "success",
    "failed",
    "stale",
    "fallback",
}


class IconManifestTests(unittest.TestCase):
    def setUp(self):
        self.index = json.loads((ICON_DIR / "index.json").read_text(encoding="utf-8"))
        self.manifest = json.loads((ICON_DIR / "manifest.json").read_text(encoding="utf-8"))
        self.sprite_path = ICON_DIR / "sprite.svg"
        self.asset = self.manifest["assets"][0]
        self.root = ET.parse(self.sprite_path).getroot()
        self.symbols = {
            element.attrib["id"].removeprefix("ks-"): element
            for element in self.root
            if element.tag.endswith("symbol")
        }

    def test_required_action_icons_are_canonical(self):
        self.assertTrue(REQUIRED_ACTIONS.issubset(set(self.index["icons"])))
        self.assertTrue(REQUIRED_ACTIONS.issubset(set(self.asset["symbols"])))
        self.assertEqual(
            self.asset["action_symbols"][:5],
            ["commit", "pull-request", "workflow", "merge", "deploy"],
        )

    def test_required_operational_status_icons_are_canonical_and_distinct(self):
        self.assertEqual(set(self.asset["status_symbols"]), REQUIRED_STATUSES)
        self.assertTrue(REQUIRED_STATUSES.issubset(set(self.index["icons"])))
        signatures = {
            ET.tostring(self.symbols[name], encoding="unicode")
            for name in REQUIRED_STATUSES
        }
        self.assertEqual(len(signatures), len(REQUIRED_STATUSES))

    def test_sprite_symbols_match_index_and_manifest(self):
        symbols = list(self.symbols)
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
        self.assertIn("contrast", notes)
        self.assertIn("asset fails to load", notes)
        self.assertIn("immutable", notes)
        self.assertIn("vendor", notes)
        self.assertIn("must not hotlink mutable main", notes)


if __name__ == "__main__":
    unittest.main()
