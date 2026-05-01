# FTA 0002: DB再編提案

対象: [`db/prompts.json`](../../db/prompts.json)

## 目的

この提案は、既存の `blocks` と `templates` を壊さずに、今後の拡張で重複が増えにくい形へ寄せるためのもの。

狙いは次の3点。

1. 似たテンプレートの増殖を止める
2. 役割が近いブロックの意味を固定する
3. 一覧UIで系列を見失わないようにする

## 現行の設計評価

現状の設計は、次の点で良い。

- `master_style` のような共通基盤がある
- 属性や軽いメタデータをノード化しすぎていない
- `variant_of`、`related`、`aliases` で再利用の手がかりを持っている
- `artifacts` が少なく、参照ズレの管理コストがまだ低い

一方で、以下は膨らみやすい。

- 朝系の季節・状況バリエーション
- 旅行、読書、ゲーム、コスプレ系の投稿雛形
- ブランド系の見た目違い
- リプライ、反応、話題転換の近接領域

## 再編の原則

### 1. テンプレートは「完成形」に寄せる

テンプレートは、ユーザーがそのまま選ぶ完成形だけを残す。  
細かい差分はブロック側に逃がす。

例:

- 良い: `morning_tweet_spring`
- さらに良い: `morning_post` + `season=spring`

### 2. ブロックは「再利用できる意味単位」に寄せる

ブロックは、用途が一目で分かる単位だけ残す。

例:

- `morning_pose_*`
- `morning_scene_*`
- `travel_bg_*`
- `reading_scene_*`

### 3. 近い概念は1語に統一する

今後の追加時に迷わないよう、似た意味の語を増やさない。

例:

- `pack` は補助文言やルールの塊
- `layout` は配置ルール
- `scene` は背景・状況
- `pose` は身体の向き
- `outfit` は衣装

### 4. 親子関係を曖昧にしない

`variant_of` は親子関係だけに使う。  
`related` は近い参照だけに使う。  
`uses` を残すなら、`blocks` との役割差を明文化する。

## 再編案

### A. 朝系

#### 現行

- `morning_tweet_spring`
- `morning_tweet_summer`
- `morning_tweet_autumn`
- `morning_tweet_winter`
- `morning_tweet_window`
- `morning_tweet_coffee`
- `morning_tweet_commute`
- `morning_tweet_rain`
- `morning_tweet_sleepy`
- `morning_tweet_index`

#### 提案

ベース:

- `morning_post`

差分軸:

- `season`
- `scene`
- `pose`
- `mood`
- `text_mode`

想定例:

- `morning_post` + `season=spring`
- `morning_post` + `scene=window`
- `morning_post` + `mood=sleepy`

対応方針:

- 季節別テンプレートは、ベース + 変数に寄せる
- 状況別テンプレートは、sceneブロックで切る
- `morning_tweet_index` は一覧専用として残す

### B. 旅行・読書・ゲーム・コスプレ

#### 現行

- `travel_kyoto_post`
- `travel_tokyo_post`
- `travel_okinawa_post`
- `travel_hokkaido_post`
- `reading_post_general`
- `reading_post_seaside`
- `reading_post_anne`
- `cosplay_post`
- `poker_post`
- `cardgame_post`
- `joinwars_post`

#### 提案

共通雛形:

- `social_scene_post`

共通可変項目:

- `scene`
- `outfit`
- `pose`
- `text_pack`
- `layout`

対応方針:

- 旅行は `travel_bg_*` を scene として扱う
- 読書は `reading_scene_*` と `reading_pose_kafka` を組み合わせる
- ゲーム系は、ルール説明ではなく「投稿見た目」を共通化する

### C. ブランド

#### 現行

- `logo_only_sheet`
- `wordmark_sheet`
- `frame_sheet`
- `icon_mark_sheet`
- `orbit_logo_sheet`

#### 提案

ベース:

- `brand_identity_sheet`

差分軸:

- `logo_type`
- `composition`
- `negative_space`

対応方針:

- 形の違いをテンプレート名に埋め込まない
- 実例画像は `artifacts` で分ける

### D. リプライ・反応・安全

#### 現行

- `reaction_image`
- `reply_stamp_sheet`
- `comment_reply_guide`
- `topic_redirect_banner`
- `safe_reply_pack`
- `chat_reply_pack`

#### 提案

基盤:

- `reply_core_pack`

出力形式:

- `reaction_card`
- `reply_stamp_sheet`
- `redirect_banner`

動作ルール:

- `safe_reply_pack` は安全応答専用
- `chat_reply_pack` は自然な返答専用
- `topic_redirect_banner` は表示用テンプレートに限定

### E. 記録・まとめ・回収

#### 現行

- `memory_note_board`
- `poststream_review_board`
- `archive_contact_sheet`
- `persona_sheet`
- `summary_sheet`
- `archive_index`
- `research_log_pack`
- `memory_pack`

#### 提案

整理軸:

- `memory_*` = 記憶
- `review_*` = 振り返り
- `archive_*` = 回収・台帳
- `summary_*` = 要約

## 具体的な移行ルール

### ルール1: 近似テンプレートは統合候補にする

次の条件を満たす場合、別テンプレートを作らず統合する。

- 差分が背景だけ
- 差分が文言だけ
- 差分が季節だけ
- 差分がポーズだけ

### ルール2: 新規IDは「意味が増えるときだけ」

新しいIDを切る条件は次のいずれか。

- 画面構成が変わる
- クエリの見方が変わる
- 使う場面が別物になる
- 保守を分けないと事故が起きる

### ルール3: 補助メタを増やす前に系列を整理する

`family` や `domain` のようなメタを追加する前に、まずテンプレートの重複を減らす。  
メタだけ増やすと、一覧は見やすくなっても本体は太る。

## 現行IDの扱い

以下は残してよい中核ID。

- `master_style`
- `character_kafka`
- `outfit_kafka`
- `negative_common`
- `text_style_jp`
- `effects_pack`
- `speech_mode_kafka`
- `persona_pack`

以下は系列の親に寄せる候補。

- `morning_tweet_*`
- `travel_*`
- `reading_*`
- `cosplay_*`
- `poker_*`
- `cardgame_*`
- `joinwars_*`
- `logo_*`
- `reply_*`
- `archive_*`
- `memory_*`

## 実装順

1. `variant_of` / `related` / `uses` の意味を確定する
2. 朝系を1系列に束ねる
3. 旅行・読書・ゲーム系を共通雛形へ寄せる
4. ブランド系を統合する
5. リプライ・安全系をまとめる
6. 一覧UIで系列表示を行う

## 結論

このDBに必要なのは、ノード削減より先に **系列の圧縮**。  
今の構造は壊すべきではないが、似たテンプレートを増やし続ける前に、ベースと差分の境界をはっきりさせるべき。
