import re
import sys
from collections import defaultdict
from pathlib import Path
from xml.etree import ElementTree as ET

from _bootstrap import ROOT
from config import CONFIG
from src.db_io import load_prompt_db

SVG_NS = "{http://www.w3.org/2000/svg}"
XLINK_HREF = "{http://www.w3.org/1999/xlink}href"
DESIGNS_PATH = ROOT / "designs"


def _svg_dimension(value: str | None, label: str, path: Path) -> int:
    if not value or not re.fullmatch(r"[1-9][0-9]*", value):
        raise ValueError(f"{path}: {label} must be a positive integer without units")
    return int(value)


def validate_canonical_designs() -> None:
    if not DESIGNS_PATH.is_dir():
        raise FileNotFoundError(f"missing canonical designs directory: {DESIGNS_PATH}")

    designs = sorted(DESIGNS_PATH.glob("*.svg"))
    if not designs:
        raise ValueError(f"no canonical SVG designs found in {DESIGNS_PATH}")

    for path in designs:
        root = ET.parse(path).getroot()
        if root.tag != f"{SVG_NS}svg":
            raise ValueError(f"{path}: root element must be SVG")

        width = _svg_dimension(root.get("width"), "width", path)
        height = _svg_dimension(root.get("height"), "height", path)
        if root.get("viewBox") != f"0 0 {width} {height}":
            raise ValueError(f"{path}: viewBox must exactly match width/height")

        ids: set[str] = set()
        text_count = 0
        for element in root.iter():
            element_id = element.get("id")
            if element_id:
                if element_id in ids:
                    raise ValueError(f"{path}: duplicate id: {element_id}")
                ids.add(element_id)

            if element.tag == f"{SVG_NS}text":
                text_count += 1
                if not element.get("font-family"):
                    raise ValueError(f"{path}: every text element must declare font-family")

            if element.tag == f"{SVG_NS}image":
                href = element.get("href") or element.get(XLINK_HREF)
                if not href:
                    raise ValueError(f"{path}: image element must declare href")
                if href.startswith(("http://", "https://", "data:")):
                    raise ValueError(f"{path}: image href must reference a repository asset: {href}")
                asset = (path.parent / href).resolve()
                if not asset.is_relative_to(ROOT.resolve()) or not asset.is_file():
                    raise ValueError(f"{path}: missing or invalid image reference: {href}")

        if text_count == 0:
            raise ValueError(f"{path}: canonical design must contain at least one text element")


def main() -> int:
    db = load_prompt_db(ROOT / CONFIG["paths"]["db"])

    # Check for duplicate artifact paths
    artifact_paths = defaultdict(list)
    linked_paths = set()
    for template in db.templates:
        for artifact in template.artifacts:
            artifact_paths[artifact.path].append(template)
            linked_paths.add(artifact.path)

    duplicates = [
        path for path, owners in artifact_paths.items() if len([t for t in owners if t.kind != "generated"]) > 1
    ]
    if duplicates:
        for path in duplicates:
            sys.stderr.write(f"ERROR: duplicate artifact path: {path}\n")
        return 1

    # Check for orphaned artifacts
    actual_files = {f"artifacts/{f.name}" for f in (ROOT / CONFIG["paths"]["artifacts"]).iterdir() if f.is_file()}
    orphans = actual_files - linked_paths
    if orphans:
        for o in sorted(orphans):
            sys.stderr.write(f"WARNING: orphaned artifact: {o}\n")
        # NOTE: Not returning 1 yet to allow build, but reporting clearly.

    validate_canonical_designs()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
