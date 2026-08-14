import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
ICON_DIR = ROOT / "icons"
PROVENANCE = ["verified", "pinned-commit", "checksum", "canonical", "external-source", "generated", "human-reviewed"]


class ProvenanceIconTests(unittest.TestCase):
    def setUp(self):
        self.index = json.loads((ICON_DIR / "index.json").read_text(encoding="utf-8"))
        self.asset = json.loads((ICON_DIR / "manifest.json").read_text(encoding="utf-8"))["assets"][0]
        root = ET.parse(ICON_DIR / "sprite.svg").getroot()
        self.symbols = {node.attrib["id"].removeprefix("ks-") for node in root if node.tag.endswith("symbol")}

    def test_provenance_symbols_are_registered(self):
        self.assertEqual(self.asset["provenance_symbols"], PROVENANCE)
        self.assertTrue(set(PROVENANCE).issubset(self.symbols))
        self.assertTrue(set(PROVENANCE).issubset(set(self.index["icons"])))

    def test_each_provenance_symbol_has_semantic_definition(self):
        semantics = self.asset["provenance_semantics"]
        self.assertEqual(set(semantics), set(PROVENANCE))
        self.assertTrue(all(len(value.strip()) > 20 for value in semantics.values()))
        self.assertNotEqual(semantics["verified"], semantics["human-reviewed"])
        self.assertNotEqual(semantics["canonical"], semantics["pinned-commit"])

    def test_provenance_claims_require_text_and_evidence(self):
        policy = self.index["policy"].lower()
        notes = self.asset["notes"].lower()
        self.assertIn("visible text", policy)
        self.assertIn("evidence links", policy)
        self.assertIn("evidence links", notes)
        self.assertIn("immutable", notes)
        self.assertIn("vendor", notes)


if __name__ == "__main__":
    unittest.main()
