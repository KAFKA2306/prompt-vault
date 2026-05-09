# Prompt Vault Workflow Reference

## Input types

- `link`, `tweet`, `PDF`, `video`, `article`, `post`: source ingestion.
- `artifacts*`, `rename`, `view artifact`, `replace image`: artifact maintenance.

## Source ingestion

1. Read the primary source.
2. If the facts or dates are unclear, search one or two official or close follow-up sources.
3. Compare with the closest existing Prompt Vault examples in `db/prompts.json` and `artifacts/`.
4. Choose one output format.
5. If the update needs a fresh bitmap, generate it with `imagegen`.
6. Inspect the generated image.
7. Copy the selected image into `artifacts/NNN_slug.png`.
8. Write or update `db/prompts.json`.
9. Run `python3 build.py`.
10. Check `http://127.0.0.1:8787/`.

## Format selection

- Prefer an existing template when it already matches the material.
- Create a new template or block when the content would be forced into the wrong shape.
- Use `kafka_visual_standard` and `artifacts/097_rendering_quality_check_contrast.png` as the Kafka visual references.
- Kafka appearance: long light-blue hair with a lavender gradient, semi-transparent bangs, fluffy layered hair, blue-purple eyes, soft pale skin, silver triangle hairpin with a cat ornament on the left side, braided section on the right side with a black ribbon.
- Keep `character_kafka`, `character_kafka_soft_reference`, and `kafka_identity_lock` consistent.
- Prefer `prompt_hierarchy_pack`, `model_params_pack`, and `artifact_meta_pack`.

## Artifact maintenance

1. Rename image files to `NNN_slug.png`.
2. Update the `path` in `db/prompts.json`.
3. Inspect the image before keeping it.
4. Rebuild and verify locally.
5. Confirm every referenced `artifacts/*.png` also exists in `dist/artifacts/` after the rebuild.

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
- If the prompt shape feels too mixed, split it into layer blocks instead of growing one block indefinitely.

## Output checklist

- Source facts are preserved.
- The format is the right one, or a new one was created.
- Kafka is present unless it would get in the way.
- New bitmap visuals were generated with `imagegen` when that reduced manual work.
- Artifact names and DB paths match.
- Local build and localhost check pass.
