# Prompt Vault データベース定義 (Schema)

`db/prompts.json` の構造を定義します。本ドキュメントは `src/models.py` (Pydantic) の定義に基づいた、人間向けの解説書です。

## 1. 基本構造

データベースは、部品（Blocks）と組み合わせ（Templates）の2階層で構成されます。

### 1.1 Block (構成要素)

プロンプトを構成する最小単位（パーツ）です。

| フィールド | 型 | 説明 | 具体例 |
| :--- | :--- | :--- | :--- |
| `id` | 文字列 | 一意の識別子 | `"master_style"` |
| `title` | 文字列 | 部品の名称。[ADR 0012](ADR/0012-semantic-block-naming.md) の形式。 | `"キャラクター: KAFKA"` |
| `content` | 文字列 | プロンプト本文 | `"high quality, master piece..."` |
| `role` | 文字列 | 主役割。`identity` / `style` / `layout` / `outfit` / `pose` / `background` / `lighting` / `text` / `situation` / `pack`。 | `"identity"` |
| `category` | 文字列 | 部品の分類（任意） | `"style"`, `"character"` |

### 1.2 Template (プロンプトの型 / 成果物)

複数の Block を組み合わせて、具体的な用途（漫画、スタンプ等）を定義したもの、または生成済みの記録です。

| フィールド | 型 | 説明 |
| :--- | :--- | :--- |
| `id` | 文字列 | 一意の識別子。生成データは `gen_YYYYMMDD_HHMMSS` 形式。 |
| `title` | 文字列 | テンプレートまたは作品の名称。 |
| `blocks` | 配列 | 使用する `Block` の ID リスト。 |
| `kind` | 文字列 | **重要：** コンテンツの性質を定義します（実態に基づく11種類）。 |
| `purpose` | 文字列 | 使用目的（任意）。 |
| `summary` | 文字列 | 内容の要約（任意）。 |
| `artifacts` | 配列 | 画像ファイルや音声ファイル (`path`) とそのタイトル (`title`) のリスト。 |
| `generated_prompt` | 文字列 | 生成済みの完成プロンプト全文（任意）。 |
| `created_at` | 文字列 | 作成日時の ISO8601 文字列（任意）。 |

生成画像や生成音声を正式な資産として残す場合は、`artifacts/NNN_slug.png` または `artifacts/NNN_slug.wav` へ登録し、`db/prompts.json` の `artifacts` に必ず接続します。  
このリポジトリでは、手動の移動・採番・参照追記を避けるため、`scripts/register_generated_artifact.py` を単一入口として扱います。  
既存の未接続PNGを再採番して戻す場合は `scripts/reconnect_unconnected_pngs.py` を使います。  
未接続の古い PNG は `artifacts/_orphaned/` に退避し、`artifacts/` の根には残さない運用です。
- 生成画像の一次出力先は `/home/kafka/.codex/generated_images/` です。
- 生成音声の一次出力先は、各ワークフローが指定する出力先です。
- Kafka の見た目は `character_kafka` と `kafka_identity_lock` です。

### 1.3 構造ルール

`db/prompts.json` の編集では、次の境界を守ります。

- `character_kafka`、`character_kafka_core`、`hair_kafka_detail`、`accessory_kafka_hairpin`、`kafka_identity_lock`、`speech_mode_kafka` は identity block として扱う。
- `master_style`、`rendering_soft_standard`、`rendering_soft_infographic`、`rendering`、`clean_quality_rendering` は style block として扱う。
- `morning_*`、`gaming_*`、`reading_*`、`news_*`、`poker_*`、`joinwars_*`、`cosplay_*` は situation block として扱う。
- `pack` は最大 5 blocks 相当までに抑える。
- `template.blocks` は最大 8 blocks に抑える。
- 1 block は 1 主役割に抑える。
- 新規 block 作成前に既存 block を検索する。
- style と identity を混ぜない。
- template は用途だけを書く。

---

## 2. `kind` の定義

`kind` は、そのデータが「どのようなコンテンツか」を指定する属性です。

| 値 | 意味 |
| :--- | :--- |
| `social` | SNS投稿 |
| `design_sheet` | デザイン設計 |
| `sheet` | 設定シート |
| `announcement` | 告知バナー |
| `stamp` | スタンプ |
| `reaction` | 反応画像 |
| `brand` | ブランドロゴ |
| `comic` | 漫画 |
| `system` | システム基盤 |
| `news` | ニュース |

---

## 3. 具体的な記述例

### 標準テンプレート (Standard)

```json
{
  "id": "kafka_stamp_01",
  "title": "Kafkaスタンプ基本",
  "blocks": ["master_style", "character_kafka", "layout_stamp"],
  "kind": "stamp",
  "summary": "LINEスタンプ用。デフォルメされたKafkaの感情表現。"
}
```

### 生成済みスナップショット (Generated)

```json
{
  "id": "gen_20260506_150000",
  "title": "Kafka: 朝のコーヒー",
  "blocks": ["master_style", "character_kafka"],
  "kind": "social",
  "summary": "朝の光の中でコーヒーを飲むKafkaの生成結果。",
  "generated_prompt": "high quality, coffee, morning sun...",
  "artifacts": [
    { "path": "artifacts/128_kafka_evening_twilight.webp", "title": "Evening Twilight" }
  ]
}
```

---

## 4. バリデーションルール

1. **参照整合性**: `templates.blocks` に記述する ID は、必ず `blocks` リストに存在すること。
2. **画像の実在**: `artifacts.path` に記述するファイルは、必ず `artifacts/` フォルダ内に存在すること。
3. **WebP 最適化**: [ADR 0014](ADR/0014-webp-optimization.md) に従い、画像は原則として `.webp` 形式で管理すること。音声は `.wav` のまま扱うこと。
