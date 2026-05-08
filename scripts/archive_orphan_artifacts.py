import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from build import load_db  # noqa: E402


def main() -> int:
    db = load_db()
    linked_paths = {artifact.path for template in db.templates for artifact in template.artifacts}
    artifacts_dir = ROOT / "artifacts"
    orphan_dir = artifacts_dir / "_orphaned"
    orphan_dir.mkdir(exist_ok=True)

    moved = 0
    for source in sorted(artifacts_dir.glob("*.png")):
        rel_path = f"artifacts/{source.name}"
        if rel_path in linked_paths:
            continue
        target = orphan_dir / source.name
        source.rename(target)
        zone_id = source.with_name(f"{source.name}:Zone.Identifier")
        if zone_id.exists():
            zone_id.rename(orphan_dir / zone_id.name)
        print(f"moved {source.name} -> artifacts/_orphaned/{source.name}")
        moved += 1

    print(f"Archived {moved} orphan artifacts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
