from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from _bootstrap import ROOT


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Postrun wrapper for imagegen: register a generated PNG into artifacts/ and db/prompts.json."
    )
    parser.add_argument("--source", required=True, help="Generated PNG to register")
    parser.add_argument("--title", required=True, help="Template title and default artifact title")
    parser.add_argument("--artifact-title", default=None, help="Artifact display title")
    parser.add_argument("--purpose", default="", help="Template purpose")
    parser.add_argument("--summary", default="", help="Template summary")
    parser.add_argument("--generated-prompt", default=None, help="Generated prompt text")
    parser.add_argument("--kind", default="generated", help="Template kind")
    parser.add_argument("--blocks", default="", help="Comma-separated block IDs")
    parser.add_argument("--voice-caption", default=None, help="Voice caption/description")
    parser.add_argument("--voice-script", default=None, help="Voice script/text")
    args = parser.parse_args()

    source = Path(args.source).expanduser().resolve()
    if not source.exists():
        sys.stderr.write(f"ERROR: source not found: {source}\n")
        return 1
    if not source.is_file():
        sys.stderr.write(f"ERROR: source is not a file: {source}\n")
        return 1
    if source.suffix.lower() != ".png":
        sys.stderr.write("ERROR: source must be a .png file\n")
        return 1

    command = [
        sys.executable,
        str(ROOT / "scripts/artifacts/register_generated_artifact.py"),
        "--source",
        str(source),
        "--title",
        args.title,
        "--kind",
        args.kind,
        "--blocks",
        args.blocks,
    ]
    if args.artifact_title:
        command.extend(["--artifact-title", args.artifact_title])
    if args.purpose:
        command.extend(["--purpose", args.purpose])
    if args.summary:
        command.extend(["--summary", args.summary])
    if args.generated_prompt:
        command.extend(["--generated-prompt", args.generated_prompt])
    if args.voice_caption:
        command.extend(["--voice-caption", args.voice_caption])
    if args.voice_script:
        command.extend(["--voice-script", args.voice_script])

    result = subprocess.run(command, cwd=ROOT)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
