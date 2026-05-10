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

    root_files = {f"artifacts/{path.name}" for path in root_artifacts.iterdir() if path.is_file()}
    orphaned_files = {
        f"artifacts/_orphaned/{path.name}" for path in orphaned_artifacts.iterdir() if path.is_file()
    }

    root_unlinked = sorted(root_files - set(linked_paths))
    missing_linked = sorted(set(linked_paths) - root_files)
    orphaned_still_linked = sorted(path for path in linked_paths if path.startswith("artifacts/_orphaned/"))

    duplicate_links = {path: owners for path, owners in linked_paths.items() if len(owners) > 1}

    print("--- Artifact Audit Report ---")
    print(f"Root files: {len(root_files)}")
    print(f"Linked PNGs: {len(linked_paths)}")
    print(f"Orphaned files: {len(orphaned_files)}")
    print()

    if root_unlinked:
        print("--- 未接続ファイル (root artifacts/) ---")
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
