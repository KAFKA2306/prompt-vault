#!/usr/bin/env python3
from pathlib import Path
import hashlib
import json
import sys

R = Path(__file__).resolve().parents[1]
errors = []

required = [
    "DESIGN.md",
    "USAGE.md",
    "tokens.json",
    "tokens.css",
    "tokens.schema.json",
    "components.html",
    "components.manifest.json",
    "voice.md",
    "anti-patterns.md",
    "icons/index.json",
    "icons/sprite.svg",
    "characters/kafka-character.json",
    "assets/provenance.json",
    "assets/registry.json",
    "consumers/schema.json",
    "scripts/vendor_assets.py",
    "audit/input.schema.json",
    "audit/scorecard.schema.json",
    "audit/scoring-policy.json",
    "audit/README.md",
    "scripts/score.py",
    "tests/test_score.py",
    "tests/test_vendor_assets.py",
]
for rel in required:
    if not (R / rel).is_file():
        errors.append("missing " + rel)


def load_json(rel):
    try:
        return json.loads((R / rel).read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"invalid json {rel}: {exc}")
        return None


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


tokens = load_json("tokens.json")
if tokens and tokens.get("meta", {}).get("version") != "1.0.0":
    errors.append("tokens version must be 1.0.0")

for rel in [
    "tokens.schema.json",
    "components.manifest.json",
    "assets/registry.json",
    "consumers/schema.json",
    "audit/input.schema.json",
    "audit/scorecard.schema.json",
    "audit/scoring-policy.json",
    "audit/fixtures/high-score-unverified.json",
    "audit/fixtures/verified-s.json",
]:
    if (R / rel).is_file():
        load_json(rel)
    else:
        errors.append("missing " + rel)

registry = load_json("assets/registry.json") if (R / "assets/registry.json").is_file() else None
if registry:
    if registry.get("schema_version") != "1.0.0":
        errors.append("asset registry schema_version must be 1.0.0")
    collections = registry.get("collections", [])
    if not isinstance(collections, list) or not collections:
        errors.append("asset registry must define at least one collection")
    else:
        seen_collections = set()
        for collection in collections:
            if not isinstance(collection, dict):
                errors.append("asset registry collection must be an object")
                continue
            collection_id = collection.get("id")
            manifest_rel = collection.get("manifest")
            if not isinstance(collection_id, str) or not collection_id:
                errors.append("asset registry collection id must be non-empty")
                continue
            if collection_id in seen_collections:
                errors.append("duplicate asset registry collection " + collection_id)
                continue
            seen_collections.add(collection_id)
            if not isinstance(manifest_rel, str) or not manifest_rel:
                errors.append("missing manifest for asset collection " + collection_id)
                continue
            manifest_path = R / manifest_rel
            try:
                if not manifest_path.resolve().is_relative_to(R.resolve()):
                    errors.append("asset collection manifest escapes canonical root " + collection_id)
                    continue
            except Exception as exc:
                errors.append(f"cannot resolve asset collection manifest {collection_id}: {exc}")
                continue
            manifest = load_json(manifest_rel) if manifest_path.is_file() else None
            if manifest is None:
                if not manifest_path.is_file():
                    errors.append("missing asset collection manifest " + manifest_rel)
                continue
            assets = manifest.get("assets", [])
            if not isinstance(assets, list):
                errors.append("asset collection has invalid assets list " + collection_id)
                continue
            seen_assets = set()
            for asset in assets:
                if not isinstance(asset, dict):
                    errors.append("asset entry must be an object in " + collection_id)
                    continue
                asset_id = asset.get("id")
                file_rel = asset.get("file")
                expected_hash = asset.get("sha256")
                if not all(isinstance(v, str) and v for v in (asset_id, file_rel, expected_hash)):
                    errors.append("asset requires id/file/sha256 in " + collection_id)
                    continue
                if asset_id in seen_assets:
                    errors.append(f"duplicate asset id {collection_id}/{asset_id}")
                    continue
                seen_assets.add(asset_id)
                asset_path = manifest_path.parent / file_rel
                try:
                    if not asset_path.resolve().is_relative_to(R.resolve()):
                        errors.append(f"asset escapes canonical root {collection_id}/{asset_id}")
                        continue
                except Exception as exc:
                    errors.append(f"cannot resolve asset {collection_id}/{asset_id}: {exc}")
                    continue
                if not asset_path.is_file():
                    errors.append(f"missing asset file {collection_id}/{asset_id}")
                    continue
                actual_hash = sha256_file(asset_path)
                if actual_hash != expected_hash:
                    errors.append(
                        f"asset hash mismatch {collection_id}/{asset_id} "
                        f"expected={expected_hash} actual={actual_hash}"
                    )

policy = load_json("audit/scoring-policy.json") if (R / "audit/scoring-policy.json").is_file() else None
if policy:
    dimensions = policy.get("dimensions", [])
    if len(dimensions) != 8 or len(set(dimensions)) != 8:
        errors.append("scoring policy must define exactly 8 unique dimensions")
    thresholds = policy.get("thresholds", [])
    covered = []
    for row in thresholds:
        covered.extend(range(row.get("min", 1), row.get("max", -1) + 1))
    if sorted(covered) != list(range(41)):
        errors.append("scoring thresholds must cover every total from 0 to 40 exactly once")
    if set(policy.get("required_viewports", [])) != {360, 768, 1440}:
        errors.append("required viewports must be 360, 768, 1440")

for p in R.rglob("*.svg"):
    s = p.read_text(encoding="utf-8").lower()
    if "<script" in s or "onload=" in s:
        errors.append("unsafe svg " + str(p))

if errors:
    print("\n".join(errors), file=sys.stderr)
    raise SystemExit(1)
print("KAFKA SIGNAL validation passed")
