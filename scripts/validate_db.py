import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import CONFIG, root_path

from build import load_db  # noqa: E402


def main() -> int:
    db = load_db()

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
    actual_files = {f"artifacts/{f.name}" for f in root_path(CONFIG["paths"]["artifacts"]).glob("*.png")}
    orphans = actual_files - linked_paths
    if orphans:
        for o in sorted(orphans):
            sys.stderr.write(f"WARNING: orphaned artifact: {o}\n")
        # NOTE: Not returning 1 yet to allow build, but reporting clearly.

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
