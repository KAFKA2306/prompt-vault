---
name: prompt-vault-workflow
description: Prompt Vault の素材取り込みとアセット管理を「状態遷移（FSM）」として扱う skill。`db/prompts.json` の編集、`validate_db.py` / `audit_db.py` の検証、`register_generated_artifact.py` による画像登録、`reconnect_unconnected_pngs.py` による未接続 PNG の再接続、`audit_artifacts.py` の監査、`build.py` と `verify_pages.sh` の公開前確認、DB とアセットの整合性修正では必ず使う。
---

# Prompt Vault Workflow (FSM Edition)

この skill は、Prompt Vault 更新を「作業手順」ではなく「状態遷移」として定義する。エージェントは自ら完成を推定してはならず、定義された Validator のみが成功を決定する。

## 1. 状態遷移フロー (Phases)

エージェントは以下の順序で状態を遷移させる。前工程の「完了証拠」がない状態での次工程への進入は厳禁。

1. **生成系 (Generation)**: LLM による JSON 案・画像・音声の作成。
2. **検証系 (Validation)**: 整合性チェック。`validate_db.py`, `audit_db.py` を実行。
3. **登録系 (Registration)**: 決定論的スクリプトによる状態確定。`register_generated_artifact.py` を実行。
4. **監査系 (Audit)**: アセット整合性チェック。`audit_artifacts.py` を実行。
5. **公開系 (Publication)**: ビルドと最終検証。`build.py`, `verify_pages.sh` を実行。

## 2. 状態遷移条件 (Transition Conditions)

| 遷移 | 条件 (Entry Guard) | 必須エビデンス (Evidence) |
| :--- | :--- | :--- |
| 生成 -> 検証 | 成果物（.png / .wav / DB修正案）の存在 | 修正箇所の明示 |
| 検証 -> 登録 | スキーマ・整合性のパス | `validate_db.py` PASS |
| 登録 -> 監査 | 物理登録の完了 | `register_...py` の成功ログ |
| 監査 -> 公開 | 孤立・欠損アセット 0 | `audit_artifacts.py` PASS (Missing=0) |
| 公開 -> 完了 | デプロイ構造の正常性 | `verify_pages.sh` PASS |

## 3. 修復ループ (Repair Loop)

いずれかの工程で **FAIL** を検出した場合、エージェントは直ちに遷移を停止し、以下の修復フェーズへ入らなければならない。

- **FAIL 検出**: 推定によるスキップ、Fake Success の報告を禁止する。
- **修復**: ログから原因を特定し、生成系（Step 1）からやり直す。
- **再検証**: 修復後、再度同じバリデータをパスするまで次工程へ進んではならない。

## 4. 厳格ルール

- **手動登録禁止**: `artifacts/` へのコピーや DB への追記を手動で行ってはならない。必ず登録スクリプトを通す。
- **未検証状態の禁止**: バリデータを通していない状態で `dist/` を更新してはならない。
- **成功推定の禁止**: 「エラーが出ていないから成功」は認められない。必ずスクリプトの戻り値を確認する。
- **Identity Lock**: `character_kafka` 等のアイデンティティが維持されているか、各工程で再確認する。

## 5. 詳細仕様

各工程の具体的な条件とコマンドは `references/workflow.md` を参照せよ。
