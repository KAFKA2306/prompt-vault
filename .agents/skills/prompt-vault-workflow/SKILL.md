---
name: prompt-vault-workflow
description: Run Prompt Vault source ingestion and artifact maintenance end to end, including image generation, artifact path updates, DB updates, and local verification.
---

# Prompt Vault Workflow

## Scope

Use this skill for one Prompt Vault update end to end.

## Required end state

- Selected image copied into `artifacts/NNN_slug.png`
- `db/prompts.json` updated
- `python3 build.py` run
- `http://127.0.0.1:8787/` checked

## Fixed references

- Generated images start in `/home/kafka/.codex/generated_images/`
- Formal image assets live at `artifacts/NNN_slug.png`
- Artifact cleanup uses `artifacts/_orphaned/`
- Kafka visuals use `character_kafka`, `character_kafka_soft_reference`, and `kafka_identity_lock`

## Rules

- Read `references/workflow.md` for the step order.
- Edit `db/prompts.json` before `dist/`.
- Do not hand-edit `dist/`.
- Verify the generated image before keeping it.
