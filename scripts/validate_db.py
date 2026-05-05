import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from build import load_db  # noqa: E402
from src.models import PromptDB  # noqa: E402

EXPECTED_TEMPLATE_FAMILIES = {"post", "sheet", "banner", "brand", "reply", "comic", "system", "generated", "news"}


def detect_family_issues(db: PromptDB) -> list[str]:
    warnings: list[str] = []
    for template in db.templates:
        if not template.family:
            warnings.append(f"template '{template.id}' is missing family")
            continue
        if template.family not in EXPECTED_TEMPLATE_FAMILIES:
            warnings.append(f"template '{template.id}' has unexpected family '{template.family}'")
    return warnings


def main() -> int:
    db = load_db()
    warnings = detect_family_issues(db)
    if warnings:
        for w in warnings:
            sys.stderr.write(f"WARNING: {w}\n")

    artifact_paths = defaultdict(list)
    for template in db.templates:
        for artifact in template.artifacts:
            artifact_paths[artifact.path].append(template)

    duplicates = []
    for path, owners in artifact_paths.items():
        visible_owners = [t for t in owners if t.kind != "generated" and t.visibility != "internal"]
        if len(visible_owners) > 1:
            duplicates.append(path)

    if duplicates:
        for path in duplicates:
            sys.stderr.write(f"ERROR: duplicate artifact path used by multiple templates: {path}\n")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
