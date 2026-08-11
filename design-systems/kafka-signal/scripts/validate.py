#!/usr/bin/env python3
from pathlib import Path
import json
import sys

R = Path(__file__).resolve().parents[1]
errors = []

required = [
    "DESIGN.md",
    "USAGE.md",
    "tokens.json",
    "tokens.css",
    "tokens.schema.json",
    "components.html",
    "components.manifest.json",
    "voice.md",
    "anti-patterns.md",
    "icons/index.json",
    "icons/sprite.svg",
    "characters/kafka-character.json",
    "assets/provenance.json",
    "audit/input.schema.json",
    "audit/scorecard.schema.json",
    "audit/scoring-policy.json",
    "audit/README.md",
    "scripts/score.py",
    "tests/test_score.py",
]
for rel in required:
    if not (R / rel).is_file():
        errors.append("missing " + rel)


def load_json(rel):
    try:
        return json.loads((R / rel).read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"invalid json {rel}: {exc}")
        return None


tokens = load_json("tokens.json")
if tokens and tokens.get("meta", {}).get("version") != "1.0.0":
    errors.append("tokens version must be 1.0.0")

for rel in [
    "tokens.schema.json",
    "components.manifest.json",
    "audit/input.schema.json",
    "audit/scorecard.schema.json",
    "audit/scoring-policy.json",
    "audit/fixtures/high-score-unverified.json",
    "audit/fixtures/verified-s.json",
]:
    if (R / rel).is_file():
        load_json(rel)
    else:
        errors.append("missing " + rel)

policy = load_json("audit/scoring-policy.json") if (R / "audit/scoring-policy.json").is_file() else None
if policy:
    dimensions = policy.get("dimensions", [])
    if len(dimensions) != 8 or len(set(dimensions)) != 8:
        errors.append("scoring policy must define exactly 8 unique dimensions")
    thresholds = policy.get("thresholds", [])
    covered = []
    for row in thresholds:
        covered.extend(range(row.get("min", 1), row.get("max", -1) + 1))
    if sorted(covered) != list(range(41)):
        errors.append("scoring thresholds must cover every total from 0 to 40 exactly once")
    if set(policy.get("required_viewports", [])) != {360, 768, 1440}:
        errors.append("required viewports must be 360, 768, 1440")

for p in R.rglob("*.svg"):
    s = p.read_text(encoding="utf-8").lower()
    if "<script" in s or "onload=" in s:
        errors.append("unsafe svg " + str(p))

if errors:
    print("\n".join(errors), file=sys.stderr)
    raise SystemExit(1)
print("KAFKA SIGNAL validation passed")
