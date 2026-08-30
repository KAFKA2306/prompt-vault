# Architecture

Prompt Vault は「prompt文字列の保管庫」だけではなく、**再利用できる prompt 構造、生成artifact、編集可能な2D design、公開UIを別々の正本として管理し、buildで配布物へ落とす repository** です。

この文書は現在の構成を説明します。フィールドや検証条件の厳密な定義は、ここへ複製せず各実装を authority とします。

## Canonical sources

| 対象 | 正本 | 担当実装 |
| --- | --- | --- |
| Prompt DB | `db/prompts.json` | `src/prompt_db.py` |
| 生成artifactの採番・slug | `artifacts/` の実ファイル | `src/artifacts.py` |
| DB接続済み生成artifact | `artifacts/` + `db/prompts.json` | `scripts/artifacts/` |
| 固定サイズ2D design | `designs/*.svg` | `src/designs.py` |
| SVGから参照する生成画像素材 | `assets/generated/` | `src/designs.py`, `build.py` |
| Skill index | `docs/SKILLS.md` | `src/skills.py` |
| UI source | `static/` | `build.py`, `app.py` |
| 実行設定 | `config.yaml` | `config.py` |
| 静的配布物 | `dist/` | `build.py` が生成。正本ではない |
| 共通操作 | `Taskfile.yml` | Task |
| GitHub Pages delivery | `.github/workflows/deploy.yml` | GitHub Actions |

## Main data flow

```text
                    ┌─ blocks ──────────────┐
                    │                        │
db/prompts.json ────┴─ templates/artifacts ─┼── src/prompt_db.py ──┐
artifacts/ ──────────────────────────────────────────────────────────┤
designs/*.svg ───────────── src/designs.py ─────────────────────────┤
assets/generated/ ───────────────────────────────────────────────────┤
docs/SKILLS.md ──────────── src/skills.py ──────────────────────────┤
static/ ─────────────────────────────────────────────────────────────┤
                                                                      ↓
                                                                   build.py
                                                                      ↓
                                                                    dist/
                                                                      ↓
                                                               GitHub Pages
```

`dist/` を直接編集しません。変更はその生成元へ行います。

## Prompt and artifact path

Prompt DB は `Block` と `Template` を中心に構成されます。Template は block IDを組み合わせ、必要なら `artifacts` で生成PNG/WAV等へ接続します。

生成物を正式なDB接続artifactとして取り込む標準入口は次です。

```text
external generated .png/.wav
        ↓
scripts/artifacts/register_generated_artifact.py
        ├─ artifacts/NNN_slug.ext を作る
        ├─ db/prompts.json に generated template を追加
        └─ build + validate
```

採番・slugの共通ロジックは `src/artifacts.py` にあります。artifact登録script自身が別の命名規則を持つ構造にはしません。

## Blueprint design path

固定サイズ2D成果物では、最終PNGを正本にせずSVGを正本として扱う経路があります。

```text
Image generation
   ↓
assets/generated/<asset>
   ↓
designs/<design>.svg
   ├─ <image> : generated asset
   ├─ <text>  : actual text
   ├─ font-family
   ├─ coordinates
   ├─ shapes / paths
   └─ layer order
   ↓
build.py
   ↓
dist/designs/ + dist/assets/generated/
```

この経路では、意味を持つ文字・font・座標・図形を画像生成モデルのpixelへ焼き込まず、編集可能なSVG構造として保持します。Image generation は人物、写真、イラスト、背景などのasset generationに限定できます。

`src/designs.py` が現在のcanonical SVG contractを検証します。具体的な条件は実装がauthorityですが、少なくとも固定width/height、整合するviewBox、重複しないID、実font指定、repository内image参照を検証します。

## `artifacts/` と `assets/generated/` の違い

両者は同じ「画像置き場」ではありません。

- `artifacts/`: `db/prompts.json` の `Template.artifacts` から参照される生成結果。artifact connectivity audit の対象。
- `assets/generated/`: SVG等が構成素材として参照する generated asset。`build.py` が `dist/assets/generated/` へコピーし、`src/designs.py` がSVG内のローカル参照を検証する。

用途が違うため、片方をもう片方のfallbackとして扱いません。

## Build boundary

`build.py` は主に次を行います。

- Prompt DBをPydantic modelとして読み、block/artifact参照を確認
- `static/` からUIを生成
- Prompt DB と Skill index を `app.js` に埋め込む
- `designs/` と `assets/generated/` を配布物へコピー
- active artifactを `dist/artifacts/` へ公開
- PNG artifactは利用可能なrendererに応じてWebPへ変換する実装を持つ
- KAFKA SIGNALの公開ファイルをコピー

出力形式の細部は `build.py` がauthorityです。Documentation側で同じ変換ルールを別定義しません。

## Local and production surfaces

- `app.py`: ローカル確認用server
- `build.py`: 静的site生成
- GitHub Pages: `.github/workflows/deploy.yml` がmain pushでdeployし、production URLを取得して検証
- Cloudflare Pages Function: `functions/api/prompt-generate.js`。GitHub Pages workflowとは別の公開経路

PRのbuild成功とproduction deploy成功は別の証拠として扱います。

## Dependency direction

現在の `src/` は用途が名前から分かる小さなmoduleに限定します。

```text
src/
├── prompt_db.py
├── artifacts.py
├── designs.py
└── skills.py
```

現行規模では `domain/`, `services/`, `infra/` のような抽象階層を先に作りません。責務が実際に分裂したときにのみ分割します。

## Documentation boundary

- この文書: 構成と責務
- [SCHEMA.md](SCHEMA.md): Prompt DBのデータモデル
- [OPERATIONS.md](OPERATIONS.md): 操作方法
- [VALIDATION.md](VALIDATION.md): 検証契約
- [UI_DESIGN.md](UI_DESIGN.md): UI design intent
- `ADR/`: 過去の意思決定記録

現在の挙動とMarkdownが矛盾した場合、実装を確認しMarkdownを更新します。
