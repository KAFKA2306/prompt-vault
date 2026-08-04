# Prompt Vault

Prompt Vaultは、画像生成プロンプトを再利用可能な部品へ分解し、生成画像、来歴、用途、検索用メタデータと一緒に管理・公開するためのプロンプト保管庫です。

単なる文章のメモ帳ではありません。プロンプトの構成要素を`block`として整理し、テンプレート、生成アセット、静的サイトを同じデータモデルから再生成できるようにします。

> **公開サイト:** https://kafka2306.github.io/prompt-vault/  
> **Cloudflare Pages:** https://prompt-vault-cg3.pages.dev/  
> **対応Python:** 3.11系  
> **正準データ:** `db/prompts.json`  
> **正準アセット:** `artifacts/`  
> **生成物:** `dist/`

---

## 何ができるか

- 画像生成プロンプトを部品、テンプレート、生成例として整理する
- 画像を見ながらプロンプト全文をコピーする
- タグや構成要素から関連プロンプトをたどる
- 既存blockを組み合わせて新しいプロンプトを構築する
- 生成画像を採番し、データベースと同時に登録する
- 未接続アセット、破損データ、命名違反を監査する
- GitHub PagesまたはCloudflare Pages向けの静的サイトを生成する
- Cloudflare Pages Functionから、管理されたプロンプトを参照する

現在のUIは、長時間閲覧しても疲れにくいこと、生成例から目的のプロンプトへ短く到達できること、コピー操作を妨げないことを重視しています。

---

## データと生成物の関係

```text
プロンプトblock・template・artifact参照
        │
        ▼
db/prompts.json
        │
        ├─ Pydanticモデルと監査スクリプトで検証
        │
        ├─ artifacts/の画像と接続
        │
        ▼
build.py
        │
        ▼
dist/  静的サイト生成物
        │
        ▼
GitHub Pages / Cloudflare Pages
```

### 正準

| 種類 | 正準 |
|---|---|
| block、template、artifact接続 | `db/prompts.json` |
| データ型と制約 | `src/models.py`、`docs/SCHEMA.md` |
| 採用済み画像 | `artifacts/` |
| デザイン原則 | `DESIGN.md` |
| 設計判断 | `docs/ADR/` |
| エージェント操作契約 | `AGENTS.md` |

### 生成物

`dist/`は`build.py`から生成される公開用成果物です。直接編集しません。

`artifacts/_orphaned/`は、現在のデータベースへ接続されていない旧アセットの退避先です。公開アセットの正準として扱いません。

---

## blockの考え方

Prompt Vaultでは、再利用できる構成要素をblockとして扱います。

主なrole:

- `identity` — キャラクターやブランドの固定要素
- `style` — 描画・写真・質感の方向性
- `layout` — 構図や情報配置
- `outfit` — 衣装
- `pose` — 姿勢や動き
- `background` — 背景
- `lighting` — 光
- `text` — 画像内文字の条件
- `situation` — 一時的な場面
- `pack` — 複数要素をまとめた再利用単位

キャラクターKafkaの同一性に関する固定要素と、一回限りの状況や衣装を分離します。具体的な日付、特定投稿だけの文言、長大な構成を汎用blockへ混ぜません。

詳細は[`docs/SCHEMA.md`](docs/SCHEMA.md)と[`docs/ADR/0012-semantic-block-naming.md`](docs/ADR/0012-semantic-block-naming.md)を参照してください。

---

## セットアップ

### 必要環境

- Python 3.11
- `uv`
- Git
- 画面を使った検証を行う場合は、Seleniumが利用できるブラウザ環境

### 依存関係の導入

```bash
uv sync
```

`pyproject.toml`では、Pydantic、PyYAML、Selenium、Pillowを利用します。

---

## ローカルで閲覧する

```bash
uv run python app.py
```

既定のローカルURLは、起動時の出力を確認してください。READMEに固定したlocalhost URLだけを根拠に、起動済みとは判断しません。

---

## 静的サイトを生成する

```bash
uv run python build.py
```

生成後は`dist/`を直接修正せず、正準データまたは生成処理を修正して再生成します。

---

## 生成画像を登録する

採用する画像は、手動で`artifacts/`へ移動しません。次のスクリプトで、採番、コピー、データベース追記、静的生成、検証をまとめて行います。

```bash
uv run python scripts/register_generated_artifact.py \
  --source /path/to/generated.png \
  --title "画像のタイトル" \
  --purpose "利用目的" \
  --summary "内容の要約"
```

必要に応じて`--generated-prompt`と`--blocks`を指定します。

`--source`には、現在の環境に存在する画像ファイルを渡します。生成ツール固有の絶対パスはリポジトリの契約ではありません。

