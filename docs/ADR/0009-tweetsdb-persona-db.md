# ADR 0009: tweetsdb を人格再利用 DB として扱う

ステータス: 承認済み

## コンテキスト

このリポジトリの `scripts/tweetsdb.py` は、ただツイートを分類するためのものではない。
目的は、Kafka のツイート群から次のような特徴を取り出して、あとで再利用できる形にすることである。

- 観察のしかた
- 言い方のくせ
- 話題の移り方
- 感情の出方
- 画像生成の発想
- ツールへの反応
- VRChat / AI / 生活の感覚

つまり、`tweetsdb` は「ツイート整理DB」ではなく、
**Kafka の生成元を構造化して、プロンプトや文体に戻せる DB** として扱う。

## 決定事項

- 分類はなるべく実ツイートの根拠で行う。
- 根拠がないものは、無理に topic を付けない。
- fallback の topic は使わない。
- `matched_keywords` を残す。
- `topic_evidence` を残す。
- `classification_confidence` を残す。
- `owner_signal` を残す。
- `reuse_type` を残す。
- `quality_flags` を残す。
- `schema_version` と `source_archive_id` を残す。
- 画像生成用の seed は、ふわっとした一般文ではなく、実ツイートから読める内容に寄せる。

## ルール

- `reply`、`retweet`、`quote`、`link-only` は同じ粒度で混ぜすぎない。
- 他人への反応と、自分の発信は分けて扱う。
- `vrchat` のような広い topic は、必要なら `vrchat-social` や `vrchat-technical` のように分ける。
- `vrchat-events`、`vrchat-worlds`、`vrchat-avatar-mod`、`vrchat-mobile` のような具体 topic を優先する。
- `topic` は「分類名」だけでなく、「再利用の入口」として使う。
- 推測や雰囲気だけの説明は書かない。

## ねらい

この DB でやりたいことは、次の再利用である。

- プロンプト生成
- キャラクター性の再現
- 文体の再現
- 画像生成 seed
- 発想補助
- 長期人格圧縮
- RAG 素材

## 実装方針

1. ツイートを読む
2. 形態素や正規化した文字列を見る
3. 実際に当たった語を記録する
4. topic を付ける
5. その topic を何に再利用できるかを記録する
6. 最後に latent profile を作る

## これで避けたいこと

- なんとなくの分類
- 似ているようで意味が違う topic の混在
- 後から理由が追えない DB
- 画像生成や文体再現に使いにくい抽象ラベル

## 結論

`tweetsdb` は Twitter の整理表ではない。
Kafka の癖を、あとで再生成できる形で保存するための基盤である。
