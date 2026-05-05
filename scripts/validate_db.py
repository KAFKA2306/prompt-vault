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

EXPECTED_TEMPLATE_FAMILIES = {"post", "sheet", "banner", "brand", "reply", "comic", "system", "generated", "news"}


def detect_family_issues(templates: list[dict[str, Any]]) -> list[str]:
    warnings: list[str] = []
    for template in templates:
        family = template.get("family")
        if not family:
            warnings.append(f"template '{template['id']}' is missing family")
            continue
        if family not in EXPECTED_TEMPLATE_FAMILIES:
            warnings.append(f"template '{template['id']}' has unexpected family '{family}'")
    return warnings


def main() -> int:
    db = load_db()

    blocks = db["blocks"]
    templates = db["templates"]

    block_categories = Counter(block.get("category", "") for block in blocks)
    block_families = Counter(block.get("family", "") for block in blocks)
    template_kinds = Counter(template.get("kind", "") for template in templates)
    template_families = Counter(template.get("family", "") for template in templates)

    for _family, _count in block_families.most_common():
        pass
    for _category, _count in block_categories.most_common():
        pass
    for _family, _count in template_families.most_common():
        pass
    for _kind, _count in template_kinds.most_common():
        pass

    warnings = detect_family_issues(templates)
    if warnings:
        for _warning in warnings:
            pass
    else:
        pass

    artifact_paths: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for template in templates:
        for artifact in template.get("artifacts", []):
            artifact_paths[artifact["path"]].append(template)

    duplicates = []
    for path, owners in artifact_paths.items():
        visible_owners = [
            template
            for template in owners
            if template.get("kind") != "generated" and template.get("visibility") != "internal"
        ]
        if len(visible_owners) > 1:
            duplicates.append(path)
    if duplicates:
        for path in duplicates:
            pass
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
