# ADR 0011: `artifacts` は必ず DB に接続する

ステータス: 承認済み

## コンテキスト

`artifacts/` に画像ファイルだけが残ると、DB から見えない未接続PNGになる。
このリポジトリでは、画像は見た目の素材ではなく、`db/prompts.json` に結びついた記録として扱う。
- 生成画像の一次出力先は `/home/kafka/.codex/generated_images/`。
- 正式な画像資産は `artifacts/NNN_slug.png`。
- Kafka の見た目参照は `character_kafka`、`character_kafka_soft_reference`、`kafka_identity_lock`。

## 決定事項

- `artifacts/*.png` は、必ず `db/prompts.json` のどこかから参照する。
- 既存の画像に対しては、新しい `generated_prompt` レコードを追加して接続してよい。
- すでに意味のある親レコードがある場合は、その `artifacts` 配列に足してよい。
- 参照できない画像は、原則として残さない。
- 新規画像の登録は `python3 scripts/artifacts/register_generated_artifact.py` を単一入口とし、手動の移動・採番・DB追記を避ける。
- 既存の未接続PNGを再採番して戻す場合は `python3 scripts/artifacts/reconnect_unconnected_pngs.py` を使う。
- DB を直したら `python3 build.py` と `python3 scripts/validate_db.py` を実行する。

## 理由

- 画像と DB の不一致を減らせる。
- グラフ表示でDB未接続の画像が残りにくくなる。
- 何が使われているかを後から追いやすくなる。

## 運用

1. 画像を追加したら、同時に `db/prompts.json` へ接続する。
2. 既存画像を整理するときは、まず親レコードに足せるかを見る。
3. 親がないなら、最小の `generated_prompt` レコードを作る。
4. 変更後に build と validation を回す。
