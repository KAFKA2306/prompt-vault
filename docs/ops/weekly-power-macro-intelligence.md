# Weekly Power & Macro Intelligence

Weekly Power & Macro Intelligence turns central-bank signals, state policy, frontier AI lab updates, AI power ideology, analyst interpretation, and market narratives into a KAFKA decision log.

## GitHub Actions

- Workflow: `.github/workflows/weekly-power-macro-intelligence.yml`
- Runner: `[self-hosted, linux, x64]`
- Schedule: `0 22 * * 5` UTC, equal to Saturday 07:00 JST
- Required local commands on the runner: `agy`, `gh`, `python3`, `bash`
- Default issue repo: `GITHUB_REPOSITORY` inside Actions

The workflow fails early if `agy` is not in `PATH`.

## Local Cron

Use this on the user PC when a self-hosted runner is not active:

```cron
0 7 * * 6 cd /mnt/d/projects/obsidian && WEEKLY_POWER_MACRO_REPO=KAFKA2306/prompt-vault scripts/run_weekly_power_macro_intelligence.sh >> 50_logs/finance-audit/weekly-power-macro-intelligence.cron.log 2>&1
```

## Manual Backfill Dry Run

```bash
scripts/run_weekly_power_macro_intelligence.sh \
  --backfill-start 2026-06-14 \
  --backfill-end 2026-07-04 \
  --no-publish
```

After the dry run passes quality gates, publish the full period:

```bash
WEEKLY_POWER_MACRO_REPO=KAFKA2306/prompt-vault \
  scripts/run_weekly_power_macro_intelligence.sh \
  --backfill-start 2026-04-03 \
  --backfill-end 2026-07-04
```

The runner skips an Issue when `[Weekly Power & Macro Intelligence] YYYY-MM-DD` already exists.

## Default Branch Requirement

GitHub schedule triggers run from the default branch. For `KAFKA2306/prompt-vault`, place `.github/workflows/weekly-power-macro-intelligence.yml` on `main`; a local `master` branch without `origin` is not enough for scheduled operation.
