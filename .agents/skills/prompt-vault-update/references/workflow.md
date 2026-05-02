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
3. Compare with the closest existing Prompt Vault examples.
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
- Use `Kafka` by default as the visual anchor.
- Reduce `Kafka` when factual precision or readability matters more.

## Artifact maintenance

1. Rename image files to `NNN_slug.png`.
2. Update the `path` in `db/prompts.json`.
3. Keep the display `title` short and descriptive.
4. If a replacement visual is needed, generate it with `imagegen` first.
5. Inspect the image before keeping it.
6. Rebuild and verify locally.

## Editing rules

- Edit `db/prompts.json` before `dist/`.
- Do not hand-edit `dist/`.
- Keep file paths relative to the repo root.
- If the UI needs a new label family, update `static/app.js`.
- If multiple candidate formats exist, choose one and do not mix them in the same update.
- If the source is still ambiguous after one search pass, stop and verify before writing facts into the DB.

## Output checklist

- Source facts are preserved.
- The format is the right one, or a new one was created.
- Kafka is present unless it would get in the way.
- New bitmap visuals were generated with `imagegen` when that reduced manual work.
- Artifact names and DB paths match.
- Local build and localhost check pass.
