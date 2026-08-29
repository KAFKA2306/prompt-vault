from __future__ import annotations

import hashlib
import re
from pathlib import Path


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    if slug:
        return slug

    digest = hashlib.sha1(value.encode("utf-8")).hexdigest()[:8]
    return f"jp_{digest}"


def next_artifact_number(artifacts_path: Path) -> int:
    numbers: list[int] = []
    for path in artifacts_path.iterdir():
        if not path.is_file():
            continue
        match = re.match(r"^(\d{3})_", path.name)
        if match:
            numbers.append(int(match.group(1)))
    return max(numbers, default=0) + 1
