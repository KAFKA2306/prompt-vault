# Prompt Vault (2026 Edition)

画像生成プロンプトを、全文のまま積み上げるのではなく、
あとで使えるかたちにほどいて並べておく高品質な保管庫です。

2026年基準の「静かなUI (Quiet UI)」を採用し、
「すぐコピーできる」「再現しやすい」「触って気持ちいい」を統合しました。

## なぜつくったのか

- 毎回、長いプロンプトを最初から書いたくないから
- 似た出力を、少ない差分で再現したいから
- 完成イメージを先に見て、迷わず選びたいから

## プロジェクトの特徴

- **Quiet UI**: 長時間の閲覧でも疲れにくい、紙の質感を活かした洗練されたデザイン。
- **1-Click Copy**: 拡大表示から即座に全文プロンプトをコピーできる摩擦のない導線。
- **Navigable History**: モーダル内でノード（タグ）を辿っても、履歴保持により「戻る」ことが可能な高い回遊性。
- **Prompt Generator**: 既存のパーツ（ノード）を組み合わせて新しいプロンプトを構築可能。
- **Serverless Architecture**: GitHub Pages や Cloudflare Pages で即座に配信可能な静的構成。

## クイックリンク

- [ローカルプレビュー](http://127.0.0.1:8787/)
- [本番サイト (GitHub Pages)](https://kafka2306.github.io/prompt-vault/)
- [本番サイト (Cloudflare Pages)](https://prompt-vault-cg3.pages.dev/)

### ドキュメント

- [デザインガイドライン (DESIGN.md)](DESIGN.md)
- [開発・運用ルール (AGENTS.md)](AGENTS.md)
- [データベース定義 (docs/SCHEMA.md)](docs/SCHEMA.md)
- [設計決定記録 (docs/ADR/)](docs/ADR/README.md)

## 開発・運用

### ローカル開発サーバー

```bash
python3 app.py
```

### ビルド (静的ファイルの生成)

```bash
python3 build.py
```

`dist/` ディレクトリに配信用のファイルが生成されます。

### 画像の登録

生成した画像を本番資産として採用する場合は、手動で `artifacts/` に移動しないでください。次の単一コマンドで採番・コピー・DB追記・ビルド・検証まで行います。
この登録方針は [ADR 0018](docs/ADR/0018-unconnected-png-reconnect-workflow.md) にまとめています。
- 生成画像の一次出力先は `/home/kafka/.codex/generated_images/` です。
- Kafka の見た目は `character_kafka` と `kafka_identity_lock` です。

```bash
python3 scripts/register_generated_artifact.py \
  --source /path/to/generated.png \
  --title "Some Artifact Title" \
  --purpose "optional purpose" \
  --summary "optional summary"
```

必要なら `--generated-prompt` と `--blocks` も追加できます。

既存の未接続PNGを再採番して `db/prompts.json` に戻す場合は次を使います。

```bash
python3 scripts/reconnect_unconnected_pngs.py
```

事前確認だけしたい場合は `--dry-run` を付けます。

### 公開検証

```bash
bash scripts/verify_pages.sh
```

### アセット監査

```bash
python3 scripts/audit_artifacts.py
```

## データの管理

- **データベース**: `db/prompts.json` に全ての部品とテンプレートが格納されています。
- **アセット**: `artifacts/` に WebP 最適化された画像が格納されます。
- **退避先**: 未接続の古い PNG は `artifacts/_orphaned/` に移して保管します。再採番して戻すときは `scripts/reconnect_unconnected_pngs.py` を使います。
- **設定**: `config.yaml` でモデル名などを管理します。
- **Functions**: `functions/api/prompt-generate.js` は Cloudflare Pages Function です。生成本文は `prompts/frontend_codex.md` を読みます。

---

*“静かなUIで、創造的な対話をよりスムーズに。”*
