from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path
from xml.etree import ElementTree as ET

SVG_NS = "{http://www.w3.org/2000/svg}"
XLINK_HREF = "{http://www.w3.org/1999/xlink}href"


def _svg_dimension(value: str | None, label: str, path: Path) -> int:
    if not value or not re.fullmatch(r"[1-9][0-9]*", value):
        raise ValueError(f"{path}: {label} must be a positive integer without units")
    return int(value)


def _required_font_family(value: str, path: Path) -> str:
    family = value.split(",", 1)[0].strip().strip("'\"")
    if not family or family.lower() in {"serif", "sans-serif", "monospace", "cursive", "fantasy"}:
        raise ValueError(f"{path}: first font-family must be a concrete installed font")
    return family


def _validate_font_available(family: str, path: Path) -> None:
    fc_match = shutil.which("fc-match")
    if not fc_match:
        raise RuntimeError(f"{path}: fc-match is required to verify canonical SVG fonts")

    result = subprocess.run(
        [fc_match, "--format=%{family}\n", family],
        check=True,
        capture_output=True,
        text=True,
    )
    matched_families = {
        item.strip()
        for line in result.stdout.splitlines()
        for item in line.split(",")
        if item.strip()
    }
    if family not in matched_families:
        matched = ", ".join(sorted(matched_families)) or "none"
        raise ValueError(f"{path}: required font is not installed: {family} (matched: {matched})")


def validate_canonical_designs(designs_path: Path, repository_root: Path) -> None:
    if not designs_path.is_dir():
        raise FileNotFoundError(f"missing canonical designs directory: {designs_path}")

    designs = sorted(designs_path.glob("*.svg"))
    if not designs:
        raise ValueError(f"no canonical SVG designs found in {designs_path}")

    root_path = repository_root.resolve()
    verified_fonts: set[str] = set()
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
                font_family = element.get("font-family")
                if not font_family:
                    raise ValueError(f"{path}: every text element must declare font-family")
                required_font = _required_font_family(font_family, path)
                if required_font not in verified_fonts:
                    _validate_font_available(required_font, path)
                    verified_fonts.add(required_font)

            if element.tag == f"{SVG_NS}image":
                href = element.get("href") or element.get(XLINK_HREF)
                if not href:
                    raise ValueError(f"{path}: image element must declare href")
                if href.startswith(("http://", "https://", "data:")):
                    raise ValueError(f"{path}: image href must reference a repository asset: {href}")
                asset = (path.parent / href).resolve()
                if not asset.is_relative_to(root_path) or not asset.is_file():
                    raise ValueError(f"{path}: missing or invalid image reference: {href}")

        if text_count == 0:
            raise ValueError(f"{path}: canonical design must contain at least one text element")
