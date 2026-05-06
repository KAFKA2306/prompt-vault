# Prompt Vault データベース定義 (Schema)

`db/prompts.json` の構造を定義します。この定義は `src/models.py` (Pydantic) を正本としています。

## 基本構造

データベースは `blocks` と `templates` の2つの主要なリストで構成されます。

### 1. Block (構成要素)

プロンプトの部品となる最小単位です。

- `id`: 文字列。一意の識別子（例: `master_style`）。
- `title`: 文字列。部品の名称。
- `content`: 文字列。実際のプロンプトテキスト。
- `category`: 文字列。部品の分類（例: `style`, `character`）。

### 2. Template (テンプレート)

複数の Block を組み合わせて一つのプロンプトを構成する定義です。

- `id`: 文字列。一意の識別子。生成データの場合は `gen_ISO8601` 形式。
- `title`: 文字列。テンプレートの名称。
- `blocks`: 文字列のリスト。使用する Block の ID 群。
- `kind`: 文字列。`standard`（標準）または `generated`（生成済み）。
- `purpose`: 文字列。使用目的。
- `summary`: 文字列。内容の要約。
- `artifacts`: オブジェクトのリスト。
  - `path`: 文字列。画像ファイルへの相対パス（例: `artifacts/001_xxx.png`）。
  - `title`: 文字列。画像のタイトル。
- `generated_prompt`: 文字列（任意）。生成済みの完成プロンプト全文。
- `created_at`: 文字列（任意）。作成日時の ISO8601 文字列。

## バリデーションルール

1. **一貫性**: `templates` 内で指定されるすべての `blocks` ID は、`blocks` リスト内に存在しなければならない。
2. **資産の存在**: `artifacts` で指定されるすべての `path` は、実際のファイルシステム上に存在しなければならない。
3. **生成データの品質**: `kind: "generated"` のテンプレートには、少なくとも1つの `artifacts` が紐付いていることが推奨される。
