# Prompt Vault 監査システム全体仕様 (Audit System Specification)

本ドキュメントは、Prompt Vault プロジェクト固有の整合性維持、品質担保、および実行環境の安全性を確保するための具体的な監査項目、鉄則、および手順を定義する。

## 監査の三層構造

プロジェクトの監査は以下の 3 つのレイヤーで構成され、すべて `Taskfile.yml` を通じてオーケストレーションされる。

1. **データ監査 (Static/Structural Audit)**: `db/prompts.json`、アセット、リテラルの静的検証。
2. **ハーネス監査 (Harness/Runtime Audit)**: AI エージェント（Antigravity）の実行環境とプロセスの安全性。
3. **公開監査 (Workflow/Deployment Audit)**: ビルド結果の整合性とデプロイ後の到達性。

---

## 1. データ監査 (Static/Structural Audit)

リポジトリ内の「正解（Canonical Truth）」が維持されているかを自動スクリプトで検証する。

### 構成要素と実行コマンド

- **スキーマ・孤立アセット検証**: `task validate` (`scripts/validate_db.py`)
  - Pydantic モデルによる `db/prompts.json` の構造検証。
  - DB に紐付いていない `artifacts/` 直下のファイルを検出（WARNING）。
- **アセット接続監査**: `task artifacts-audit` (`scripts/audit_artifacts.py`)
  - `artifacts/` と `artifacts/_orphaned/` の接続状態を詳細にチェック。
  - 「参照あり・ファイルなし」「未接続ファイル」「重複参照」を検出し、不整合があれば FAIL させる。
- **リテラル監査**: `task literals-audit` (`scripts/audit_literals.py`)
  - `config.yaml` で指定された必須リテラルが主要なドキュメントや ADR 内に正しく記述されているかを検証。
- **カノニカル監査**: `task canonical-audit` (`scripts/audit_db.py`)
  - **Canonical Drift 検出**: ブロックの責任範囲が逸脱していないか（Identity に Situation が混ざっていないか等）を検証。
  - **Role 整合性**: 指定されたロールの妥当性と、パックブロックの制限（最大10行）を確認。

---

## 2. ハーネス監査 (Harness/Runtime Audit)

AI エージェントの実行環境の品質を、本プロジェクト独自のガードレールに照らして監査する。

### 具体的なガードレール

- **リソース競合監視**: VRChat 実行時などの高負荷状態を検知し、AI による画像生成や Whisper 処理を安全に一時停止する仕組み。
- **インシデント管理**: `data/incidents.jsonl` への全てのタスク失敗、リトライ、スキップの構造化ログ記録。
- **実行環境の隔離**: `uv run` を介した依存関係の隔離と、決定論的なツール呼び出しの徹底。詳細は [docs/HARNESS_CHECKLIST.md](docs/HARNESS_CHECKLIST.md) を参照。

---

## 3. 公開監査 (Workflow/Deployment Audit)

アセットの取り込みから公開までのパイプラインが正しく機能しているかを検証する。

### 構成要素と実行コマンド

- **アセット再接続**: `scripts/artifacts/reconnect_unconnected_pngs.py`
  - 孤立した PNG を検出し、自動採番（`NNN_slug.png`）して DB に再接続する。
- **サイトビルド**: `task build` (`build.py`)
  - DB から静的な HTML ギャラリーを生成。
- **デプロイ検証**: `task verify` (`scripts/verify_pages.sh`)
  - GitHub Pages 等にデプロイされたフロントエンドが正常に応答し、"Prompt Vault" という文字列が含まれているかを確認。

---

## 運用上の10の鉄則 (Operational Principles)

Prompt Vault の全運用および監査は、以下の「鉄則」に従わなければならない。

### 3.1 監査システム自身の監査 (Audit Runtime Limits)

監査プロセスがリソースを無制限に消費したり、無限ループに陥ることを防ぐため、以下の制約を強制する。

