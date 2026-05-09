from __future__ import annotations

import re
from pathlib import Path


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return slug or "artifact"


def next_artifact_number(artifacts_path: Path) -> int:
    numbers: list[int] = []
    for path in artifacts_path.glob("*.png"):
        match = re.match(r"^(\d{3})_", path.name)
        if match:
            numbers.append(int(match.group(1)))
    return max(numbers, default=0) + 1
