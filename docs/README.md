# Prompt Vault Documentation

このディレクトリの Markdown はすべて同じ強さの「仕様」ではありません。現在の挙動を知りたい場合は、まず下記の **Current documentation** を読み、最終的な事実確認は実装・設定・機械可読データで行います。

## Current documentation

| 文書 | 役割 | 実装上の authority |
| --- | --- | --- |
| [ARCHITECTURE.md](ARCHITECTURE.md) | 現在の構成、正本、データフロー | `src/`, `build.py`, directory layout |
| [SCHEMA.md](SCHEMA.md) | `db/prompts.json` の人間向け説明 | `src/prompt_db.py`, `scripts/audit_db.py` |
| [OPERATIONS.md](OPERATIONS.md) | 日常操作、artifact登録、delivery | `Taskfile.yml`, `scripts/`, workflows |
| [VALIDATION.md](VALIDATION.md) | validator と production verification | validator scripts, `.github/workflows/deploy.yml` |
| [UI_DESIGN.md](UI_DESIGN.md) | UIの設計意図 | `static/` |
| [SKILLS.md](SKILLS.md) | Skill一覧 | Skill index loader / source index |

Repository 全体の入口は [../README.md](../README.md)、AI coding agent の作業規約は [../AGENTS.md](../AGENTS.md) です。

## Authority order

現在仕様が食い違った場合は、概ね次の順で確認します。

1. 現在の実装・workflow・設定
2. `db/prompts.json`、`designs/*.svg` などの機械可読な正本
3. 上記 Current documentation
4. ADR、manual、ops、plan、report
5. Issue、過去の会話、古い生成物

Markdownだけを根拠に実装挙動を推測しません。

## Historical / contextual documentation

- `ADR/`: 当時の意思決定記録。現在仕様と矛盾する場合は current implementation を優先します。
- `manual/`: 特定サービス・作業の手順書。
- `ops/`: 個別運用の説明。
- `plans/`: 計画・作業メモ。完了済みでも現行仕様の正本にはしません。
- `reports/`, `generated/`, `FTA/`: 調査・生成結果などの記録。
- `results-*.md`: KAFKA RESULTS 系workflowの個別契約・説明。
- `PERSONA_DEVELOPMENT.md`: personaに関するドメイン文書。

過去の削除済みdocumentationはGit履歴から参照できます。current treeに互換ポインタだけを残しません。

## Documentation rule

変更されやすい列挙・パス・フィールドを複数の Markdown にコピーしません。Schema は `src/prompt_db.py`、実行入口は `Taskfile.yml` と `scripts/`、公開経路は workflow を authority とし、document は「どこに何があるか」「どの責務か」を説明します。
