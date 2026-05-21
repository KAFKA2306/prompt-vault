#!/usr/bin/env bash
set -euo pipefail

TS="$(date +%Y%m%d-%H%M%S)"
RUN_DIR="runs/destructive_guard/$TS"
mkdir -p "$RUN_DIR"

git status --porcelain=v1 > "$RUN_DIR/git_status.txt"
git ls-files --others --exclude-standard > "$RUN_DIR/untracked.txt"
git diff --name-only > "$RUN_DIR/modified.txt"

find artifacts dist/artifacts generated tmp -type f \
  \( -name "*.png" -o -name "*.webp" -o -name "*.jpg" -o -name "*.jpeg" \) \
  2>/dev/null > "$RUN_DIR/image_candidates.txt" || true

grep -E '\.(png|webp|jpg|jpeg)$' "$RUN_DIR/untracked.txt" \
  > "$RUN_DIR/untracked_images.txt" || true

if grep -q '^db/prompts.json$' "$RUN_DIR/modified.txt"; then
  echo "FAIL: db/prompts.json is modified. Evidence: $RUN_DIR"
  exit 1
fi

if [ -s "$RUN_DIR/untracked_images.txt" ]; then
  echo "FAIL: untracked image artifacts exist. Evidence: $RUN_DIR"
  cat "$RUN_DIR/untracked_images.txt"
  exit 1
fi

echo "PASS: destructive preflight clear. Evidence: $RUN_DIR"
