# ADR 0008: 外部ソースから Prompt Vault を更新する流れ

ステータス: 承認済み

## コンテキスト

このリポジトリでは、ユーザーが記事リンク、ツイート、PDF、動画、または `artifacts*` のような一言を突然貼ることがある。
そのたびに、毎回その場で手順を考えると、形式がぶれやすく、ファイル名や参照先のズレも起きやすい。

## 決定事項

- 入力をまず2種類に分ける。
  - 外部ソースの追加
  - `artifacts` の整理や rename
- 外部ソースは、関連ソースを探してから読む。
- その内容に合うフォーマットを選ぶ。
  - 既存型で足りるなら再利用する
  - 無理があるなら新しい型を作る
- `Kafka` は原則使う。
  - ただし、邪魔なら小さくする
  - 事実性や読みやすさを優先する
- `db/prompts.json` を先に更新する。
- 生成画像を正式な資産にする場合は、`scripts/artifacts/register_generated_artifact.py` を使って `artifacts/NNN_slug.png` への採番・コピー・DB追記を一度に行う。
- `artifacts` は実ファイル名と DB の `path` を必ず一致させる。
- 変更後は `python3 build.py` と `python3 scripts/validate_db.py` を実行する。
- 最後に `python3 app.py` で `http://127.0.0.1:8787/` を確認する。

## 例

- 記事リンクが来たら、公式ソースを読み、必要なら関連記事も探し、最適なテンプレートを選ぶ。
- `artifacts*` と来たら、画像を `scripts/artifacts/register_generated_artifact.py` 経由で `NNN_slug.png` に登録し、DB の参照も合わせる。

## 理由

- 同じ手順を毎回手で考えなくてよくなる。
- 形式の単調化を避けやすくなる。
- 画像、JSON、生成物の不一致を防ぎやすくなる。

## 運用

1. 入力を分類する。
2. 読む。
3. 形式を決める。
4. `db/prompts.json` を更新する。
5. 必要なら `scripts/artifacts/register_generated_artifact.py` を使って登録する。
6. `python3 build.py` と `python3 scripts/validate_db.py` を実行する。
7. localhost で確認する。
