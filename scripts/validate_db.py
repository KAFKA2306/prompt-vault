import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from build import load_db  # noqa: E402


def main() -> int:
    db = load_db()
    artifact_paths = defaultdict(list)
    for template in db.templates:
        for artifact in template.artifacts:
            artifact_paths[artifact.path].append(template)

    duplicates = [
        path for path, owners in artifact_paths.items() if len([t for t in owners if t.kind != "generated"]) > 1
    ]
    if duplicates:
        for path in duplicates:
            sys.stderr.write(f"ERROR: duplicate artifact path: {path}\n")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
