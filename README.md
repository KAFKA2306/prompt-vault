https://kafka2306.github.io/prompt-vault/
https://prompt-vault-cg3.pages.dev/

# Prompt Vault

[![Deploy](https://github.com/KAFKA2306/prompt-vault/actions/workflows/deploy.yml/badge.svg)](https://github.com/KAFKA2306/prompt-vault/actions/workflows/deploy.yml)

生成プロンプトを文章のまま保存するのではなく、再利用できる構成要素、組み合わせ、生成画像、用途、来歴を分けて管理する保管庫です。

- 再利用単位: `block`
- 組み合わせ: `template`
- 生成物: `artifact`
- 正準データ: `db/prompts.json`
- 正準アセット: `artifacts/`
- データ型と制約: `src/models.py`
- 静的生成: `build.py`
- UI: `static/`
- 生成物: `dist/`（直接編集しない）

## 構造

```text
db/prompts.json
        │
        ├─ src/models.py / validator で検証
        ├─ artifacts/ と接続
        ▼
build.py
        ▼
dist/
        ▼
GitHub Pages / Cloudflare Pages
```

変更され得る仕様は Markdown に重複して持たず、現在の実装と機械可読データを優先します。AI coding agent の作業規約は `AGENTS.md` を参照してください。

## セットアップ

必要環境は Python 3.11、`uv`、Git です。

```bash
uv sync
```

ローカル表示:

```bash
uv run python app.py
```

静的サイト生成:

```bash
uv run python build.py
```

`dist/` は生成物です。修正は正準データ、UI、または生成処理へ行います。

## 生成画像を登録する

採用する画像は登録スクリプトを通して、採番、コピー、データベース追記、静的生成、検証をまとめて行います。

```bash
uv run python scripts/register_generated_artifact.py \
  --source /path/to/generated.png \
  --title "画像のタイトル" \
  --purpose "利用目的" \
  --summary "内容の要約"
```

外部ツール固有の絶対パスを repository の契約にしません。

## 検証

既存の共通入口を使います。

```bash
task validate
task artifacts-audit
task build
```

全体確認:

```bash
task deliver
```

Pull Request では変更した head SHA を checkout してデータ検証と build を行います。`main` では GitHub Pages へ deploy し、公開 URL を取得して実ページを確認します。ローカル build や CI 成功だけを production 成功の証拠にしません。

## データ方針

- `db/prompts.json` と `artifacts/` の接続を検証する。
- synthetic、fixture、placeholder を実生成物の代用にしない。
- 未接続・未使用・重複を確認できたものは残さず削除する。
- 一回限りの日付、文言、衣装、背景を汎用 `block` に混ぜない。
- 取得失敗や検証失敗を fallback や broad exception で成功扱いにしない。
- 新しい個別 script を増やす前に既存 validator へ統合する。

## Cloudflare Pages Function

`functions/api/prompt-generate.js` は Cloudflare Pages Function です。秘密情報は repository に保存せず、必要な環境変数は Cloudflare 側で管理します。

## 公開境界

公開 repository へ API key、token、cookie、認証情報、個人情報、非公開会話、利用権を確認できない第三者アセットを保存しません。

公開 URL の稼働状態は Git の内容だけでは判断せず、実 URL を確認します。
