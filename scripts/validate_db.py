import sys
from collections import defaultdict

from _bootstrap import ROOT
from config import CONFIG
from src.db_io import load_prompt_db


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

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
