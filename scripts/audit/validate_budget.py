import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = ROOT / "config/audit.yaml"


def load_audit_config():
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


def validate_budget() -> None:
    config = load_audit_config()
    budgets = config.get("budgets", {})

    file_count = sum(
        1
        for _ in ROOT.rglob("*")
        if _.is_file()
        and not any(p.startswith((".", "twitter-")) or p in {"node_modules", "dist"} for p in _.parts)
    )
    max_files = budgets.get("max_files_scanned", 5000)

    if file_count > max_files:
        sys.exit(1)



if __name__ == "__main__":
    validate_budget()
