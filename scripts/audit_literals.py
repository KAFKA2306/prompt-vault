import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CHECKS = {
    "AGENTS.md": [
        "/home/kafka/.codex/generated_images/",
        "artifacts/NNN_slug.png",
        "character_kafka",
        "kafka_identity_lock",
    ],
    "README.md": [
        "/home/kafka/.codex/generated_images/",
        "character_kafka",
        "kafka_identity_lock",
    ],
    "docs/SCHEMA.md": [
        "/home/kafka/.codex/generated_images/",
        "artifacts/NNN_slug.png",
        "artifacts/_orphaned/",
        "character_kafka",
        "kafka_identity_lock",
    ],
    "docs/ADR/0011-artifact-graph-connectivity.md": [
        "/home/kafka/.codex/generated_images/",
        "artifacts/NNN_slug.png",
        "character_kafka",
        "kafka_identity_lock",
    ],
    "docs/ADR/0014-webp-optimization.md": [
        "/home/kafka/projects/prompt-vault/artifacts/NNN_slug.png",
        "/home/kafka/projects/prompt-vault/dist/artifacts/NNN_slug.webp",
        "db/prompts.json",
    ],
    "docs/ADR/0018-unconnected-png-reconnect-workflow.md": [
        "/home/kafka/.codex/generated_images/",
        "artifacts/_orphaned/",
        "character_kafka",
        "kafka_identity_lock",
    ],
    ".agents/skills/prompt-vault-workflow/SKILL.md": [
        "/home/kafka/.codex/generated_images/",
        "artifacts/NNN_slug.png",
        "character_kafka",
        "kafka_identity_lock",
    ],
    ".agents/skills/prompt-db-guard/SKILL.md": [
        "/home/kafka/.codex/generated_images/",
        "artifacts/NNN_slug.png",
        "artifacts/_orphaned/",
        "character_kafka",
        "kafka_identity_lock",
    ],
    "/home/kafka/projects/.agent/skills/.system/imagegen/SKILL.md": [
        "/home/kafka/.codex/generated_images/",
        "/home/kafka/projects/prompt-vault/artifacts/NNN_slug.png",
        "/home/kafka/projects/prompt-vault/db/prompts.json",
        "/home/kafka/projects/prompt-vault/artifacts/_orphaned/",
        "character_kafka",
        "character_kafka_soft_reference",
        "kafka_identity_lock",
    ],
}


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
