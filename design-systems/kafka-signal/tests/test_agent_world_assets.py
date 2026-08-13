import hashlib
import json
import unittest
from pathlib import Path

KS = Path(__file__).resolve().parents[1]
REGISTRY = KS / "assets" / "registry.json"
MANIFEST = KS / "assets" / "agent-world" / "manifest.json"
CONSUMER = KS / "consumers" / "agent-resources.json"
PREVIEW = KS / "preview" / "agent-world-assets.html"


class AgentWorldAssetsTest(unittest.TestCase):
    def setUp(self):
        self.registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        self.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.consumer = json.loads(CONSUMER.read_text(encoding="utf-8"))
        self.assets = self.manifest["assets"]
        self.by_id = {asset["id"]: asset for asset in self.assets}

    def test_collection_is_registered(self):
        collections = {entry["id"]: entry for entry in self.registry["collections"]}
        self.assertIn("agent-world", collections)
        self.assertEqual(collections["agent-world"]["manifest"], "assets/agent-world/manifest.json")

    def test_asset_ids_are_unique_and_files_match_hashes(self):
        self.assertEqual(len(self.by_id), len(self.assets))
        for asset in self.assets:
            path = MANIFEST.parent / asset["file"]
            self.assertTrue(path.is_file(), asset["id"])
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(digest, asset["sha256"], asset["id"])
            self.assertEqual(asset["format"], "image/svg+xml")
            self.assertTrue(asset["decorative"])

    def test_role_and_state_contract_is_complete(self):
        roles = {asset.get("role") for asset in self.assets if asset["category"] == "role"}
        states = {asset.get("state") for asset in self.assets if asset["category"] == "state"}
        scenes = {asset.get("scene") for asset in self.assets if asset["category"] == "scene"}
        self.assertEqual(roles, {"issue", "pull_request", "workflow_run"})
        self.assertEqual(states, {"working", "waiting", "done", "failed"})
        self.assertTrue({"desk", "review-bench", "station-sign", "floor-tile", "terminal"} <= scenes)

    def test_agent_resources_consumer_resolves_only_registered_ids(self):
        self.assertEqual(self.consumer["repository"], "KAFKA2306/agent-resources")
        self.assertEqual(len(self.consumer["assets"]), len(self.assets))
        for requested in self.consumer["assets"]:
            self.assertEqual(requested["collection"], "agent-world")
            self.assertIn(requested["id"], self.by_id)
            self.assertFalse(requested["destination"].startswith("/"))
            self.assertNotIn("..", Path(requested["destination"]).parts)

    def test_mutable_main_hotlink_is_forbidden(self):
        self.assertFalse(self.manifest["consumer_contract"]["runtime_hotlink_mutable_main"])
        serialized = MANIFEST.read_text(encoding="utf-8") + CONSUMER.read_text(encoding="utf-8")
        self.assertNotIn("raw.githubusercontent.com/KAFKA2306/prompt-vault/main", serialized)

    def test_preview_contains_every_asset(self):
        html = PREVIEW.read_text(encoding="utf-8")
        for asset in self.assets:
            self.assertIn(asset["file"], html)
            self.assertIn(asset["id"], html)


if __name__ == "__main__":
    unittest.main()