- **制限閾値**:
  - 単一監査の最大実行時間（Runtime）
  - 最大トークン使用量（Token Usage）
  - 最大ファイルスキャン数（File Scan Count）
  - 最大ディレクトリ探索深度（Directory Traversal Depth）
  - 最大ツールコール回数（Tool Call Count）
  - 最大リトライ回数（Retry Count）
  - 最大サブプロセス起動数（Subprocess Count）
- **閾値超過時の対応**:
  - 直ちに **HARD FAIL** とし、監査を中断（Aborted）した上で、そこまでの部分的な結果（Partial Result）のみを保持する。

### 3.2 虚偽の成功検知 (Fake Success Detection)

LLM による「自己申告」や「雰囲気での成功」を一切排除する。

- **禁止事項**: 「修正しました」という自己申告、自然文による成功報告のみでの終了、ダウンストリームの検証を伴わない完了報告（例: "アップロード成功"、"生成完了" のみの自然文報告）。
- **必須検証項目 (Evidence-Based Verification)**:
  - 対象アセットの実在確認 (Artifact Exists)
  - ハッシュ値の更新確認 (Hash Changed)
  - タイムスタンプの更新確認 (Timestamp Updated)
  - 外部ベリファイア（スクリプト）のパス (Downstream Verifier Passes)
  - 外部 API またはリモートへの到達性確認 (Remote Reachable)
  - 意味のある差分（Semantic Diff）の存在

### 3.3 エビデンス階層 (Evidence Levels)

証拠の信頼性を以下の階層で定義し、高レベルの証拠を優先する。

- **LEVEL 0**: LLM による自然文の主張（信頼禁止）
- **LEVEL 1**: ファイルシステム上の実在確認（Filesystem Existence）
- **LEVEL 2**: スキーマおよびパーサーによるバリデーション（Schema/Parser Validation）
- **LEVEL 3**: 決定論的な実行プログラムによる検証（Deterministic Executable Verification）
- **LEVEL 4**: 外部 API による確認（External API Confirmation）
- **LEVEL 5**: システム間を跨ぐクロスバリデーション（Cross-System Verification）

*原則として、監査の PASS 判定は LEVEL 1 以上の決定論的な証拠にのみ依存させなければならない。*

### 3.4 修復ポリシー (Repair Policy)

監査システムは、ユーザーの明示的な許可なく広範囲な修復を行ってはならない。

- **許可される修復**: 局所的（Local）、可逆的（Reversible）、制約下（Bounded）の変更のみ。
- **禁止事項**: 全ファイル書き換え（Full Rewrite）、広範なリファクタリング（Broad Refactor）、再帰的な自動修復（Recursive Repair）、憶測に基づく自動修正（Speculative Auto-Fix）。

### 3.5 アセットの出自管理 (Artifact Provenance)

全アセット（Artifact）は以下のメタデータを保持し、追跡可能でなければならない。

- `generated_at` (生成日時)
- `source_template` (ソーステンプレート)
- `source_blocks` (ソースブロック)
- `generator_version` (生成器のバージョン)
- `model_identifier` (モデル識別子)
- `hash` (ハッシュ値)
- `registration_event` (登録イベント)

これらの出自情報（Provenance）が欠落しているアセットは、監査において **FAIL** と見なす。

### 3.6 境界ルールの強制 (Boundary Enforcement)

データの役割（責務）を厳格に分離し、カノニカルな境界を維持する。

- **Identity ブロック**:
  - 外見（髪、目、顔立ちなど）の不変メタデータに限定。
  - **含めてはならない情報**: 服装 (Outfit)、カメラ (Camera)、照明 (Lighting)、背景 (Background)、ポーズ (Pose)、感情 (Emotion)、季節 (Season)、場所 (Location)。
- **Situation ブロック**:
  - 状況や場面の記述のみ。
  - **含めてはならない情報**: Identity の核心情報。
