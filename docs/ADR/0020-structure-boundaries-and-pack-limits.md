# ADR 0020: 構造境界と pack / template の上限を固定する

## ステータス

承認済み

## コンテキスト

`db/prompts.json` には、見た目・用途・記憶・固定特徴が混在しやすい。

特に次の問題が繰り返し起きる。

- `character_kafka`、`kafka_identity_lock`、`speech_mode_kafka` に季節や用途が混ざる
- `morning_*`、`gaming_*`、`news_*`、`cosplay_*` が常時読み込み前提になる
- `pack` が大きくなりすぎる
- `template.blocks` が長くなりすぎる
- 似た block が増える

## 決定事項

### 1. identity block は編集禁止領域とする

次の block は Kafka の不変特徴を保持する。

- `character_kafka`
- `kafka_identity_lock`
- `speech_mode_kafka`

ここには季節、服、投稿用途を入れない。

### 2. situation block は一時注入だけとする

次の block 群は状況用とする。

- `morning_*`
- `gaming_*`
- `news_*`
- `cosplay_*`

常時読み込みにしない。

### 3. pack の上限を固定する

`pack` は最大 5 blocks 相当までとする。

6 個以上は分割候補。
10 個以上は必ず分割する。

### 4. `template.blocks` の上限を固定する

`template.blocks` は最大 8 blocks とする。

超えた場合は pack 化か template 分割を行う。

### 5. 1 block は 1 主役割とする

1 block には、背景、服、ポーズ、感情、光を同時に詰め込まない。

### 6. 原子化しすぎない

単独差し替えしない要素は分けない。

「朝の空気感」程度は situation に残す。

### 7. 命名規則を固定する

次の接頭辞を使う。

- `identity_*`
- `speech_*`
- `visual_*`
- `outfit_*`
- `pose_*`
- `background_*`
- `lighting_*`
- `layout_*`
- `text_*`
- `situation_*`
- `pack_*`
- `template_*`

### 8. 重複 block を増やさない

新規 block を追加する前に既存 block を検索する。

似ている場合は既存 block を優先する。

### 9. style と identity を混ぜない

`style` は描画品質、余白、色、線を表す。

`identity` は Kafka 本人の不変特徴を表す。

### 10. template は用途だけを書く

template には用途を書く。

見た目指定は block 側に寄せる。

### 11. artifact path は参照情報として扱う

artifact path は生成物への接続情報とする。

block 本体の意味定義には混ぜない。

## 理由

- identity と situation の境界が明確になる
- pack の肥大化を止められる
- template の長文化を止められる
- 似た block の重複を減らせる
- block と template の責務が分かれる

## 影響

- `db/prompts.json` の編集基準が明確になる
- 監査で pack サイズと template 長を確認できる
- 新規 block の追加前に既存検索が必須になる

## 結論

identity は固定、situation は注入、pack は小さく、template は用途だけ。
