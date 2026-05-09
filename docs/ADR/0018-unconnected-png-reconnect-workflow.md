# ADR 0018: 未接続PNGの再採番・再接続ワークフロー

## ステータス

承認済み

## コンテキスト

Prompt Vault では、画像を `db/prompts.json` に接続した状態で管理する必要がある。
新規の生成画像は `scripts/register_generated_artifact.py` で `artifacts/NNN_slug.png` に登録できるが、既存の未接続PNGをまとめて整理する作業には別の手順が必要だった。
- 生成画像の一次出力先は `/home/kafka/.codex/generated_images/`。
- 退避先は `artifacts/_orphaned/`。
- Kafka の見た目参照は `character_kafka`、`character_kafka_soft_reference`、`kafka_identity_lock`。

手動での移動、手動の採番、手動の参照追記は、再発しやすく、抜けや重複を招きやすい。
そこで、既存の未接続PNGを再採番して DB に戻す標準手順を明文化する。

## 決定

- 新規画像の登録は `python3 scripts/register_generated_artifact.py` を単一入口とする。
- 既存の未接続PNGを再採番して `artifacts/` と `db/prompts.json` に戻す場合は `python3 scripts/reconnect_unconnected_pngs.py` を使う。
- 事前確認だけしたい場合は `python3 scripts/reconnect_unconnected_pngs.py --dry-run` を使う。
- `artifacts/` の root に未接続PNGを残さない。
- 再接続時は、画像を `artifacts/NNN_slug.png` にそろえ、対応する `db/prompts.json` の `artifacts` 配列へ接続する。
- 変更後は `python3 build.py` と `python3 scripts/validate_db.py` を実行する。

## 理由

- 画像の登録と、既存資産の整理を分けると、操作の意味が明確になる。
- 再採番と再接続をスクリプト化すると、手動ミスを減らせる。
- `artifacts/` の root を「接続済み PNG のみ」に保てる。
- DB とファイルの不一致を早期に検出しやすくなる。

## 運用

1. 新しい画像を採用するときは `register_generated_artifact.py` を使う。
2. 既存の未接続PNGを整理するときは `reconnect_unconnected_pngs.py` を使う。
3. 変更後は build と validation を回す。
4. `artifacts/_orphaned/` は退避先として使うが、最終状態では root に未接続PNGを残さない。
