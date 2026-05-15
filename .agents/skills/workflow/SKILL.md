---
name: prompt-vault-workflow
description: Prompt Vault の素材取り込みとアセット管理を扱う skill。画像だけ渡されたとき、path だけ渡されたとき、画像生成プロンプトだけ渡されたとき、`db/prompts.json` を直したいとき、`validate_db.py` / `audit_db.py` で検証したいとき、`register_generated_artifact.py` で画像登録したいとき、`reconnect_unconnected_pngs.py` で未接続 PNG を再接続したいとき、`audit_artifacts.py` で監査したいとき、`build.py` と `verify_pages.sh` で公開前確認したいときに使う。
---

# Prompt Vault Workflow (FSM Edition)

この skill は、Prompt Vault の入力が画像だけ、path だけ、画像生成プロンプトだけ、または `db/prompts.json` とアセットの整合性相談だけのときに使う。まず `references/workflow.md` で該当する分岐を選び、その分岐に書かれたコマンドだけを実行する。

## 1. 最初に見るもの

- 画像または path があるとき: そのファイルを登録対象として扱う。
- 画像生成プロンプトだけがあるとき: 生成結果を `register_generated_artifact.py` に渡せる形にする。
- `db/prompts.json` の修正があるとき: `validate_db.py` と `audit_db.py` を通す。

## 2. 実行ルール

- `artifacts/` と DB を手で更新しない。
- `reconnect_unconnected_pngs.py` は未接続 PNG の整理に使う。
- 登録後は `audit_artifacts.py` を確認する。
- 公開前は `build.py` と `scripts/verify_pages.sh` を確認する。
- `character_kafka` と `kafka_identity_lock` を崩さない。

## 3. 参照

分岐と実行コマンドの詳細は `references/workflow.md` にまとめる。
