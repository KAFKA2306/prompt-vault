# Operations

この文書は Prompt Vault の日常操作をまとめます。コマンドの正本は `Taskfile.yml` と `scripts/` です。外部ツール固有の絶対パスは repository の恒久的な操作契約にしません。

## Setup

必要環境:

- Python 3.11
- `uv`
- Git
- canonical SVGを検証する環境では `fc-match` と必要font

```bash
uv sync
```

## Local UI

```bash
task run
```

または:

```bash
uv run app.py
```

標準設定は `config.yaml` がauthorityです。

## Static build

```bash
task build
```

生成先は `dist/` です。`dist/` は派生物なので直接修正しません。

## Register a generated artifact

生成済みPNG/WAVを正式なDB接続artifactとして採用する標準入口:

```bash
uv run python scripts/artifacts/register_generated_artifact.py \
  --source /path/to/generated.png \
  --title "Artifact title" \
  --purpose "Purpose" \
  --summary "Summary"
```

現在の登録scriptは次を行います。

1. sourceの存在と `.png` / `.wav` を確認
2. `src/artifacts.py` の採番・slug規則で `artifacts/NNN_slug.ext` を作成
3. `db/prompts.json` に `kind=generated` のTemplateを追加
4. `created_at`、必要に応じてprompt/voice fieldsを記録
5. 通常は `build.py` と `scripts/validate_db.py` を実行

`--skip-build` は存在しますが、delivery完了条件を省略するための成功fallbackではありません。後で必要な検証を別途実行します。

主要optionはscriptの `--help` をauthorityとします。

```bash
uv run python scripts/artifacts/register_generated_artifact.py --help
```

## Reconnect unconnected PNGs

既存未接続PNGを扱う入口:

```bash
uv run python scripts/artifacts/reconnect_unconnected_pngs.py --dry-run
```

結果を確認してから必要な場合のみ実行します。

```bash
uv run python scripts/artifacts/reconnect_unconnected_pngs.py
```

新規artifact登録と既存未接続artifactの修復を同じ操作として扱いません。

## Canonical SVG designs

固定サイズ2D成果物では `designs/*.svg` を編集可能な正本として使用できます。

- textは `<text>` として保持
- concrete fontを `font-family` で指定
- layoutは座標・shape・pathとして保持
- generated illustration/photoは `assets/generated/` へ置き、SVGの `<image>` からrepository相対参照
- render済み画像だけを唯一の正本にしない

検証は `task validate` の中で `src/designs.py` を通ります。

## Validation commands

通常の変更:

```bash
task validate
task artifacts-audit
task build
```

全体delivery:

```bash
task deliver
```

詳細は [VALIDATION.md](VALIDATION.md) を参照してください。

## Pull Request delivery

1. current `main` からtask用branchを作る
2. current implementation / data / validatorを確認して変更
3. exact PR head SHA のCIを確認
4. CI success後に、その確認済みheadをmerge
5. merge後の `main` をread-back
6. 公開物に影響する場合はmain pushのdeployとproduction verificationを確認

PRではGitHub Pagesのdeploy jobはskipされます。PR build成功をproduction成功とは扱いません。

## Production

`.github/workflows/deploy.yml` は `main` push時に静的siteをGitHub Pagesへdeployし、取得したpage URLに対してproduction verificationを実行します。

Cloudflare Pages / Functionは別経路です。GitHub Pages workflowのsuccessだけでCloudflare側の状態まで確認済みとはしません。

## KAFKA RESULTS and specialized workflows

KAFKA RESULTS系scriptは `scripts/results/` にまとまっています。各workflowの詳細なデータ契約は `docs/results-*.md` とworkflow実装を参照してください。

Weekly macro等の個別運用は `docs/ops/` に置きます。repository全体の基本操作と個別運用を同じ文書へ混ぜません。

## Documentation changes

Documentationの変更でも、current implementationと矛盾しないことを確認します。ADRやplanに現在仕様をコピーして正本化しません。Current documentationの入口は [README.md](README.md) です。
