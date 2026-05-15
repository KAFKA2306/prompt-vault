# Prompt Vault Zero-Trust Workflow Specification

このドキュメントは、Prompt Vault の自律運用における「絶対的な整合性」を保証するための技術仕様である。

## 0. 入力解析と分岐 (Input Analysis & Branching)

エージェントは入力を受け取った直後、以下のルーティングに基づき走行ルートを決定する。

### ブランチ・ルーティング・テーブル

| Branch | 入力タイプ | 走行ルート (Phases) | 必須主要コマンド |
| :--- | :--- | :--- | :--- |
| **A. Ingestion** | 新規ソース (URL/PDF等) | 1 → 2 → 3 → 4 → 5 | `imagegen`, `register_...py`, `audit`, `verify` |
| **B. Maintenance** | メタデータ修正依頼 | 2 → 4 → 5 | `validate_db.py`, `audit_artifacts.py`, `verify_pages.sh` |
| **C. Replacement** | 画像・音声の差し替え | 1 → 3 → 4 → 5 | `imagegen`, `register_...py`, `audit_artifacts.py` |
| **D. Cleanup** | 監査エラー/未接続ファイル | 4 → 2 → 4 | `reconnect_unconnected_pngs.py`, `audit_artifacts.py` |

---

## 1. 生成系 (Generation Phase)

LLM はソースに基づきアセットと JSON ドラフトを準備する。

- **Input**: `URL`, `Tweet`, `Artifact maintenance request`
- **Output**:
  - 生成済みアセット (`/home/kafka/.codex/generated_images/*.png`)
  - 修正予定の JSON データ構造案
- **Exit Condition**: 生成完了の明示。

## 2. 検証系 (Validation Phase)

- **Command**: `python3 scripts/validate_db.py`, `python3 scripts/audit_db.py`
- **Exit Condition**: **PASS (Exit 0)**。FAIL 時は修復フェーズへ戻る。

## 3. 登録系 (Registration Phase)

- **Command**: `python3 scripts/register_generated_artifact.py --source <path> --title <title> ...`
- **Exit Condition**: スクリプトが正常終了し、`artifacts/` への物理登録と DB 追記が完了すること。

## 4. 監査系 (Audit Phase)

- **Command**: `python3 scripts/audit_artifacts.py`
- **Exit Condition**: `audit_artifacts.py` が **PASSED** を出力すること。

## 5. 公開系 (Publication Phase)

- **Command**: `python3 build.py`, `bash scripts/verify_pages.sh`
- **Exit Condition**: `verify_pages.sh` が **ok** を返し、かつ localhost (port 8787) での目視確認が完了すること。

---

## 7. Zero-Trust Execution Model

エージェントは非信頼対象である。以下のリスクを前提に設計する。

- `incomplete update`, `hallucinated success`, `skipped validation`, `fake registration`, `orphan generation`, `duplicate registration`, `invalid schema mutation`, `identity drift`, `silent overwrite`, `unintended deletion`, `task switching`, `context loss`, `false completion declaration`

すべての状態遷移はバリデータ群により外部検証されなければならない。

## 8. Canonical State Machine

**許可される状態遷移:**

`UNINITIALIZED` → `GENERATING` → `GENERATED_UNREGISTERED` → `VALIDATING` → `VALIDATED` → `REGISTERING` → `REGISTERED` → `AUDITING` → `AUDIT_PASSED` → `BUILDING` → `BUILT` → `VERIFYING` → `VERIFIED` → `PUBLISHED`

**禁止状態:**

`PUBLISHED_WITH_WARNINGS`, `PARTIALLY_REGISTERED`, `VALIDATION_SKIPPED`, `AUDIT_SKIPPED`, `MISSING_ARTIFACT_IGNORED`

## 9. Fail Closed Principle

バリデータが不明状態（timeout, partial stdout, malformed json, missing exit code）を返した場合、成功ではなく **FAIL** とみなす。

## 10. Mandatory Workflow State Persistence

会話履歴ではなく、`.tmp/workflow_state.json` 等に状態を保存する。

- **必須項目**: `workflow_id`, `branch`, `state`, `generated_assets`, `registered_assets`, `validation_results`, `audit_results`, `build_results`, `verify_results`, `blocking_reason`, `last_successful_phase`, `next_required_phase`, `created_at`, `updated_at`

## 11. Asset Lifecycle Rules

生成画像は必ず `registered`, `rejected`, `orphaned`, `deleted` のいずれかへ遷移させ、未分類状態を禁止する。

## 12. Registration Guarantees

登録処理は atomic operation とする。以下のいずれかが失敗した場合、全体を rollback する。

- `file copy`
- `hash generation`
- `DB update`
- `thumbnail generation`
- `metadata insertion`

## 13. Immutable Identity Guarantees

`character_kafka`, `kafka_identity_lock`, `speech_mode_kafka`, `kafka_visual_standard` は変更禁止。変更には明確な理由、diff ログ、人間による承認を必須とする。

## 14. Provenance Requirements

すべての artifact は以下を含む provenance を持たなければならない。

- `source_type`, `source_reference`, `generation_model`, `generation_prompt_hash`, `workflow_id`, `registered_by`, `timestamp`

## 15. Audit Requirements

リポジトリ全体に対し、以下の項目を検査する。

- `orphan assets`
- `missing linked files`
- `duplicate hashes`
- `invalid metadata`
- `invalid identity tags`
- `unresolved references`
- `broken pages`
- `invalid thumbnails`
- `dangling workflow states`
- `abandoned generated assets`

## 16. Repair Loop Enforcement

FAIL 検出 → classify error → repair → re-validate → re-audit → continue。再検証なき修復は禁止。

## 17. Human Escalation Conditions

以下の状態は人間に判断を仰ぐ。

- `identity conflict`
- `destructive overwrite`
- `ambiguous duplicate`
- `provenance unknown`
- `copyright uncertainty`
- `validator disagreement`
- `unresolved audit loop`

## 18. Completion Contract

エージェントは以下をすべて満たした場合のみ `COMPLETED` を宣言可能。

- `validate_db.py` exit 0
- `audit_db.py` exit 0
- `audit_artifacts.py` PASSED
- `build.py` exit 0
- `verify_pages.sh` ok
- `missing assets = 0`
- `orphans = 0`
- `duplicate links = 0`
- `workflow_state = VERIFIED`

## 19. Continuous Audit Mode

作業中も常に監査可能状態を維持する。以下の状態を禁止する。

- `temporary silent corruption`
- `hidden unregistered assets`
- `local-only references`
- `undocumented manual edits`

## 20. Zero-Trust Philosophy

目的は「LLM が正しく振る舞うことを期待すること」ではなく、**「LLM が間違ってもリポジトリが壊れないこと」**である。
