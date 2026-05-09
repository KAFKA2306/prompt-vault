# ADR 0010: Prompt Vault を prompt operating system として整理する

ステータス: 承認済み

## コンテキスト

`db/prompts.json` が大きくなり、単なる prompt 集ではなくなってきた。
いまの課題は、1つの prompt を増やすことそのものではなく、
**再利用・比較・評価・再生成がしやすい形に整理できているか**である。

現状の問題は次の通り。

- `prompts.json` が巨大で、diff review が重い
- `style`、`layout`、`workflow`、`log`、`check` が同じ平面に混ざりやすい
- 成果物の評価記録が弱く、keep / revise / reject が残りにくい
- artifact のメタデータが `path` と `title` だけで弱い
- model / seed / params が分離されず、再現性が落ちる
- negative prompt の分類が体系化されていない
- naming drift が起きやすい
- review workflow の最小単位が固定されていない

この repo は「prompt collection」ではなく、
**prompt operating system** として扱うべき段階に入っている。

## 決定事項

### 1. データを用途階層で分ける

`db/prompts.json` の中身は、少なくとも次の用途で分けて考える。

- `base` / `character`
- `composition` / `layout`
- `rendering`
- `typography` / `text`
- `negative`
- `workflow`
- `review`
- `memory` / `log`
- `model` / `params`

意味が違うものを同じ階層に置かない。

### 2. 1 change = 1 intent = 1 output = 1 score にする

レビュー可能な最小単位は次の形に固定する。

```json
{
  "run_id": "",
  "block_ids": [],
  "intent": "",
  "model": "",
  "seed": "",
  "params": {},
  "artifact": "",
  "scores": {
    "clarity": 0,
    "identity": 0,
    "text_readability": 0,
    "artifact_noise": 0
  },
  "decision": "keep | revise | reject"
}
```

これは「何を変えたか」と「何が出たか」と「どう評価したか」を1つにまとめるための最小単位である。

### 3. artifact はメタデータ付きで扱う

画像は `path` と `title` だけで終わらせない。
少なくとも次の情報を残す。

- `run_id`
- `model`
- `seed`
- `params`
- `prompt_hash`
- `decision`
- `scores`

これにより、あとで同じ結果を再現しやすくする。

### 4. negative prompt は taxonomy 化する

`negative_common` だけで済ませず、意味ごとに分ける。

例:

- `negative_anatomy`
- `negative_skin`
- `negative_shadow`
- `negative_color`
- `negative_layout`
- `negative_text`
- `negative_artifact`

### 5. 命名規則を揃える

`*_viz`、`*_pack`、`*_check`、`*_only_kafka` などの接尾辞は、
意味の違いを表すルールとして固定する。

- `*_layout`: 構図・画面構成
- `*_pack`: 再利用可能なテキストや属性の束
- `*_check`: 検証用
- `*_viz`: 見せることが主目的の表示系
- `*_log`: 記録系
- `*_review`: 評価系

命名だけで役割が判別できるようにする。

### 6. model / params を分離する

`SDXL`、`Niji`、`GPT-image` など、モデルごとの効き方を前提に分ける。
`model`、`params`、`seed` はレビュー記録に明示的に残す。

### 7. skills は「現在の標準」を参照する

`prompt-vault-workflow` は、
- 既存の Prompt Vault prompt を基準にする
- `kafka_visual_standard` と `097_rendering_quality_check_contrast.png` を Kafka の標準参照にする
- 画像を正式な資産にする場合は、`scripts/register_generated_artifact.py` で `artifacts/` と DB を同時に揃える
- その後に `build.py` で `dist/artifacts/` が一致していることを確認する
- review 可能な記録を残す

という運用にする。

## 理由

- prompt が増えても drift しにくくなる
- compare / review / regenerate がしやすくなる
- 人間が読める prompt と機械が最適化しやすい prompt を分けやすくなる
- 後から「何が良かったか」を学習しやすくなる
- `db/prompts.json` が巨大化しても、意味のある単位で扱いやすくなる

## 運用方針

1. 新しい prompt を足す前に、用途階層を決める。
2. 1つの change に対して、1つの intent と 1つの output を残す。
3. artifact には model / seed / params / score を残す。
4. negative は taxonomy に分ける。
5. 新しい命名は、接尾辞だけで用途が分かるようにする。
6. `prompt-vault-workflow` は標準参照を優先し、必要なら新しい型を作る。

## 結論

Prompt Vault は prompt の置き場ではなく、
prompt を作り、比較し、再利用し、改善するための operating system である。
