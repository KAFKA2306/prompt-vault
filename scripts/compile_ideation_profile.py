#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from _bootstrap import ROOT
from src.ideation import compile_ideation_profile


def main() -> int:
    parser = argparse.ArgumentParser(description="Compile a compact Kafka ideation profile from tweetsdb.")
    parser.add_argument("--source", type=Path, default=ROOT / "db" / "tweetsdb.json")
    parser.add_argument("--output", type=Path, default=ROOT / "dist" / "data" / "ideation_profile.json")
    parser.add_argument("--max-exemplars", type=int, default=120)
    args = parser.parse_args()

    payload = compile_ideation_profile(args.source, args.output, max_exemplars=args.max_exemplars)
    print(
        f"wrote {args.output} "
        f"({payload['meta']['source_record_count']} source records, "
        f"{payload['meta']['exemplar_count']} exemplars)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
