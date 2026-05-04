# Prompt Vault Add Flow Reference

## Input types

- `link`, `tweet`, `PDF`, `video`
  - Treat as source ingestion.
- `article`, `post`
  - Treat as source ingestion.
- `artifacts*`, `rename`, `view artifact`, `replace image`
  - Treat as artifact maintenance.

## Source ingestion

1. Read the primary source.
2. Search one or two official or close follow-up sources if the facts or dates are unclear.
3. Compare with the closest existing Prompt Vault examples in `db/prompts.json` and `artifacts/`.
4. Choose one output format.
5. If the update needs a fresh bitmap, generate it with `imagegen`.
6. Inspect the generated image.
7. Copy the selected image into `artifacts/`.
8. Write or update `db/prompts.json`.
9. Run `python3 build.py`.
10. Check `http://127.0.0.1:8787/`.

## Format selection

- Prefer an existing template when it already matches the material.
- Create a new template or block when the content would be forced into the wrong shape.
- Use the closest saved Prompt Vault prompt as the default reference for wording, structure, and visual tone.
- Use `Kafka` by default as the visual anchor.
- Use `db/prompts.json`'s `kafka_visual_standard` block and `artifacts/097_rendering_quality_check_contrast.png` as the default Kafka visual references when judging face, hair, color balance, shading, and polish.
- Reduce `Kafka` when factual precision or readability matters more.
- Keep Kafka's face and identity consistent, but change the outfit to match the specific situation, place, time of day, weather, season, and activity.

## Artifact maintenance

1. Rename image files to `NNN_slug.png`.
2. Update the `path` in `db/prompts.json`.
3. Keep the display `title` short and descriptive.
4. If a replacement visual is needed, generate it with `imagegen` first.
5. Inspect the image before keeping it.
6. Rebuild and verify locally.
7. Confirm every referenced `artifacts/*.png` also exists in `dist/artifacts/` after the rebuild.

## Editing rules

- Edit `db/prompts.json` before `dist/`.
- Do not hand-edit `dist/`.
- Keep file paths relative to the repo root.
- If the UI needs a new label family, update `static/app.js`.
- If multiple candidate formats exist, choose one and do not mix them in the same update.
- If the source is still ambiguous after one search pass, stop and verify before writing facts into the DB.
- If the user says to base the work on existing Prompt Vault prompts, do not invent a new style unless the current entries clearly fail.
- If the user says Kafka looks wrong, compare against `kafka_visual_standard` and `097_rendering_quality_check_contrast.png` before changing anything else.
- Treat a missing `dist/artifacts/*.png` copy as a sync bug, not as an acceptable partial build.

## Output checklist

- Source facts are preserved.
- The format is the right one, or a new one was created.
- Kafka is present unless it would get in the way.
- New bitmap visuals were generated with `imagegen` when that reduced manual work.
- Artifact names and DB paths match.
- Local build and localhost check pass.
