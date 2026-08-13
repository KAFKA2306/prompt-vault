from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "vendor_assets.py"
SPEC = importlib.util.spec_from_file_location("vendor_assets", SCRIPT)
assert SPEC and SPEC.loader
vendor_assets = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(vendor_assets)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class VendorAssetsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.signal = self.root / "signal"
        self.consumer_root = self.root / "consumer"
        self.signal.mkdir()
        self.consumer_root.mkdir()

        (self.signal / "manifest.json").write_text(
            json.dumps({"release": "kafka-signal-v-test"}), encoding="utf-8"
        )
        (self.signal / "assets" / "test").mkdir(parents=True)
        payload = b"canonical-asset\n"
        (self.signal / "assets" / "test" / "hero.txt").write_bytes(payload)
        asset_hash = sha256_bytes(payload)
        (self.signal / "assets" / "test" / "manifest.json").write_text(
            json.dumps(
                {
                    "assets": [
                        {
                            "id": "hero",
                            "file": "hero.txt",
                            "sha256": asset_hash,
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        (self.signal / "assets" / "registry.json").write_text(
            json.dumps(
                {
                    "schema_version": "1.0.0",
                    "canonical_repository": "KAFKA2306/prompt-vault",
                    "release_manifest": "manifest.json",
                    "collections": [
                        {"id": "test", "manifest": "assets/test/manifest.json"}
                    ],
                }
            ),
            encoding="utf-8",
        )
        self.consumer_manifest = self.root / "consumer.json"
        self.write_consumer("public/assets/hero.txt")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def write_consumer(self, destination: str) -> None:
        self.consumer_manifest.write_text(
            json.dumps(
                {
                    "schema_version": "1.0.0",
                    "repository": "KAFKA2306/example",
                    "assets": [
                        {
                            "collection": "test",
                            "id": "hero",
                            "destination": destination,
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

    def run_vendor(self, *, dry_run: bool = False):
        return vendor_assets.vendor_assets(
            signal_root=self.signal,
            destination_root=self.consumer_root,
            consumer_manifest=self.consumer_manifest,
            canonical_commit="0123456789abcdef0123456789abcdef01234567",
            dry_run=dry_run,
        )

    def test_vendors_selected_asset_and_writes_lock(self) -> None:
        result = self.run_vendor()
        destination = self.consumer_root / "public/assets/hero.txt"
        self.assertEqual(destination.read_bytes(), b"canonical-asset\n")
        lock = json.loads(
            (self.consumer_root / ".kafka-signal/pages-assets.lock.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(lock["release"], "kafka-signal-v-test")
        self.assertEqual(lock["canonical_commit"], "0123456789abcdef0123456789abcdef01234567")
        self.assertEqual(lock["assets"][0]["destination"], "public/assets/hero.txt")
        self.assertEqual(result["plan"][0]["action"], "copy")

    def test_dry_run_does_not_write_asset_or_lock(self) -> None:
        result = self.run_vendor(dry_run=True)
        self.assertEqual(result["plan"][0]["action"], "copy")
        self.assertFalse((self.consumer_root / "public/assets/hero.txt").exists())
        self.assertFalse((self.consumer_root / ".kafka-signal/pages-assets.lock.json").exists())

    def test_rejects_canonical_hash_mismatch(self) -> None:
        manifest_path = self.signal / "assets/test/manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["assets"][0]["sha256"] = "0" * 64
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaisesRegex(vendor_assets.AssetRegistryError, "canonical hash mismatch"):
            self.run_vendor()

    def test_rejects_path_traversal(self) -> None:
        self.write_consumer("../escape.txt")
        with self.assertRaisesRegex(vendor_assets.AssetRegistryError, "unsafe path segment"):
            self.run_vendor()

    def test_rejects_unmanaged_overwrite(self) -> None:
        destination = self.consumer_root / "public/assets/hero.txt"
        destination.parent.mkdir(parents=True)
        destination.write_text("local file\n", encoding="utf-8")
        with self.assertRaisesRegex(vendor_assets.AssetRegistryError, "unmanaged destination"):
            self.run_vendor()

    def test_rejects_local_drift_after_lock(self) -> None:
        self.run_vendor()
        destination = self.consumer_root / "public/assets/hero.txt"
        destination.write_text("locally modified\n", encoding="utf-8")
        with self.assertRaisesRegex(vendor_assets.AssetRegistryError, "local modification"):
            self.run_vendor()


if __name__ == "__main__":
    unittest.main()
