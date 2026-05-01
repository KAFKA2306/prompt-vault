#!/usr/bin/env python3
from __future__ import annotations

import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from build import load_db  # noqa: E402


def group_by_prefix(items: list[dict[str, Any]], prefix: str) -> list[dict[str, Any]]:
    return [item for item in items if item["id"].startswith(prefix)]


def detect_family_duplicates(templates: list[dict[str, Any]]) -> list[str]:
    families: dict[str, list[str]] = defaultdict(list)
    for template in templates:
        template_id = template["id"]
        family = template_id.split("_", 1)[0]
        families[family].append(template_id)
    warnings: list[str] = []
    for family, ids in sorted(families.items()):
        if len(ids) < 3:
            continue
        if family in {"morning", "travel", "reading", "cosplay", "poker", "cardgame", "joinwars", "logo", "reply", "archive", "memory"}:
            warnings.append(f"family '{family}' has {len(ids)} templates: {', '.join(ids)}")
    return warnings


def main() -> int:
    db = load_db()

    blocks = db["blocks"]
    templates = db["templates"]

    block_categories = Counter(block.get("category", "") for block in blocks)
    template_kinds = Counter(template.get("kind", "") for template in templates)

    print(f"blocks: {len(blocks)}")
    print(f"templates: {len(templates)}")
    print(f"artifacts: {sum(len(template.get('artifacts', [])) for template in templates)}")
    print("block categories:")
    for category, count in block_categories.most_common():
        print(f"  {category}: {count}")
    print("template kinds:")
    for kind, count in template_kinds.most_common():
        print(f"  {kind}: {count}")

    warnings = detect_family_duplicates(templates)
    if warnings:
        print("warnings:")
        for warning in warnings:
            print(f"  - {warning}")
    else:
        print("warnings: none")

    artifact_paths = []
    for template in templates:
        for artifact in template.get("artifacts", []):
            artifact_paths.append(artifact["path"])

    duplicates = [path for path, count in Counter(artifact_paths).items() if count > 1]
    if duplicates:
        print("duplicate artifact paths:")
        for path in duplicates:
            print(f"  - {path}")
        return 1

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