- **Presentation ブロック**:
  - レンダリング手法、描画スタイル、レイアウトなどの提示方法に限定。
  - **含めてはならない情報**: 意味論的な設定や伝承 (Semantic Lore)。

### 3.7 決定論的なシリアライズ (Deterministic Serialization)

差分管理、キャッシュ効率、および再現性のために、データの保存形式を固定する。

- 監査対象の JSON/YAML データは以下を強制する。
  - キーの順序固定 (Stable Key Ordering)
  - UTF-8 正規化 (UTF-8 Normalized)
  - 決定論的な改行コード (Deterministic Newline)
  - 決定論的な空白/インデント (Deterministic Spacing)

### 3.8 LLM 使用制限 (LLM Usage Restrictions)

LLM の役割を「補助」に限定し、真実の決定権を与えない。

- **許可される用途**: 分類候補の生成 (Classification Candidate Generation)、要約 (Summarization)、警告・修正候補の提案 (Warning Suggestion)。
- **禁止される用途**: 正準真実（Canonical Truth）の生成、スキーマの自動修復 (Schema Repair)、実在確認の代行 (Existence Verification)、権威的判断 (Authority Judgement)。

### 3.9 インシデント分類 (Incident Taxonomy)

全インシデントは以下のいずれかに厳密に分類して記録する。

- `SCHEMA_FAIL`: スキーマ検証エラー
- `ORPHAN_ARTIFACT`: 紐付けのないアセットの存在
- `MISSING_REFERENCE`: DBから存在しないアセットへの参照
- `CANONICAL_DRIFT`: ロールや境界の逸脱
- `HALLUCINATED_REFERENCE`: 存在しないファイルやブロックの参照
- `FAKE_SUCCESS`: 証拠なき成功主張の検出
- `RUNTIME_OVERFLOW`: 実行時間またはリソース制限超過
- `TOKEN_OVERFLOW`: トークン上限超過
- `RECURSIVE_LOOP`: 無限再帰またはループの検知
- `TOOL_RUNAWAY`: ツールの暴走検知
- `CONFIG_DRIFT`: 設定ファイルの不整合
- `VERIFIER_FAILURE`: 検証プログラム自体のエラー

### 3.10 監査の禁止事項 (What Audit MUST NOT Do)

監査プロセスにおいて以下を厳禁とする。

- 推論による情報の補完 (No Inference)
- 意味・コンテキストの勝手な補完 (No Context Completion)
- データの自己生成 (No Data Generation)
- “自然だからOK” という主観的判断 (No "Looks Natural" Approval)
- リポジトリ全域の書き換え (No Repository-Wide Rewrite)
- 隠蔽されたフォールバックの使用 (No Hidden Fallback)
- 可変な真実の作成 (No Mutable Truth Creation)

---

## 監査の実行フロー

### デリバリー・パイプライン

新しいプロンプトやアセットを追加した際は、以下のコマンドを実行して一括監査を行う。

```bash
task deliver
```

このコマンドは内部的に以下の順序で監査を実行し、一つでも失敗すればビルドを中断する：

1. `literals-audit`
2. `validate`
3. `canonical-audit`
4. `artifacts-audit`
5. `build`

### 定期メンテナンス

- `task artifacts-audit` でアセットの接続状態を定期的に確認し、必要に応じて `scripts/artifacts/reconnect_unconnected_pngs.py` を実行する。
- [docs/HARNESS_CHECKLIST.md](docs/HARNESS_CHECKLIST.md) を半手動で確認し、ハーネスのドリフトを防止する。

## 参照ファイル

- **[Taskfile.yml](Taskfile.yml)**: 監査コマンドの定義。
- **[config.yaml](config.yaml)**: 監査対象リテラルやパスの定義。
- **[AGENTS.md](AGENTS.md)**: 開発時の思考ガイドライン。
- **[docs/HARNESS_CHECKLIST.md](docs/HARNESS_CHECKLIST.md)**: ハーネス監査のチェックリスト。