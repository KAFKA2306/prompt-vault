#!/usr/bin/env bash
set -euo pipefail

# Run general preflight check
./scripts/guard_destructive.sh

TS="$(date +%Y%m%d-%H%M%S)"
RUN_DIR="runs/destructive_guard/$TS"
mkdir -p "$RUN_DIR"

# Explicitly use -n (dry-run) and capture output
git clean -fdn > "$RUN_DIR/git_clean_dry_run.txt"

if [ ! -s "$RUN_DIR/git_clean_dry_run.txt" ]; then
  echo "PASS: no files would be removed."
  exit 0
fi

echo "BLOCKED: git clean would remove files. Evidence: $RUN_DIR"
cat "$RUN_DIR/git_clean_dry_run.txt"
exit 1
