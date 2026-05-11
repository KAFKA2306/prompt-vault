import argparse
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from _bootstrap import ROOT

from config import CONFIG
from src.db_io import load_json_db, save_json_db
from src.artifact_ops import next_artifact_number, slugify

DB_PATH = ROOT / CONFIG["paths"]["db"]
ARTIFACTS_PATH = ROOT / CONFIG["paths"]["artifacts"]


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
    parser = argparse.ArgumentParser(description="Register a generated artifact into artifacts/ and db/prompts.json.")
    parser.add_argument("--source", required=True, help="Source PNG or WAV to register")
    parser.add_argument("--title", required=True, help="Template title and default artifact title")
    parser.add_argument("--artifact-title", default=None, help="Artifact display title")
    parser.add_argument("--purpose", default="", help="Template purpose")
    parser.add_argument("--summary", default="", help="Template summary")
    parser.add_argument("--generated-prompt", default=None, help="Generated prompt text")
    parser.add_argument("--kind", default="generated", help="Template kind")
    parser.add_argument("--blocks", default="", help="Comma-separated block IDs")
    parser.add_argument("--voice-caption", default=None, help="Voice caption/description")
    parser.add_argument("--voice-script", default=None, help="Voice script/text")
    parser.add_argument("--skip-build", action="store_true", help="Skip build and validation")
    args = parser.parse_args()

    source = Path(args.source).expanduser().resolve()
    if not source.exists():
        sys.stderr.write(f"ERROR: source not found: {source}\n")
        return 1
    if source.suffix.lower() not in {".png", ".wav"}:
        sys.stderr.write("ERROR: source must be a .png or .wav file\n")
        return 1

    ARTIFACTS_PATH.mkdir(exist_ok=True)
    artifact_name = f"{next_artifact_number(ARTIFACTS_PATH):03d}_{slugify(args.title)}{source.suffix.lower()}"
    destination = ARTIFACTS_PATH / artifact_name
    if destination.exists():
        sys.stderr.write(f"ERROR: destination already exists: {destination}\n")
        return 1

    shutil.copy2(source, destination)

    db = load_json_db(DB_PATH)

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
            "voice_caption": args.voice_caption,
            "voice_script": args.voice_script,
            "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        }
    )

    save_json_db(DB_PATH, db)

    if not args.skip_build:
        subprocess.run([sys.executable, "build.py"], cwd=ROOT, check=True)
        subprocess.run([sys.executable, "scripts/validate_db.py"], cwd=ROOT, check=True)

    print(f"Registered {destination}")
    print(f"Template id: {template_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
