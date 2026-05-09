# AGENTS.md - 思考ガイドライン

## 戦略的エントリポイント（どのファイルをどう見るか）

エージェントは、タスクの種類に応じて以下の順序で思考し、ファイルを読み取ること。

### 1. 構造とルールの把握（迷ったとき、新規追加時）

- **[SCHEMA.md](docs/SCHEMA.md)**: データの「型」と「分類」の正解。
- **[AGENTS.md](AGENTS.md)**: このファイル。開発の「作法」と「優先順位」。
- **[ADR/](docs/ADR/)**: 過去の「決定事項」とその理由。特に [ADR 0012](docs/ADR/0012-semantic-block-naming.md) の命名規則。
- **[src/models.py](src/models.py)**: 実装上の「真実」。Pydantic モデルがデータの整合性を担保する。

### 2. 視覚的・体験的な修正（表示崩れ、UI改善）

- **[DESIGN.md](DESIGN.md)**: 視覚的な「美学」と「禁止事項」。
- **[static/app.js](static/app.js)**: 表示の「ロジック」。検索、モーダル、画像表示の振る舞い。
- **[static/style.css](static/style.css)**: 見た目の「詳細」。余白、色、レスポンス。
- **[static/index.html](static/index.html)**: 画面の「骨格」。セクション配置。

### 3. コンテンツの追加・変更（プロンプト、画像）

- **[db/prompts.json](db/prompts.json)**: 全ての「源泉」。テンプレート、ブロック、`artifacts` の接続。
- **[artifacts/](artifacts/)**: 実体の「アセット」。ファイル名は `NNN_slug.png`。
- **[artifacts/_orphaned/](artifacts/_orphaned/)**: 退避した古い PNG の保管先。root の `artifacts/` に未接続 PNG を残さない。
- 生成画像の一次出力先: `/home/kafka/.codex/generated_images/`
- Kafka の見た目: `character_kafka`、`character_kafka_soft_reference`、`kafka_identity_lock`

### 4. 生成物の登録

- **[scripts/register_generated_artifact.py](scripts/register_generated_artifact.py)**: 生成画像を `artifacts/` と `db/prompts.json` に同時登録する単一入口。
- **[scripts/reconnect_unconnected_pngs.py](scripts/reconnect_unconnected_pngs.py)**: 既存の未接続PNGを再採番して `artifacts/` と `db/prompts.json` に再接続する整備用スクリプト。事前確認は `--dry-run` を使う。
- **[docs/ADR/0018-unconnected-png-reconnect-workflow.md](docs/ADR/0018-unconnected-png-reconnect-workflow.md)**: 未接続PNGの再採番・再接続に関する正式な決定事項。

---

## 思考の原則 (Meta Principles)

- **DB-First**: 画面を直す前に、まず `db/prompts.json` のデータ構造が正しいか、モデルに適合しているかを確認せよ。
- **Zero-Fat**: 「単機能・最小構成」を維持せよ。重複したロジックや、使われていないフィールドは削除の対象。
- **Gallery-First**: このプロジェクトは「ギャラリー」である。全ての変更は「画像が見やすく、プロンプトがコピーしやすいか」という基準で評価せよ。
- **Naming as Logic**: 名称（title）は単なるラベルではなく、システム内の役割（[ADR 0012](docs/ADR/0012-semantic-block-naming.md)）を示す。類似したブロックは「包含関係」がないか常に疑え。
- **External Reference Hygiene**: 外部参照は、借りるもの、変えるもの、一目で修正するものを分ける。[ADR 0021](docs/ADR/0021-external-reference-hygiene.md) に従い、`〇〇風` と `inspired by` は使わない。
- **Structure Boundaries**: `character_kafka`、`kafka_identity_lock`、`speech_mode_kafka` は identity block として固定する。`morning_*`、`gaming_*`、`news_*`、`cosplay_*` は situation block として一時注入だけにする。`pack` は最大 5 blocks 相当、`template.blocks` は最大 8 blocks を目安にする。
- **Role First**: `db/prompts.json` の `Block` には `role` を付ける。`identity`、`style`、`layout`、`outfit`、`pose`、`background`、`lighting`、`text`、`situation`、`pack` を基準に見る。
- **Source Fidelity**: ボードゲーム系の画像は、元のルール、コンポーネント、既存の見た目を確認してから作る。知っている人が見て違和感を覚える抽象化や、雑な一般化は避ける。

---

## 変更手順のメタ思考

1. **データ整合性**: `src/models.py` の Pydantic モデルを確認し、`db/prompts.json` を編集。
2. **生成物登録**: 画像を採用する場合は、`scripts/register_generated_artifact.py` を使って `artifacts/NNN_slug.png` への採番・コピー・DB追記を一度に行う。生成画像の一次出力先は `/home/kafka/.codex/generated_images/`。既存の未接続PNGを整理する場合は ADR 0018 に従って `scripts/reconnect_unconnected_pngs.py` を使う。手動の移動、手動の採番、`dist/` への直接編集はしない。
3. **静的生成**: 登録スクリプトが `python3 build.py` と `python3 scripts/validate_db.py` を通す。`dist/` はこのコマンドでのみ更新される「生成物」であり、直接編集は厳禁。
4. **内容照合**: `character_kafka` と `kafka_identity_lock` を確認してから画像を作る。
5. **ローカル検証**: 必要な場合のみ `python3 app.py` で表示を確認する。画像が表示されない、あるいは `画像なし` のラベルが出る場合は、`artifacts/` と JSON の接続ミスを疑う。
6. **アセット監査**: `python3 scripts/audit_artifacts.py` で root `artifacts/` と `db/prompts.json` の接続状態を確認する。
7. **公開検証**: `scripts/verify_pages.sh` でデプロイ後の状態をシミュレート。

---

## 自律実行と完了定義

- **完遂の定義**: 登録スクリプト実行後に `build.py` と `validate_db.py` が通り、必要に応じてローカル表示確認まで済んだ状態を指す。
- **停止の判断**: 大規模なディレクトリ構造の変更、あるいは既存の ADR に抵触する可能性が高い場合は、プランを提示して停止せよ。
- **文言の誠実さ**: 実装されていない機能を「できる」と書かない。DBにあるデータと、実際に画面に出る導線のみを記述せよ。
