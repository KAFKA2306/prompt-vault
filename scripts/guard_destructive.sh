#!/usr/bin/env bash
set -euo pipefail

TS="$(date +%Y%m%d-%H%M%S)"
RUN_DIR="runs/destructive_guard/$TS"
mkdir -p "$RUN_DIR"

git status --porcelain=v1 > "$RUN_DIR/git_status.txt"
git ls-files --others --exclude-standard > "$RUN_DIR/untracked.txt"
git diff --name-only > "$RUN_DIR/modified.txt"
git clean -fdn > "$RUN_DIR/git_clean_dry_run.txt"

: > "$RUN_DIR/image_candidates.txt"
for dir in artifacts dist/artifacts generated tmp; do
  if [[ -d "$dir" ]]; then
    find "$dir" -type f \
      \( -name "*.png" -o -name "*.webp" -o -name "*.jpg" -o -name "*.jpeg" \) \
      >> "$RUN_DIR/image_candidates.txt"
  fi
done

awk '/\.(png|webp|jpg|jpeg)$/' "$RUN_DIR/untracked.txt" \
  > "$RUN_DIR/untracked_images.txt"

if grep -q '^db/prompts.json$' "$RUN_DIR/modified.txt"; then
  echo "FAIL: db/prompts.json is modified. Evidence: $RUN_DIR"
  exit 1
fi

if [[ -s "$RUN_DIR/untracked_images.txt" ]]; then
  echo "FAIL: untracked image artifacts exist. Evidence: $RUN_DIR"
  cat "$RUN_DIR/untracked_images.txt"
  exit 1
fi

if [[ -s "$RUN_DIR/git_clean_dry_run.txt" ]]; then
  echo "BLOCKED: git clean would remove files. Evidence: $RUN_DIR"
  cat "$RUN_DIR/git_clean_dry_run.txt"
  exit 1
fi

echo "PASS: destructive preflight clear. Evidence: $RUN_DIR"
