# 002 DB Design Review

> 最終決定は [ADR](../ADR/README.md) を見る。このメモは、何が問題だったかを短く残すための記録。

## 結論

`db/prompts.json` は今の規模なら使えるが、将来の事故を避けるために最低限の検証は入れた方がいい。

## 主な懸念

### 1. 壊れた参照を実行時まで見逃す

- `build.py` は JSON をそのまま読み込んでいる
- `static/app.js` は `blocks[blockId]` や `template.artifacts[0]` を直接参照している
- `blockId` の typo 1 個で、ビルド失敗ではなく壊れた表示になる

### 2. DB を丸ごと JS に埋め込んでいる

- `build.py` は `db/prompts.json` 全体を `app.js` に埋め込んでいる
- データが増えるほど初回転送量と再ビルド時間が増える
- 今は軽いが、増え続ける前提には弱い

### 3. UI が使っていないメタデータがある

- `steps`、`summary`、`notes`、複数 `artifacts` は DB にある
- 画面側は主に `title`、`purpose`、`kind`、`blocks` と最初の `artifact` しか使っていない
- 入れた情報が表示されず、死蔵フィールドが増えやすい

### 4. `kind` の分類がコード固定

- `kindLabels` は `static/app.js` に直書きされている
- 新しい `kind` を増やすたびに UI 修正が必要になる

### 5. いくつか未参照のブロックがある

- `slide_pack`
- `persona_sheet_vlog`
- `daily_work_sheet_vlog`

## 最小の改善方針

- スキーマを増やしすぎず、ビルド時に参照検証だけ入れる
- まずは `block.id` と `template.blocks` の整合性をチェックする
- 必要になったら、その次に relational 化を考える
