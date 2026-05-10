---
name: prompt-vault-workflow
description: Prompt Vault の素材取り込みとアセット管理を最後まで通す。画像生成、アセットパス更新、DB 更新、ローカル確認をまとめて行うときに使う。
---

# Prompt Vault Workflow

この skill は、1 回の Prompt Vault 更新を最初から最後まで通すための手順書。

## Scope

1 回の Prompt Vault 更新を end to end で進めるときに使う。

## Required end state

- 選んだ画像が `artifacts/NNN_slug.png` にコピーされている
- `db/prompts.json` が更新されている
- `python3 build.py` を実行している
- `http://127.0.0.1:8787/` を確認している

## Fixed references

- 生成画像の一次出力先は `/home/kafka/.codex/generated_images/`
- 正式な画像資産は `artifacts/NNN_slug.png`
- アセット整理の退避先は `artifacts/_orphaned/`
- Kafka の見た目参照は `character_kafka`、`character_kafka_soft_reference`、`kafka_identity_lock`

## Rules

- 手順の順番は `references/workflow.md` を読む。
- `dist/` より先に `db/prompts.json` を編集する。
- `dist/` は手で編集しない。
- 生成画像は残す前に確認する。
