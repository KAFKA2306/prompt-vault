import sys
from collections import defaultdict

from _bootstrap import ROOT

from config import CONFIG
from src.db_io import load_prompt_db


def main() -> int:
    db = load_prompt_db(ROOT / CONFIG["paths"]["db"])

    root_artifacts = ROOT / CONFIG["paths"]["artifacts"]
    orphaned_artifacts = ROOT / CONFIG["paths"]["orphaned_artifacts"]

    linked_paths = defaultdict(list)
    for template in db.templates:
        for artifact in template.artifacts:
            linked_paths[artifact.path].append(template.id)

    root_pngs = {f"artifacts/{path.name}" for path in root_artifacts.glob("*.png")}
    orphaned_pngs = {f"artifacts/_orphaned/{path.name}" for path in orphaned_artifacts.glob("*.png")}

    root_unlinked = sorted(root_pngs - set(linked_paths))
    missing_linked = sorted(set(linked_paths) - root_pngs)
    orphaned_still_linked = sorted(path for path in linked_paths if path.startswith("artifacts/_orphaned/"))

    duplicate_links = {path: owners for path, owners in linked_paths.items() if len(owners) > 1}

    print("--- Artifact Audit Report ---")
    print(f"Root PNGs: {len(root_pngs)}")
    print(f"Linked PNGs: {len(linked_paths)}")
    print(f"Orphaned PNGs: {len(orphaned_pngs)}")
    print()

    if root_unlinked:
        print("--- 未接続PNG (root artifacts/) ---")
        for path in root_unlinked:
            print(path)
        print()

    if missing_linked:
        print("--- DB参照あり・ファイルなし ---")
        for path in missing_linked:
            print(path)
        print()

    if orphaned_still_linked:
        print("--- _orphaned にあるが DB 参照あり ---")
        for path in orphaned_still_linked:
            print(path)
        print()

    if duplicate_links:
        print("--- 重複参照 ---")
        for path, owners in sorted(duplicate_links.items()):
            print(f"{path}: {owners}")
        print()

    problems = bool(root_unlinked or missing_linked or orphaned_still_linked or duplicate_links)
    print("Artifact audit:", "FAILED" if problems else "PASSED")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
