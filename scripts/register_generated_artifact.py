import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "db" / "prompts.json"
ARTIFACTS_PATH = ROOT / "artifacts"


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return slug or "artifact"


def next_artifact_number() -> int:
    numbers: list[int] = []
    for path in ARTIFACTS_PATH.glob("*.png"):
        match = re.match(r"^(\d{3})_", path.name)
        if match:
            numbers.append(int(match.group(1)))
    return max(numbers, default=0) + 1


def next_template_id(existing_ids: set[str]) -> str:
    base = datetime.now().strftime("gen_%Y%m%d_%H%M%S")
    candidate = base
    suffix = 2
    while candidate in existing_ids:
        candidate = f"{base}_{suffix}"
        suffix += 1
    return candidate


def parse_blocks(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description="Register a generated image into artifacts/ and db/prompts.json.")
    parser.add_argument("--source", required=True, help="Source PNG to register")
    parser.add_argument("--title", required=True, help="Template title and default artifact title")
    parser.add_argument("--artifact-title", default=None, help="Artifact display title")
    parser.add_argument("--purpose", default="", help="Template purpose")
    parser.add_argument("--summary", default="", help="Template summary")
    parser.add_argument("--generated-prompt", default=None, help="Generated prompt text")
    parser.add_argument("--kind", default="generated", help="Template kind")
    parser.add_argument("--blocks", default="", help="Comma-separated block IDs")
    parser.add_argument("--skip-build", action="store_true", help="Skip build and validation")
    args = parser.parse_args()

    source = Path(args.source).expanduser().resolve()
    if not source.exists():
        sys.stderr.write(f"ERROR: source not found: {source}\n")
        return 1
    if source.suffix.lower() != ".png":
        sys.stderr.write("ERROR: source must be a .png file\n")
        return 1

    ARTIFACTS_PATH.mkdir(exist_ok=True)
    artifact_name = f"{next_artifact_number():03d}_{slugify(args.title)}.png"
    destination = ARTIFACTS_PATH / artifact_name
    if destination.exists():
        sys.stderr.write(f"ERROR: destination already exists: {destination}\n")
        return 1

    shutil.copy2(source, destination)

    with DB_PATH.open("r", encoding="utf-8") as f:
        db = json.load(f)

    templates = db.setdefault("templates", [])
    existing_ids = {t.get("id") for t in templates if isinstance(t, dict) and t.get("id")}
    template_id = next_template_id(existing_ids)
    artifact_title = args.artifact_title or args.title

    templates.append(
        {
            "id": template_id,
            "title": args.title,
            "blocks": parse_blocks(args.blocks),
            "kind": args.kind,
            "purpose": args.purpose,
            "summary": args.summary,
            "artifacts": [
                {
                    "path": f"artifacts/{destination.name}",
                    "title": artifact_title,
                }
            ],
            "generated_prompt": args.generated_prompt,
            "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        }
    )

    with DB_PATH.open("w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
        f.write("\n")

    if not args.skip_build:
        subprocess.run([sys.executable, "build.py"], cwd=ROOT, check=True)
        subprocess.run([sys.executable, "scripts/validate_db.py"], cwd=ROOT, check=True)

    print(f"Registered {destination}")
    print(f"Template id: {template_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