登録方針は[`docs/ADR/0018-unconnected-png-reconnect-workflow.md`](docs/ADR/0018-unconnected-png-reconnect-workflow.md)に記録しています。

---

## 未接続画像を再接続する

事前確認:

```bash
uv run python scripts/reconnect_unconnected_pngs.py --dry-run
```

実行:

```bash
uv run python scripts/reconnect_unconnected_pngs.py
```

この処理は、旧PNGの再採番と`db/prompts.json`への再接続に使います。結果を確認せずに大量ファイルを移動しません。

---

## 検証

主な検証入口:

```bash
uv run python scripts/validate_db.py
uv run python scripts/audit_db.py
uv run python scripts/audit_artifacts.py
bash scripts/verify_pages.sh
```

確認対象:

- JSONがモデルとschemaに適合すること
- block名、role、参照関係が有効であること
- `db/prompts.json`と`artifacts/`が接続していること
- rootの`artifacts/`に未接続PNGを残していないこと
- 再利用性の低い文言や過大なblockが混入していないこと
- 静的サイトが再生成できること
- 公開前のファイル構造がPagesの前提を満たすこと

検証スクリプトの存在だけでは、現在の公開サイトが正しい証拠にはなりません。公開後は実URLも確認します。

---

## Cloudflare Pages Function

`functions/api/prompt-generate.js`はCloudflare Pages Functionです。生成本文の管理対象として`prompts/frontend_codex.md`を参照します。

FunctionへAPIキーや秘密情報を直接コミットしません。Cloudflare側の環境変数が必要な場合は、リポジトリ外で管理します。

---

## ディレクトリ構成

```text
artifacts/               採用済み画像
  _orphaned/             未接続旧画像の退避
config.yaml              モデルなどの共通設定
db/prompts.json          block、template、artifact接続の正準
src/models.py            Pydanticモデル
static/                   UIのHTML、CSS、JavaScript
prompts/                  Functionなどから参照するプロンプト
functions/                Cloudflare Pages Function
scripts/                  登録、再接続、監査、公開検証
docs/                     schema、skills、運用文書
docs/ADR/                 設計判断
dist/                     build.pyによる静的生成物
DESIGN.md                 デザイン方針
AGENTS.md                 エージェント操作契約
```

---

## README.mdとAGENTS.md

- `README.md`は、人間が目的、使い方、構造、運用、制約を理解する入口です。
- `AGENTS.md`は、AIエージェントが変更するときの読取順序、禁止事項、検証手順を定義します。

人間向けの重要事項をAGENTS.mdだけへ置かず、エージェント固有の細かな命令をREADMEへ重複させません。

---

## セキュリティと公開境界

公開リポジトリへ次を保存しません。

- APIキー、token、cookie、認証情報
- 非公開の会話全文
- 個人情報
- ローカル環境固有の秘密パス
- 利用権を確認できない第三者アセット
- 未公開の生成入力や機密prompt

画像、キャラクター、外部作品を参照する場合は、来歴、利用条件、変更内容を確認します。「特定作品風」など曖昧な模倣表現を正準データへ残しません。

---

## 既知の制約

- 公開サイトは静的生成物を中心とし、すべての生成処理をブラウザだけで完結させるものではありません。
- プロンプトから同じ画像が必ず再生成されることは保証しません。モデル、seed、サービス仕様、入力画像などの条件に依存します。
- 未接続画像を自動的に正しいtemplateへ推測接続しません。
- Cloudflare Pages Functionの稼働状態や環境変数は、Gitの内容だけでは確認できません。
- 外部生成ツールの出力場所は環境依存です。

---

## 関連文書

- [`DESIGN.md`](DESIGN.md) — UIと見た目の方針
- [`AGENTS.md`](AGENTS.md) — エージェント操作契約
- [`docs/SCHEMA.md`](docs/SCHEMA.md) — データモデル
- [`docs/SKILLS.md`](docs/SKILLS.md) — repo-local skill一覧
- [`docs/ADR/README.md`](docs/ADR/README.md) — ADR索引
- [`docs/ADR/0018-unconnected-png-reconnect-workflow.md`](docs/ADR/0018-unconnected-png-reconnect-workflow.md) — 未接続画像の再接続
- [`docs/ADR/0019-config-and-shared-artifact-ops.md`](docs/ADR/0019-config-and-shared-artifact-ops.md) — 設定と共通アセット操作
- [`docs/ADR/0021-external-reference-hygiene.md`](docs/ADR/0021-external-reference-hygiene.md) — 外部参照の衛生管理

---

## ライセンス

コード、生成画像、プロンプト、第三者素材では適用条件が異なる場合があります。リポジトリの`LICENSE`、各アセットの来歴、外部サービスの利用規約を確認してください。

**README実体監査:** 2026年8月4日
