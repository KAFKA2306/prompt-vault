# Prompt DB Schema

`db/prompts.json` の人間向け説明です。**型の正本は `src/prompt_db.py`** です。この文書と実装が食い違う場合は、Pydantic modelとvalidatorを確認して文書を更新します。

Prompt DBは次の2配列を持ちます。

```json
{
  "blocks": [],
  "templates": []
}
```

## `Artifact`

`Template.artifacts` の要素です。

| field | type | required | default |
| --- | --- | --- | --- |
| `path` | string | yes | — |
| `title` | string | no | `""` |

現在のPydantic schemaにhash、model identifier、generator version等のprovenance fieldはありません。それらを必須仕様として扱う場合は、先にschemaを実装します。

## `Block`

再利用可能なprompt構成要素です。

| field | type | required | default |
| --- | --- | --- | --- |
| `id` | string | yes | — |
| `title` | string | yes | — |
| `content` | string | yes | — |
| `role` | string | yes | — |
| `category` | string | no | `""` |

`role` はPydantic上は任意文字列ではなく「必須のstring」ですが、Literal enumには固定されていません。`scripts/audit_db.py` がknown rolesを持ち、unknown roleをWARNINGとして扱います。

Semanticなsingle-responsibility、identity/style境界、pack size等はschemaではなく`audit_db.py`のaudit規則です。

## `Template`

Blockの組み合わせ、用途、生成記録、artifact接続を表します。

| field | type | required | default |
| --- | --- | --- | --- |
| `id` | string | yes | — |
| `title` | string | yes | — |
| `blocks` | list[string] | no | `[]` |
| `kind` | Literal | no | `"social"` |
| `purpose` | string | no | `""` |
| `summary` | string | no | `""` |
| `artifacts` | list[Artifact] | no | `[]` |
| `generated_prompt` | string or null | no | `null` |
| `voice_caption` | string or null | no | `null` |
| `voice_script` | string or null | no | `null` |
| `created_at` | string or null | no | `null` |

### `kind`

現在 `src/prompt_db.py` が受理する値は11種類です。

```text
announcement
brand
comic
design_sheet
news
reaction
sheet
social
stamp
system
generated
```

`generated` は生成artifactの登録記録等に使用されます。`audit_db.py` は `kind != generated` のTemplateでblocksが空の場合にWARNINGを出します。

## Legacy migration

`PromptDB` はload時にlegacy top-level `generated_prompts` が存在すれば、未登録IDを `templates` へ移し、`kind="generated"` として扱うmigrationを持ちます。

これはload-time compatibilityです。legacy fieldを新規データの正本として使う理由にはしません。

## Reference integrity

Schema parseだけではすべての参照整合性を保証しません。現在は複数の層で確認します。

- `build.py`: Templateのblock IDが存在すること、artifact pathが実在すること
- `scripts/audit_db.py`: unknown block reference、duplicate block ID等
- `scripts/audit_artifacts.py`: DBと`artifacts/`の接続
- `scripts/validate_db.py`: Pydantic parse、duplicate artifact条件、canonical SVG等

詳細は [VALIDATION.md](VALIDATION.md) を参照してください。

## Generated artifact registration

標準登録scriptは現在 `.png` と `.wav` をsourceとして受け付けます。

```bash
uv run python scripts/artifacts/register_generated_artifact.py --help
```

このscriptは `src/artifacts.py` の採番・slug規則を使い、`artifacts/NNN_slug.ext` を作成して `kind=generated` のTemplateを追加します。

Pydantic `Artifact.path` 自体は拡張子をLiteral制約していません。登録入口の対応formatとschemaの型制約を混同しません。

## Example

### Reusable template

```json
{
  "id": "kafka_stamp_01",
  "title": "Kafka stamp",
  "blocks": ["master_style", "character_kafka", "layout_stamp"],
  "kind": "stamp",
  "summary": "Reusable stamp composition"
}
```

### Generated record

```json
{
  "id": "gen_20260830_120000",
  "title": "Generated example",
  "blocks": ["master_style", "character_kafka"],
  "kind": "generated",
  "purpose": "Example",
  "summary": "Generated result",
  "artifacts": [
    {
      "path": "artifacts/321_generated_example.png",
      "title": "Generated example"
    }
  ],
  "generated_prompt": "...",
  "voice_caption": null,
  "voice_script": null,
  "created_at": "2026-08-30T12:00:00+09:00"
}
```

## SVG designs are not Prompt DB records

`designs/*.svg` と `assets/generated/` はPrompt DB schemaとは別のcanonical pathです。

- Prompt DB: prompt構造とDB接続artifact
- SVG: fixed-size 2Dのlayout/text/font/shape構造
- `assets/generated/`: SVGから参照するimage asset

SVG contractは `src/designs.py` がauthorityです。詳細は [ARCHITECTURE.md](ARCHITECTURE.md) を参照してください。

## Do not duplicate schema in Markdown

新しいfield、`kind`、validation ruleを追加した場合は、まず実装を変更します。この文書は実装変更後に人間向け説明として追従させます。ADRやplanへ同じfield一覧をcurrent contractとして複製しません。
