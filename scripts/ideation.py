#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from _bootstrap import ROOT
from src.ideation import load_ideation_profile, retrieve_ideation


def main() -> int:
    parser = argparse.ArgumentParser(description="Retrieve evidence-backed Kafka ideation examples.")
    parser.add_argument("query", help="What you want to ideate from")
    parser.add_argument("--profile", type=Path, default=ROOT / "dist" / "data" / "ideation_profile.json")
    parser.add_argument("--topic", default=None)
    parser.add_argument("--mood", default=None)
    parser.add_argument("--function", default=None)
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()

    if not args.profile.is_file():
        raise FileNotFoundError(
            f"compiled ideation profile not found: {args.profile}; run `task build` first"
        )

    payload = load_ideation_profile(args.profile)
    result = retrieve_ideation(
        payload,
        args.query,
        topic=args.topic,
        mood=args.mood,
        function=args.function,
        limit=args.limit,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
