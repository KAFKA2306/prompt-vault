from __future__ import annotations

import argparse
import subprocess
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIB = 1024 * 1024


def tracked_files() -> list[tuple[str, int]]:
    raw = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
    rows: list[tuple[str, int]] = []
    for item in raw.decode().split("\0"):
        if not item:
            continue
        path = ROOT / item
        if not path.is_file():
            raise FileNotFoundError(f"tracked file is missing from checkout: {item}")
        rows.append((item, path.stat().st_size))
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-bytes", type=int)
    parser.add_argument("--max-file-bytes", type=int)
    parser.add_argument("--top", type=int, default=20)
    args = parser.parse_args()

    rows = tracked_files()
    total = sum(size for _, size in rows)
    by_root: dict[str, int] = defaultdict(int)
    for path, size in rows:
        by_root[path.split("/", 1)[0]] += size

    print(f"tracked_files={len(rows)}")
    print(f"tracked_bytes={total}")
    print(f"tracked_mib={total / MIB:.2f}")
    print("top_level_mib:")
    for name, size in sorted(by_root.items(), key=lambda item: item[1], reverse=True):
        print(f"  {name}: {size / MIB:.2f}")
    print("largest_files:")
    for path, size in sorted(rows, key=lambda item: item[1], reverse=True)[: args.top]:
        print(f"  {size / MIB:.2f} MiB\t{path}")

    failures: list[str] = []
    if args.max_bytes is not None and total > args.max_bytes:
        failures.append(f"tracked tree {total} bytes exceeds {args.max_bytes}")
    if args.max_file_bytes is not None:
        oversized = [(path, size) for path, size in rows if size > args.max_file_bytes]
        if oversized:
            failures.append(
                f"{len(oversized)} tracked files exceed {args.max_file_bytes} bytes"
            )

    for failure in failures:
        print(f"ERROR: {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
