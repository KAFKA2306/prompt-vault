import sys

from pathlib import Path

from _bootstrap import ROOT

from config import CONFIG

CHECKS = CONFIG["audit_literals"]


def main() -> int:
    problems = []

    for rel_or_abs_path, needles in CHECKS.items():
        path = Path(rel_or_abs_path)
        if not path.is_absolute():
            path = ROOT / path

        if not path.exists():
            problems.append(f"missing file: {path}")
            continue

        content = path.read_text(encoding="utf-8")
        for needle in needles:
            if needle not in content:
                problems.append(f"missing literal in {path}: {needle}")

    if problems:
        for line in problems:
            sys.stderr.write(f"ERROR: {line}\n")
        return 1

    print("Literal audit: PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
