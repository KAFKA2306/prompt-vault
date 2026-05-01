#!/usr/bin/env bash
set -euo pipefail

gh_url="${GH_PAGES_URL:-https://kafka2306.github.io/prompt-vault/}"
cf_url="${CF_PAGES_URL:-}"

check_url() {
  local label="$1"
  local url="$2"

  echo "check: $label $url"
  body="$(curl -fsSL "$url")"
  printf '%s' "$body" | grep -q "Prompt Vault"
  echo "ok: $label"
}

check_url "github-pages" "$gh_url"

if [ -n "$cf_url" ]; then
  check_url "cloudflare-pages" "$cf_url"
else
  echo "skip: cloudflare-pages (set CF_PAGES_URL to verify)"
fi
