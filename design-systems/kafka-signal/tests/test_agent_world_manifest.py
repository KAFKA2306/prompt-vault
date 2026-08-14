from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK_DIR = ROOT / "assets" / "agent-world"
MANIFEST_PATH = PACK_DIR / "manifest.json"
PROP_MANIFEST_PATH = ROOT / "assets" / "agent-world-props" / "manifest.json"
CONSUMER_PATH = ROOT / "consumers" / "agent-resources.json"


class AgentWorldManifestTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        cls.assets = cls.manifest["assets"]
        cls.by_id = {asset["id"]: asset for asset in cls.assets}

    def test_manifest_exposes_stable_production_contract(self) -> None:
        self.assertEqual(self.manifest["schema_version"], "1.1.0")
        self.assertEqual(
            self.manifest["production_policy"],
            {
                "source": "manifest-only",
                "raw_file_usage": "forbidden",
                "consumer_resolution": "stable-id-via-registry",
            },
        )
        self.assertEqual(len(self.by_id), len(self.assets))
        required = {
            "id",
            "file",
            "sha256",
            "category",
            "role",
            "state",
            "allowed_usage",
            "notes",
        }
        for asset in self.assets:
            self.assertTrue(required <= asset.keys(), asset["id"])
            self.assertEqual(asset["class"], asset["category"], asset["id"])
            self.assertTrue(asset["role"], asset["id"])
            self.assertTrue(asset["state"], asset["id"])
            self.assertTrue(asset["allowed_usage"], asset["id"])
            self.assertTrue(asset["notes"], asset["id"])

    def test_all_raw_svg_files_are_registered_exactly_once(self) -> None:
        registered = [(PACK_DIR / asset["file"]).resolve() for asset in self.assets]
        if PROP_MANIFEST_PATH.is_file():
            prop_manifest = json.loads(PROP_MANIFEST_PATH.read_text(encoding="utf-8"))
            registered.extend(
                (PROP_MANIFEST_PATH.parent / asset["file"]).resolve()
                for asset in prop_manifest["assets"]
            )
        self.assertEqual(len(registered), len(set(registered)))
        raw = sorted(path.resolve() for path in PACK_DIR.glob("*.svg"))
        self.assertEqual(sorted(registered), raw)

    def test_role_state_selectors_are_deterministic_and_consistent(self) -> None:
        selectors = self.manifest["selectors"]
        keys = [(row["role"], row["state"]) for row in selectors]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertEqual(len(selectors), len(self.assets))
        selected_ids = {row["asset_id"] for row in selectors}
        self.assertEqual(selected_ids, set(self.by_id))
        for row in selectors:
            asset = self.by_id[row["asset_id"]]
            self.assertEqual(row["role"], asset["role"])
            self.assertEqual(row["state"], asset["state"])

    def test_agent_resources_consumes_registered_ids_only(self) -> None:
        consumer = json.loads(CONSUMER_PATH.read_text(encoding="utf-8"))
        agent_world = [
            row for row in consumer["assets"] if row["collection"] == "agent-world"
        ]
        self.assertTrue(agent_world)
        self.assertEqual({row["id"] for row in agent_world}, set(self.by_id))


if __name__ == "__main__":
    unittest.main()
