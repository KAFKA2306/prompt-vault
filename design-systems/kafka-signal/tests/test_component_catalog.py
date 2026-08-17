import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ComponentCatalogTests(unittest.TestCase):
    def test_catalog_uses_canonical_manifest_and_search(self) -> None:
        html = (ROOT / "components.html").read_text(encoding="utf-8")
        manifest = json.loads((ROOT / "components.manifest.json").read_text(encoding="utf-8"))

        self.assertIn('fetch("components.manifest.json")', html)
        self.assertIn('type="search"', html)
        self.assertIn('aria-live="polite"', html)
        self.assertGreaterEqual(len(manifest["components"]), 1)

        for name, features in manifest["components"].items():
            self.assertTrue(name)
            self.assertIsInstance(features, list)
            self.assertGreaterEqual(len(features), 1)


if __name__ == "__main__":
    unittest.main()
