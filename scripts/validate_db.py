import sys
from collections import defaultdict

from _bootstrap import ROOT
from config import CONFIG
from src.designs import validate_canonical_designs
from src.prompt_db import load_prompt_db

LEGACY_SRC_IMPORTS = (
    "src." + "models",
    "src." + "db_io",
    "src." + "artifact_ops",
    "src." + "skills_index",
)


def validate_no_legacy_src_imports() -> None:
    for path in ROOT.rglob("*.py"):
        if any(part in {"dist", ".venv", "__pycache__"} for part in path.parts):
            continue
        content = path.read_text(encoding="utf-8")
        for legacy_import in LEGACY_SRC_IMPORTS:
            if legacy_import in content:
                raise ValueError(f"{path}: legacy src import is forbidden: {legacy_import}")


def main() -> int:
    validate_no_legacy_src_imports()
    db = load_prompt_db(ROOT / CONFIG["paths"]["db"])

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

    actual_files = {f"artifacts/{f.name}" for f in (ROOT / CONFIG["paths"]["artifacts"]).iterdir() if f.is_file()}
    orphans = actual_files - linked_paths
    if orphans:
        for orphan in sorted(orphans):
            sys.stderr.write(f"WARNING: orphaned artifact: {orphan}\n")

    validate_canonical_designs(ROOT / "designs", ROOT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
