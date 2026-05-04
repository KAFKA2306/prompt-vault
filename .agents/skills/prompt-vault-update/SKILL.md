---
name: prompt-vault-update
description: Turn pasted links, tweets, posts, articles, PDFs, videos, or artifact requests into Prompt Vault DB updates. Use when the user drops an external source, asks to add or update a prompt/template/news item, says artifacts or rename, or needs db/prompts.json and dist/ updated with a new format.
---

# Prompt Vault Add Flow

## Overview

Use this skill to turn one user input into one concrete Prompt Vault update. Treat the request as either source ingestion or artifact maintenance, read the minimum needed context, choose one format, and base the new work on the closest existing entries in `db/prompts.json` first. Generate a new image with `imagegen` when the task needs a bitmap, then update `db/prompts.json`, artifacts, and generated output.

## Workflow

1. Classify the input.
   - Link, tweet, PDF, video, article, or post: source ingestion.
   - `artifacts*`, `rename`, `view artifact`, or `replace image`: artifact maintenance.

2. Gather context.
   - Read the primary source first.
   - Search one or two official or close follow-up sources when the facts or dates are not obvious.
   - Inspect the closest matching examples in `db/prompts.json` and `artifacts/`.
   - Treat existing Prompt Vault prompts as the default style and structure reference unless the user explicitly asks for a new direction.

3. Choose the format.
   - Pick one existing template when it already fits the job.
   - Create one new template or block when the old one would force the content into the wrong shape.
   - Use Kafka by default, but lower her presence when she hurts readability or factual precision.
   - Treat `db/prompts.json`'s `kafka_visual_standard` block and `artifacts/097_rendering_quality_check_contrast.png` as the visual standard for Kafka's face, hair, colors, line quality, and overall polish unless the user asks for a different style.
   - Keep Kafka's identity stable, but vary the outfit by the specific situation, place, time of day, weather, season, and activity so the image does not feel repetitive.

4. Draft the update.
   - Preserve factual wording, names, numbers, and dates exactly.
   - Keep the source tone when it matters.
   - Reduce the story to the few beats that must appear on screen.

5. Update files.
   - Edit `db/prompts.json` first.
   - If the task needs a new bitmap, call `imagegen`, inspect the result, then copy the selected file into `artifacts/`.
   - Rename or add artifact files to match `NNN_slug.png`.
   - Keep every `db/prompts.json` `path` value aligned with a real file name.
   - Update `static/app.js` only when a new family or label is required.

6. Build and verify.
   - Run `python3 build.py`.
   - Open `http://127.0.0.1:8787/`.
   - Confirm the new item appears, the labels read correctly, the image matches the DB reference, and every referenced `artifacts/*.png` also exists in `dist/artifacts/`.

## Rules

- Do not force everything into one old pattern.
- Create a new format when it improves clarity or avoids repetition.
- Start from the closest existing `db/prompts.json` examples before inventing a new prompt shape.
- For Kafka visuals, use `kafka_visual_standard` and `097_rendering_quality_check_contrast.png` as the default references and align new prompts to that look.
- Use `imagegen` directly when the task needs a new bitmap visual.
- Verify the generated image before treating it as the final artifact.
- Do not edit `dist/` by hand.
- Keep artifact renames and DB links in sync.
- Treat missing `dist/artifacts/*.png` copies as a blocking sync error after `build.py`.
- If a source is uncertain, verify before writing it into the DB.

## Reference

See [workflow.md](references/workflow.md) for the concrete step order, file targets, and artifact-handling checklist.
