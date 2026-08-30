# Validation

Prompt Vault の完了判定は、LLMの自然文ではなく現在のvalidator・build・workflowの実行結果を使います。この文書は**実装済みの検証だけ**を説明します。将来構想のruntime budget、incident ledger、provenance framework等を実装済み仕様として記載しません。

## Command map

`Taskfile.yml` の現在の主要入口:

```text
task validate
  ├─ scripts/validate_db.py
  └─ scripts/audit_db.py

task artifacts-audit
  └─ scripts/audit_artifacts.py

task literals-audit
  └─ scripts/audit_literals.py

task build
  └─ build.py

task deliver
  ├─ literals-audit
  ├─ validate
  ├─ artifacts-audit
  └─ build
```

Taskの定義そのものは `Taskfile.yml` がauthorityです。

## `scripts/validate_db.py`

現在のhard validationの中心です。

実装上、主に次を確認します。

- 廃止済み `src` module importの再導入
- 移動済み KAFKA RESULTS script pathの再導入
- 移動済み artifact script pathの再導入
- `db/prompts.json` のPydantic parse
- artifact pathの重複条件
- root `artifacts/` の未接続fileをWARNINGとして報告
- `designs/*.svg` のcanonical design contract

Canonical SVGの詳細検証は `src/designs.py` が担当します。

## `scripts/audit_db.py`

Prompt DBのsemantic / reuse auditです。

主なERROR:

- unknown block reference
- duplicate block ID
- missing role
- single-responsibilityを明確に破る複数heading
- concrete panel marker
- pack blockの過大化

主なWARNING:

- empty non-generated template
- template block数過多
- unknown role
- mixed-roleらしいkeyword
- identity/style境界の疑わしい混在
- unused blocks
- broad pack naming

`--strict` を付けた場合はWARNINGでもfailします。通常の `task validate` ではstrict modeではありません。

このheuristic auditとPydantic schemaを同じものとして扱いません。

## `scripts/audit_artifacts.py`

`artifacts/` とPrompt DBの接続を検証します。

FAIL対象:

- root `artifacts/` にあるがDBから未接続
- DB参照があるが実fileがない
- `_orphaned` をDBが参照
- 同一artifactの重複参照

このauditは `assets/generated/` を対象にしません。SVG用generated assetは `src/designs.py` のimage reference validationで別に扱います。

## `scripts/audit_literals.py`

少数のstable documentation anchorを確認する単純なliteral auditです。Proseの内容が正しいことや、実装と一致すること自体を証明するvalidatorではありません。

このcheckへhost固有pathや過去ADRの文言を大量に固定しません。Current documentationの主要入口が消えていないことを確認する用途に限定します。

## Build validation

`build.py` 自身も入力を検証します。

- Prompt DBをPydantic modelとしてload
- Templateが存在しないblockを参照していないこと
- DBのartifact pathが実在すること
- required KAFKA SIGNAL public filesが存在すること
- canonical `designs/` と `assets/generated/` が存在すること

buildが生成した `dist/` は証拠の一つですが正本ではありません。

## Pull Request workflow

`.github/workflows/deploy.yml` はPRで、PR head SHAを明示的にcheckoutし、checkout SHAの一致を確認します。

現在のbuild jobでは次を実行します。

1. exact source SHA verification
2. Python / uv setup
3. artifact script entrypoint smoke check (`--help`)
4. canonical SVG font install
5. `scripts/validate_db.py`
6. `build.py`

PRではdeploy / verify-production jobはskipされます。

## Main deployment and production verification

`main` pushではbuild成功後にGitHub Pagesへdeployし、workflowが返したpage URLを使用してproductionを確認します。

現在のproduction verificationは、少なくとも次を実URLから取得・確認します。

- index pageの `Prompt Vault`
- canonical SVG design
- required font declaration
- generated image asset
- Issue #91のthis-week / next-week SVGとそのtext / asset reference

つまり、local build成功、PR CI成功、main production成功は別レベルの確認です。

## Evidence states

運用上は次の区別を使います。

- **OBSERVED**: tool / validator / remote responseで直接確認した
- **UNVERIFIED**: 必要な確認を実行していない、または結果が取れていない

推測だけでOBSERVEDへ昇格させません。複雑な独自taxonomyを追加する場合は、まず実装してからdocumentationへ反映します。

## Not currently enforced

過去のaudit documentsには、次のような構想が実装済みであるかのように記載されていましたが、現在のrepository-level validation contractとしては確認できません。

- token/tool/runtime budgetの汎用enforcement framework
- `data/incidents.jsonl` への全incident自動記録
- artifactごとのhash / generator_version / model_identifier等のprovenance必須schema
- LLM claimを自動分類・検証する5層audit engine
- VRChat負荷を検知して画像生成を停止するruntime monitor

これらが必要なら、documentationではなく実装とvalidatorを先に追加します。
