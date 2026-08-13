#!/usr/bin/env python3
"""Vendor selected KAFKA SIGNAL Pages assets into a checked-out consumer repo."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path, PurePosixPath
from typing import Any

LOCK_PATH = Path(".kafka-signal/pages-assets.lock.json")


class AssetRegistryError(RuntimeError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise AssetRegistryError(f"missing JSON file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise AssetRegistryError(f"invalid JSON: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise AssetRegistryError(f"JSON root must be an object: {path}")
    return data


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_relative_path(value: str, *, label: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise AssetRegistryError(f"{label} must be a non-empty string")
    if "\\" in value:
        raise AssetRegistryError(f"{label} must use POSIX-style separators: {value}")
    pure = PurePosixPath(value)
    if pure.is_absolute() or value.startswith("/"):
        raise AssetRegistryError(f"{label} must be repository-relative: {value}")
    if any(part in {"", ".", ".."} for part in pure.parts):
        raise AssetRegistryError(f"{label} contains an unsafe path segment: {value}")
    if pure.parts and pure.parts[0].lower() == ".git":
        raise AssetRegistryError(f"{label} may not write inside .git: {value}")
    if pure.parts and ":" in pure.parts[0]:
        raise AssetRegistryError(f"{label} may not be a drive-qualified path: {value}")
    return Path(*pure.parts)


def require_inside(root: Path, candidate: Path, *, label: str) -> None:
    root_resolved = root.resolve()
    candidate_resolved = candidate.resolve()
    if not candidate_resolved.is_relative_to(root_resolved):
        raise AssetRegistryError(f"{label} escapes canonical root: {candidate}")


def load_asset_index(signal_root: Path) -> tuple[dict[str, Any], dict[tuple[str, str], dict[str, Any]]]:
    registry = load_json(signal_root / "assets/registry.json")
    if registry.get("schema_version") != "1.0.0":
        raise AssetRegistryError("unsupported asset registry schema_version")

    collections = registry.get("collections")
    if not isinstance(collections, list) or not collections:
        raise AssetRegistryError("asset registry must contain at least one collection")

    index: dict[tuple[str, str], dict[str, Any]] = {}
    seen_collections: set[str] = set()
    for collection in collections:
        if not isinstance(collection, dict):
            raise AssetRegistryError("collection entries must be objects")
        collection_id = collection.get("id")
        manifest_value = collection.get("manifest")
        if not isinstance(collection_id, str) or not collection_id:
            raise AssetRegistryError("collection.id must be a non-empty string")
        if collection_id in seen_collections:
            raise AssetRegistryError(f"duplicate collection id: {collection_id}")
        seen_collections.add(collection_id)

        manifest_rel = safe_relative_path(manifest_value, label="collection manifest")
        manifest_path = signal_root / manifest_rel
        require_inside(signal_root, manifest_path, label="collection manifest")
        manifest = load_json(manifest_path)
        assets = manifest.get("assets")
        if not isinstance(assets, list):
            raise AssetRegistryError(f"collection has no assets array: {collection_id}")

        for asset in assets:
            if not isinstance(asset, dict):
                raise AssetRegistryError(f"asset entries must be objects: {collection_id}")
            asset_id = asset.get("id")
            file_value = asset.get("file")
            expected_hash = asset.get("sha256")
            if not all(isinstance(value, str) and value for value in (asset_id, file_value, expected_hash)):
                raise AssetRegistryError(f"asset requires id, file and sha256: {collection_id}")
            key = (collection_id, asset_id)
            if key in index:
                raise AssetRegistryError(f"duplicate asset id: {collection_id}/{asset_id}")

            file_rel = safe_relative_path(file_value, label=f"asset file {collection_id}/{asset_id}")
            source_path = manifest_path.parent / file_rel
            require_inside(signal_root, source_path, label=f"asset file {collection_id}/{asset_id}")
            index[key] = {
                "collection": collection_id,
                "id": asset_id,
                "source_path": source_path,
                "source_relative": source_path.relative_to(signal_root).as_posix(),
                "sha256": expected_hash,
            }
    return registry, index


def validate_consumer(data: dict[str, Any]) -> None:
    if data.get("schema_version") != "1.0.0":
        raise AssetRegistryError("unsupported consumer schema_version")
    repository = data.get("repository")
    if not isinstance(repository, str) or not repository.startswith("KAFKA2306/") or repository.count("/") != 1:
        raise AssetRegistryError("consumer repository must be KAFKA2306/<repo>")
    assets = data.get("assets")
    if not isinstance(assets, list) or not assets:
        raise AssetRegistryError("consumer assets must be a non-empty array")


def load_existing_lock(destination_root: Path) -> dict[str, Any] | None:
    lock_path = destination_root / LOCK_PATH
    if not lock_path.exists():
        return None
    return load_json(lock_path)


def prior_lock_by_destination(lock: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if lock is None:
        return {}
    records = lock.get("assets")
    if not isinstance(records, list):
        raise AssetRegistryError("existing Pages asset lock has invalid assets field")
    result: dict[str, dict[str, Any]] = {}
    for record in records:
        if isinstance(record, dict) and isinstance(record.get("destination"), str):
            result[record["destination"]] = record
    return result


def vendor_assets(
    *,
    signal_root: Path,
    destination_root: Path,
    consumer_manifest: Path,
    canonical_commit: str,
    dry_run: bool = False,
) -> dict[str, Any]:
    if not canonical_commit.strip():
        raise AssetRegistryError("canonical commit must be non-empty")

    registry, asset_index = load_asset_index(signal_root)
    consumer = load_json(consumer_manifest)
    validate_consumer(consumer)

    release_manifest_rel = safe_relative_path(registry.get("release_manifest"), label="release manifest")
    release_manifest_path = signal_root / release_manifest_rel
    require_inside(signal_root, release_manifest_path, label="release manifest")
    release_manifest = load_json(release_manifest_path)
    release = release_manifest.get("release")
    if not isinstance(release, str) or not release:
        raise AssetRegistryError("release manifest has no release value")

    previous = prior_lock_by_destination(load_existing_lock(destination_root))
    requested_destinations: set[str] = set()
    plan: list[dict[str, Any]] = []
    lock_records: list[dict[str, Any]] = []

    for request in consumer["assets"]:
        if not isinstance(request, dict):
            raise AssetRegistryError("consumer asset entries must be objects")
        collection = request.get("collection")
        asset_id = request.get("id")
        destination_value = request.get("destination")
        if not isinstance(collection, str) or not isinstance(asset_id, str):
            raise AssetRegistryError("consumer asset requires collection and id")
        destination_rel = safe_relative_path(destination_value, label=f"destination {collection}/{asset_id}")
        destination_key = destination_rel.as_posix()
        if destination_key in requested_destinations:
            raise AssetRegistryError(f"duplicate consumer destination: {destination_key}")
        requested_destinations.add(destination_key)

        asset = asset_index.get((collection, asset_id))
        if asset is None:
            raise AssetRegistryError(f"unknown asset: {collection}/{asset_id}")
        source_path = asset["source_path"]
        if not source_path.is_file():
            raise AssetRegistryError(f"canonical asset file is missing: {asset['source_relative']}")
        actual_source_hash = sha256_file(source_path)
        if actual_source_hash != asset["sha256"]:
            raise AssetRegistryError(
                f"canonical hash mismatch for {collection}/{asset_id}: "
                f"manifest={asset['sha256']} actual={actual_source_hash}"
            )

        destination_path = destination_root / destination_rel
        destination_path.parent.mkdir(parents=True, exist_ok=True) if not dry_run else None
        action = "copy"
        if destination_path.exists():
            if not destination_path.is_file():
                raise AssetRegistryError(f"destination is not a file: {destination_key}")
            current_hash = sha256_file(destination_path)
            prior = previous.get(destination_key)
            if prior is not None:
                locked_hash = prior.get("destination_sha256")
                if not isinstance(locked_hash, str) or current_hash != locked_hash:
                    raise AssetRegistryError(f"local modification detected: {destination_key}")
            elif current_hash != actual_source_hash:
                raise AssetRegistryError(f"unmanaged destination would be overwritten: {destination_key}")
            if current_hash == actual_source_hash:
                action = "unchanged"

        if action == "copy" and not dry_run:
            shutil.copy2(source_path, destination_path)

        record = {
            "collection": collection,
            "id": asset_id,
            "source": asset["source_relative"],
            "destination": destination_key,
            "source_sha256": actual_source_hash,
            "destination_sha256": actual_source_hash,
        }
        lock_records.append(record)
        plan.append({"action": action, **record})

    lock = {
        "schema_version": "1.0.0",
        "release": release,
        "canonical_repository": registry.get("canonical_repository"),
        "canonical_commit": canonical_commit,
        "consumer_repository": consumer["repository"],
        "assets": lock_records,
    }
    if not dry_run:
        lock_path = destination_root / LOCK_PATH
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        lock_path.write_text(json.dumps(lock, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return {"dry_run": dry_run, "plan": plan, "lock": lock}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True, help="Path to design-systems/kafka-signal")
    parser.add_argument("--destination", type=Path, required=True, help="Checked-out consumer repository root")
    parser.add_argument("--consumer-manifest", type=Path, required=True)
    parser.add_argument("--commit", required=True, help="Pinned prompt-vault commit SHA")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = vendor_assets(
            signal_root=args.source,
            destination_root=args.destination,
            consumer_manifest=args.consumer_manifest,
            canonical_commit=args.commit,
            dry_run=args.dry_run,
        )
    except AssetRegistryError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, **result}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
