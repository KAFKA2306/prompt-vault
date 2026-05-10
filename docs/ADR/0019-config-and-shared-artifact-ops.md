# ADR 0019: 設定と共通 artifact 操作を単一正本に寄せる

## ステータス

承認済み

## コンテキスト

このリポジトリでは、`app.py`、`build.py`、`functions/api/prompt-generate.js`、`scripts/*` に同じ固定値や同種の処理が散在していた。

具体的には次のものが重複していた。

- `127.0.0.1`
- `8787`
- `gemini-2.5-flash`
- `gemini-2.5-flash-lite`
- `db/prompts.json`
- `static`
- `dist`
- `artifacts`
- `artifacts/_orphaned`
- `prompts/frontend_codex.md`
- `/home/kafka/.codex/generated_images/`
- `slugify`
- `next_artifact_number`

この状態では、設定変更や artifact 命名規則の変更が複数ファイルに波及し、誤解と修正漏れが起きやすかった。

## 決定事項

### 1. 設定の正本を `config.yaml` に置く

次の値を `config.yaml` に集約する。

- `app.host`
- `app.port`
- `ai.model`
- `paths.db`
- `paths.static`
- `paths.dist`
- `paths.artifacts`
- `paths.orphaned_artifacts`
- `paths.prompts`
- `paths.skills_index`
- `paths.generated_images`
- `audit_literals`

`config.py` は `config.yaml` を読むための薄い読み取り層とする。

### 2. Python 側は `config.py` を通して設定を読む

`app.py`、`build.py`、`scripts/*` は `config.yaml` を直接読まず、`config.py` の `CONFIG` と `root_path()` を使う。

### 3. artifact の共通処理を `src/` に昇華する

次の共通処理は `src/artifact_ops.py` に置く。

- `slugify`
- `next_artifact_number`

`scripts/register_generated_artifact.py` と `scripts/reconnect_unconnected_pngs.py` はこれを呼ぶだけにする。

### 4. 生成プロンプト本文は `prompts/frontend_codex.md` を正本にする

`app.py` と `functions/api/prompt-generate.js` は本文を直書きせず、`prompts/frontend_codex.md` を読む。

### 5. `dist/` は生成物、`prompts/` は本文資産とする

`build.py` は `prompts/` を `dist/prompts/` にコピーし、Cloudflare Pages Functions が同じ本文を参照できるようにする。

## 理由

- 設定値の変更点が 1 か所にまとまる
- artifact の採番と slug 生成が 1 箇所になる
- `scripts/*` は薄い入口になり、読みやすくなる
- `app.py` と `functions/` の本文が一致する
- `dist/` は配布物、`prompts/` は正本、という役割が明確になる

## 影響

- `config.yaml` の変更で、`app.py`、`build.py`、`scripts/*`、`functions/api/prompt-generate.js` の参照値が揃う
- `config.yaml` は固定値の一覧ではなく、実行設定の正本になる
- `src/artifact_ops.py` が artifact 命名の共通ロジックになる
- `build.py` が `dist/config.json` と `dist/prompts/frontend_codex.md` を出力する

## 結論

固定値は `config.yaml` に、artifact 共通処理は `src/` に寄せる。
`scripts/*` は実行入口に限定し、重複定義を増やさない。
