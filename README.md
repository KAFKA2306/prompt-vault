https://kafka2306.github.io/prompt-vault/
https://prompt-vault-cg3.pages.dev/

# Prompt Vault

[![Deploy](https://github.com/KAFKA2306/prompt-vault/actions/workflows/deploy.yml/badge.svg)](https://github.com/KAFKA2306/prompt-vault/actions/workflows/deploy.yml)

Prompt Vault は、promptを文章の塊として保存するだけでなく、**再利用構造・生成artifact・編集可能な2D design・公開UIを別々の正本として管理する repository** です。

## System at a glance

```text
db/prompts.json ──────┐
artifacts/ ────────────┤
designs/*.svg ─────────┤
assets/generated/ ─────┤
docs/SKILLS.md ─────────┤
static/ ────────────────┤
                        ↓
                     build.py
                        ↓
                      dist/
                        ↓
                   GitHub Pages
```

主な正本:

- Prompt DB: `db/prompts.json` / `src/prompt_db.py`
- DB接続済み生成物: `artifacts/`
- 固定サイズ2Dの編集可能な正本: `designs/*.svg`
- SVG用generated asset: `assets/generated/`
- UI source: `static/`
- 実行設定: `config.yaml`
- 静的生成: `build.py`
- 生成物: `dist/` — 直接編集しない

固定サイズ2Dでは、文字・font・座標・図形をSVG構造として保持し、画像生成は写真・人物・イラスト等のasset生成に分離できます。

## Documentation

現在仕様の入口は [docs/README.md](docs/README.md) です。

- [Architecture](docs/ARCHITECTURE.md) — 正本、責務、データフロー
- [Schema](docs/SCHEMA.md) — `db/prompts.json`
- [Operations](docs/OPERATIONS.md) — 日常操作とdelivery
- [Validation](docs/VALIDATION.md) — validator / CI / production verification
- [UI Design](docs/UI_DESIGN.md) — UIのstable design intent
- [AGENTS.md](AGENTS.md) — AI coding agentの作業契約

ADR、plan、reportは履歴・記録です。現在の実装と矛盾する場合はcurrent code / data / workflowを確認します。

## Quick start

```bash
uv sync
task run
```

静的build:

```bash
task build
```

全体delivery check:

```bash
task deliver
```

## Register generated artifacts

PNG/WAVを正式なDB接続artifactとして採用する標準入口:

```bash
uv run python scripts/artifacts/register_generated_artifact.py \
  --source /path/to/generated.png \
  --title "Artifact title" \
  --purpose "Purpose" \
  --summary "Summary"
```

未接続PNGの確認:

```bash
uv run python scripts/artifacts/reconnect_unconnected_pngs.py --dry-run
```

詳細は [docs/OPERATIONS.md](docs/OPERATIONS.md) を参照してください。

## Validation and delivery

```bash
task validate
task artifacts-audit
task build
```

PRではexact head SHAをcheckoutして検証・buildします。`main` pushではGitHub Pagesへdeployした後、workflowが取得したproduction URLを実際に確認します。PR CI successとproduction successを同一視しません。

詳細は [docs/VALIDATION.md](docs/VALIDATION.md) を参照してください。

## Repository rules

- `dist/` を直接修正しない。
- DB、artifact、SVGの意味構造をpixel出力だけに潰さない。
- 新しいscriptや独自schemaを増やす前に既存責務へ統合できるか確認する。
- 未接続・参照切れ・検証失敗をsilent fallbackで成功扱いしない。
- host固有pathやone-off手順を恒久documentationへ固定しない。
- Markdownへ実装仕様を重複コピーしない。current code / machine-readable dataをauthorityとする。

## Cloudflare

`functions/api/prompt-generate.js` はCloudflare Pages Functionです。GitHub Pages workflowとは別の公開経路です。秘密情報はrepositoryへ保存しません。
