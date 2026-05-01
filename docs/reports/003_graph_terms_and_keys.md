# 003 Graph Terms And Keys

> 最終決定は [ADR](../ADR/README.md) を見る。このメモは、用語と追加キーの検討過程を残す記録。

## 方針

`db/prompts.json` は壊さず、graph 的に考えやすい最小の追加キーだけ入れる。

## 用語対応

- `block` -> `node`
- `template` -> `recipe`
- `templates.blocks` -> `uses`
- `tags` -> `labels`
- `kind` -> `type`
- `artifacts` -> `outputs`
- `summary` -> `intent`
- `steps` -> `path`
- `notes` -> `remarks`

## 追加するキー

### blocks

- `aliases`
- `related`
- `variant_of`

### templates

- `uses`
- `labels`
- `outputs`

## 最小の使い方

- `blocks` は原子部品のまま使う
- `templates` はレシピのまま使う
- `uses` は既存の `blocks` と同じ参照先を持つ
- `related` は横断検索の補助にだけ使う
- `variant_of` は派生元の明示にだけ使う

## これで増える認識

- 何が部品か
- 何が派生か
- 何が再利用されるか
- 何が検索語か

## これ以上はやらない

- まだ Graph DB は入れない
- まだ `db` を分割しない
- まだ既存キー名を全面変更しない

## 実践したもの

- 一部の `blocks` に `aliases` / `related` / `variant_of` を追加した
- 一部の `templates` に `uses` を追加した
- 画面側で `uses` を見せるようにした
