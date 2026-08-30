import re
import sys
from pathlib import Path

from _bootstrap import ROOT
from config import CONFIG

CHECKS = CONFIG["audit_literals"]
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def _resolve_document_path(rel_or_abs_path: str) -> Path:
    path = Path(rel_or_abs_path)
    return path if path.is_absolute() else ROOT / path


def _validate_local_markdown_links(path: Path) -> list[str]:
    if path.suffix.lower() != ".md":
        return []

    problems = []
    content = path.read_text(encoding="utf-8")
    for raw_target in MARKDOWN_LINK.findall(content):
        target = raw_target.strip()
        if target.startswith(("#", "http://", "https://", "mailto:")):
            continue

        target_path = target.split("#", 1)[0]
        if not target_path:
            continue

        resolved = (path.parent / target_path).resolve()
        if not resolved.is_relative_to(ROOT.resolve()):
            problems.append(f"documentation link escapes repository in {path}: {target}")
        elif not resolved.exists():
            problems.append(f"broken documentation link in {path}: {target}")
    return problems


def main() -> int:
    problems = []

    for rel_or_abs_path, needles in CHECKS.items():
        path = _resolve_document_path(rel_or_abs_path)

        if not path.exists():
            problems.append(f"missing file: {path}")
            continue

        content = path.read_text(encoding="utf-8")
        for needle in needles:
            if needle not in content:
                problems.append(f"missing literal in {path}: {needle}")

        problems.extend(_validate_local_markdown_links(path))

    if problems:
        for line in problems:
            sys.stderr.write(f"ERROR: {line}\n")
        return 1

    print("Documentation anchor audit: PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
