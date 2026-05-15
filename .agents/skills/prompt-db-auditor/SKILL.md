---
name: prompt-db-auditor
description: MUST use this skill to audit db/prompts.json canonical drift. Detect boundary violation, lifecycle contamination, generated/history/artifact mixing, pack black-boxing, identity leakage, duplicate/near-duplicate blocks, and force candidate classification from structured evidence only.
---


# prompt-db-auditor

この skill は `db/prompts.json` を「壊れているか」ではなく、「理想の canonical prompt database からどれだけ逸脱しているか」で監査する。特に generated / history / artifact memory が canonical layer に混入していないか、block の責務境界が破れていないか、pack が black box 化していないか、identity core が schema ではなく自然文だけで守られていないかを検出する。
自然文として読むのではなく、構造データとして扱う。
この skill は監査、報告、提案に加えて、`db/prompts.json` とこの skill 自身の安全な修正も担当する。

## 使う場面

- canonical structure との差分を確認したい
- block / template / artifact の参照関係を確認したい
- identity core の逸脱や重複を止めたい
- 変更を PASS / FAIL / UNVERIFIED / DEPRECATED / candidates で整理したい

## 基本方針

- 「良い感じ」「雰囲気が近い」を証拠にしない
- 問題探しではなく、理想状態との差分検出として扱う
- prompts.json を自然文ではなく構造データとして扱う
- canonical / generated / archived / experimental を同じ層に混ぜない
- template は reusable composition と generated snapshot を兼ねない
- generated_prompt を source of truth にしない。source of truth は blocks と参照整合性
- identity / emotion / rendering / negative / scene を分離して見る
- identity core は immutable に近いものとして扱い、髪・目・感情署名・空気感を editable zone から分ける
- pack は semantic black box にしない。必要なら責務を分割する
- artifact lifecycle と prompt lifecycle を同一視しない
- generated は状態・種類・出自のどれかを曖昧に残さず、監査対象として分けて見る
- 1 block = 1 責務、1 template = 1 目的
- 未検証を PASS にしない。render 未確認、artifact 未確認、drift 未確認は UNVERIFIED
- LLM 出力は信用せず、schema validation / reference validation / artifact audit / diff review を通す
- orphan / duplicate / deprecated を放置しない
- すぐ削除せず、PASS / FAIL / UNVERIFIED / DEPRECATED で状態管理する
- 長さより bounded / reusable / understandable を優先する
- PASS は「理想状態に一致」したときだけ付ける
- 監査結果は boundary violation を中心に、merge / split / archive / delete / canonical 候補を分けて出す
- 編集は canonical core を壊さない最小差分で行い、変更後は必ず再監査する
- 画像やファイルの移動は手でやらず、登録・再接続系のスクリプトを優先する

## 実行順

1. `src/models.py` で実際のスキーマを確認する
2. `python3 scripts/audit_db.py` で構造監査をする
3. `python3 scripts/validate_db.py` で artifact 参照を検証する
4. `python3 scripts/audit_artifacts.py` で root / `_orphaned` の接続を確認する
5. `git diff -- db/prompts.json .agents/skills/prompt-db-guard` で差分を確認する
6. 必要なときだけ `python3 build.py` を通して dist 側の整合性を見る

## 参照

- コマンドの意味と失敗条件: [references/commands.md](references/commands.md)
- 手動監査で FAIL 扱いする基準: [references/fail-conditions.md](references/fail-conditions.md)

## 出力形式

監査結果は次の構造で返す。

```markdown
## prompts.json Ideal-State Diff Audit

Status: PASS / FAIL / UNVERIFIED

### Canonical Target
- ...

### Boundary Violations
- ...

### Complexity Sources
- ...

### Split Candidates
- ...

### Merge Candidates
- ...

### Archive Candidates
- ...

### Delete Candidates
- ...

### Recommended Consolidation
- ...

### Do Not Touch
- ...

### Next Verification
- ...
```
