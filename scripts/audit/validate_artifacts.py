import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent


def validate_artifacts() -> None:
    result = subprocess.run(["python3", str(ROOT / "scripts/audit_artifacts.py")], check=False, capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit(1)


if __name__ == "__main__":
    validate_artifacts()
