---
name: prompt-vault-workflow
description: Prompt Vault の生成アセット登録と DB 更新を、現在の実装・validator・delivery contract に沿って行う skill。
---

# Prompt Vault Workflow

`AGENTS.md` と現在の実装を正本とする。過去の一括migration、host固有path、会話上の状態機械を恒久手順にしない。

## Route

### 生成アセットを登録する

1. 登録する PNG / WAV の実体を確認する。
2. `scripts/artifacts/register_generated_artifact.py` で `artifacts/` と `db/prompts.json` を同時に更新する。
3. `scripts/audit_artifacts.py` で接続を確認する。

### DBだけを変更する

- `db/prompts.json` と `src/prompt_db.py` の現行schemaに従う。
- `scripts/validate_db.py` と `scripts/audit_db.py` を通す。

### 未接続アセットを扱う

- まず `scripts/audit_artifacts.py` で実状態を確認する。
- 残す必要がある実アセットは通常の登録経路へ戻す。
- 参照がなく不要と確認できたものは削除する。
- 特定ファイル名を列挙した一回限りの再接続scriptを正本にしない。

## Validation

全体変更は既存Taskを使う。

```bash
task deliver
```

PRではexact head SHAのCIを確認し、merge後は`main`をread-backする。公開物に影響する場合はproduction verificationまで確認する。確認できない状態を成功扱いにしない。
