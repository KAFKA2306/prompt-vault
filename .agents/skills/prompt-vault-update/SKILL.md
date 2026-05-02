---
name: prompt-vault-update
description: Turn pasted links, tweets, posts, articles, PDFs, videos, or artifact requests into Prompt Vault DB updates. Use when the user drops an external source, asks to add or update a prompt/template/news item, says artifacts or rename, or needs db/prompts.json and dist/ updated with a new format.
---

# Prompt Vault Add Flow

## Overview

Use this skill to turn an incoming source or artifact request into a concrete Prompt Vault update. Read the source, search related context, choose or design the best format, generate a new image with `imagegen` when needed, then update `db/prompts.json`, artifacts, and generated output.

## Workflow

1. Classify the input.
   - Link, tweet, PDF, or video: source ingestion.
   - `artifacts*` or rename request: artifact maintenance.

2. Gather context.
   - Read the primary source carefully.
   - Search related or official follow-up sources when needed.
   - Inspect the closest examples in `db/prompts.json` and `artifacts/`.

3. Choose the format.
   - Prefer the best-fitting existing template when it is clearly appropriate.
   - Design a new format when repetition would feel forced or stale.
   - Keep Kafka as the default visual anchor, but reduce or remove her when she hurts clarity or factual precision.

4. Draft the update.
   - Preserve factual wording and dates.
   - Keep any emotional tone that matters to the source.
   - For manga/news outputs, identify the key beats and make them readable as short panels or callouts.

5. Update files.
   - Edit `db/prompts.json` first.
   - If a new visual is needed, call `imagegen` and save the result into `artifacts/` before wiring it into the DB.
   - Inspect the generated image before copying it into the project so the artifact matches the intended prompt.
   - Add or rename artifact files to match the `NNN_slug.png` convention.
   - Keep `db/prompts.json` `path` values aligned with real file names.
   - Update `static/app.js` only if a new family or label is needed.

6. Build and verify.
   - Run `python3 build.py`.
   - Check `http://127.0.0.1:8787/`.
   - Confirm the artifact appears, the labels read correctly, and the layout still works.

## Rules

- Do not force everything into one old pattern.
- Create a new format when it improves clarity or avoids repetition.
- Use `imagegen` directly when the task needs a new bitmap visual, instead of asking for manual image creation.
- Verify the generated image before treating it as the final artifact.
- Do not edit `dist/` by hand.
- Keep artifact renames and DB links in sync.
- If a source is uncertain, verify before writing it into the DB.

## Reference

See [workflow.md](references/workflow.md) for the concrete step order, file targets, and artifact-handling checklist.
