#!/usr/bin/env bash
set -euo pipefail

repo="${WEEKLY_POWER_MACRO_REPO:-${WEEKLY_MACRO_REPO:-${GITHUB_REPOSITORY:-KAFKA2306/prompt-vault}}}"
publish_raw="${PUBLISH_WEEKLY_POWER_MACRO:-${PUBLISH_WEEKLY_MACRO:-true}}"
case "$publish_raw" in
  true|1|yes|on) publish="true" ;;
  false|0|no|off) publish="false" ;;
  *)
    echo "invalid publish setting: $publish_raw" >&2
    exit 2
    ;;
esac
agy_timeout="${AGY_TIMEOUT_SECONDS:-1800}"
prompt_max_bytes="${PROMPT_MAX_BYTES:-120000}"
week_end="$(date +%F)"
start=""
end=""
backfill_start=""
backfill_end=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --week-end)
      week_end="$2"
      shift 2
      ;;
    --start)
      start="$2"
      shift 2
      ;;
    --end)
      end="$2"
      shift 2
      ;;
    --backfill-start)
      backfill_start="$2"
      shift 2
      ;;
    --backfill-end)
      backfill_end="$2"
      shift 2
      ;;
    --repo)
      repo="$2"
      shift 2
      ;;
    --no-publish)
      publish="false"
      shift
      ;;
    *)
      echo "unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

if ! command -v agy >/dev/null 2>&1; then
  echo "agy not found in PATH" >&2
  exit 1
fi
if [[ "$publish" == "true" ]]; then
  if [[ -z "$repo" ]]; then
    echo "repo is required when publishing" >&2
    exit 2
  fi
  if ! command -v gh >/dev/null 2>&1; then
    echo "gh not found in PATH while publishing is enabled" >&2
    exit 1
  fi
fi

run_one() {
  local d="$1"
  local s="${2:-}"
  local e="${3:-$1}"
  local out_dir="outputs/weekly-power-macro-intelligence/$d"
  local docs_dir="docs/reports/weekly-power-macro-intelligence"
  local prompt_file="$out_dir/prompt.md"
  local report_file="$out_dir/report.md"
  local docs_report="$docs_dir/$d.md"
  local title="[Weekly Power & Macro Intelligence] $d"

  mkdir -p "$out_dir" "$docs_dir"

  if [[ -z "$s" ]]; then
    s="$(date -d "$d -6 days" +%F)"
  fi

  python3 scripts/weekly_power_macro_intelligence_collect.py \
    --week-end "$d" \
    --start "$s" \
    --end "$e"

  if ! python3 scripts/weekly_power_macro_intelligence_collect.py gate --week-end "$d" >"$out_dir/quality.json"; then
    echo "quality gate failed; preserved collection evidence and skipped report publication for $d" >&2
    return 1
  fi

  python3 scripts/build_weekly_power_macro_intelligence_prompt.py \
    --week-end "$d" \
    --prompt-file "$prompt_file"

  local prompt_bytes
  prompt_bytes="$(wc -c < "$prompt_file")"
  if [[ "$prompt_bytes" -gt "$prompt_max_bytes" ]]; then
    echo "prompt too large: ${prompt_bytes} bytes > ${prompt_max_bytes}" >&2
    return 1
  fi

  if ! timeout "$agy_timeout" bash -c 'agy --dangerously-skip-permissions --print "$(cat "$1")"' _ "$prompt_file" >"$report_file.tmp" 2>"$out_dir/agy.stderr"; then
    rm -f "$report_file.tmp"
    echo "agy failed or timed out; preserved collection and stderr and skipped report publication for $d" >&2
    return 1
  fi

  {
    printf '%s\n\n' "---"
    printf 'type: weekly_power_macro_intelligence\n'
    printf 'domain: Finance\n'
    printf 'week_end: %s\n' "$d"
    printf 'source: agy\n'
    printf '%s\n\n' "---"
    cat "$report_file.tmp"
    printf '\n'
  } >"$report_file"
  rm -f "$report_file.tmp"
  perl -0pi -e 's/[ \t]+$//mg' "$report_file"

  cp "$report_file" "$docs_report"
  python3 scripts/verify_weekly_power_macro_outputs.py --week-end "$d" >"$out_dir/verification.json"

  if [[ "$publish" == "true" ]]; then
    publish_issue "$repo" "$title" "$docs_report"
  fi
}

ensure_label() {
  local repo_name="$1"
  local label="$2"
  if gh api "repos/$repo_name/labels" --paginate --jq '.[].name' | grep -Fxq "$label"; then
    return 0
  fi
  gh api "repos/$repo_name/labels" \
    -f "name=$label" \
    -f color=0E8A16 \
    -f description="Weekly Power and Macro Intelligence" >/dev/null
}

issue_number() {
  local repo_name="$1"
  local title="$2"
  gh issue list \
    --repo "$repo_name" \
    --state all \
    --search "$title in:title" \
    --json number,title \
    --jq ".[] | select(.title == \"$title\") | .number" | sed -n '1p'
}

publish_issue() {
  local repo_name="$1"
  local title="$2"
  local body_file="$3"
  local labels=(
    weekly-regime
    central-bank
    boj
    fed
    fiscal-policy
    japan-government
    trump-administration
    tariff-watch
    ai-policy
    openai
    anthropic
    altman
    dario
    trade-watch
    ai-capex
    sbg-nav
    content-seed
  )

  local existing_number
  existing_number="$(issue_number "$repo_name" "$title")"
  if [[ -n "$existing_number" ]]; then
    gh issue edit "$existing_number" --repo "$repo_name" --body-file "$body_file" >/dev/null
    echo "issue updated: $title (#$existing_number)"
    return 0
  fi
  for label in "${labels[@]}"; do
    ensure_label "$repo_name" "$label"
  done

  local args=(issue create --repo "$repo_name" --title "$title" --body-file "$body_file")
  for label in "${labels[@]}"; do
    args+=(--label "$label")
  done
  gh "${args[@]}"
}

if [[ -n "$backfill_start" || -n "$backfill_end" ]]; then
  if [[ -z "$backfill_start" || -z "$backfill_end" ]]; then
    echo "--backfill-start and --backfill-end must be used together" >&2
    exit 2
  fi
  cursor="$backfill_start"
  while [[ "$(date -d "$cursor" +%u)" != "6" ]]; do
    cursor="$(date -d "$cursor +1 day" +%F)"
  done
  while [[ "$cursor" < "$backfill_end" || "$cursor" == "$backfill_end" ]]; do
    period_start="$(date -d "$cursor -6 days" +%F)"
    if [[ "$period_start" < "$backfill_start" ]]; then
      period_start="$backfill_start"
    fi
    run_one "$cursor" "$period_start" "$cursor"
    cursor="$(date -d "$cursor +7 days" +%F)"
  done
else
  run_one "$week_end" "$start" "${end:-$week_end}"
fi
