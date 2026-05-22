import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = ROOT / "config/audit.yaml"


def load_audit_config():
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


def validate_structure() -> None:
    config = load_audit_config()
    errors = []

    for item in config.get("canonical_files", []):
        p = ROOT / item["path"]
        if item["required"] and not p.exists():
            errors.append(f"MISSING_CANONICAL: {item['path']}")

    for path in config.get("required_paths", []):
        if not (ROOT / path).exists():
            errors.append(f"MISSING_PATH: {path}")

    forbidden = config.get("forbidden_patterns", [])
    for pattern in forbidden:
        for p in ROOT.glob(pattern):
            if p.is_file():
                errors.append(f"FORBIDDEN_PATH: {p.relative_to(ROOT)}")

    if errors:
        for _e in errors:
            pass
        sys.exit(1)


if __name__ == "__main__":
    validate_structure()
