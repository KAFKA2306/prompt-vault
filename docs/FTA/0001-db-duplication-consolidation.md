# FTA 0001: DB重複整理レポート

対象: [`db/prompts.json`](../../db/prompts.json)

## 要約

このDBは、すでに「部品化されたグラフ」としてかなり良い形にある。  
ただし、今後の拡張では **ノード数そのもの** より、**系列の複製** と **意味が近いブロックの増殖** が保守コストを押し上げる。

結論としては、次の順で整理するのが妥当。

1. `variant_of` / `related` / `uses` の意味を固定する
2. 朝系のテンプレート群を1つの系列として束ねる
3. 旅行・読書・ゲーム・コスプレ系を共通雛形に寄せる
4. ブランド系とリプライ系をファミリー化する
5. 参照切れ検証を維持する

## 現状

実データ上の規模は以下。

- `blocks`: 102
- `templates`: 46
- `artifacts`: 3

カテゴリの偏りは次の通り。

- 背景: 22
- 形式・レイアウト: 22
- セリフ・フレーズ: 11
- ポーズ: 10
- 衣装: 9
- ブランド: 5

この分布から見て、DBの膨張リスクは「完全な新規概念の追加」よりも、**似た構造の派生を何度も手で増やすこと**にある。

## 重複が強い領域

### 1. 朝系

対象例:

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
- `morning_pose_*`
- `morning_background_*`
- `morning_scene_*`

問題:

- 1つの目的に対して、季節差分と状況差分が別系列で増えている
- 構成要素の差が小さく、テンプレートの重複が見えやすい
- 一覧・検索・保守のどれでも散らばりやすい

整理案:

- ベーステンプレートを1つ置く
- `season`、`scene`、`mood`、`text_mode` を差分として扱う
- 一覧は系列単位で束ねる

### 2. 旅行・読書・ゲーム・コスプレ系

対象例:

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

問題:

- 構造はほぼ同じで、差分は背景や衣装、文言だけ
- テンプレート名は用途ごとに分かれるが、実質的には同じ投稿フォーマットの亜種

整理案:

- 共通の投稿雛形を作る
- `scene` / `outfit` / `text_pack` を差し替え可能にする
- 各用途は「完成形」だけ残し、中間概念は部品へ戻す

### 3. ブランド系

対象例:

- `logo_only_sheet`
- `wordmark_sheet`
- `frame_sheet`
- `icon_mark_sheet`
- `orbit_logo_sheet`

問題:

- 同じブランド設計のバリエーションが、個別テンプレートとして並んでいる
- 将来の追加時に命名と役割がぶれやすい

整理案:

- `brand_identity_sheet` のような親を置く
- 種別を `logo_type` として持たせる
- 実例画像は `artifacts` で分岐する

### 4. リプライ・安全系

対象例:

- `reaction_image`
- `reply_stamp_sheet`
- `comment_reply_guide`
- `topic_redirect_banner`
- `safe_reply_pack`
- `chat_reply_pack`

問題:

- 返答、スタンプ、話題転換、安全リダイレクトが近いレイヤーにある
- 目的が似ているため、どのテンプレートを選ぶか迷いやすい

整理案:

- `reply_core_pack` を基準にする
- 出力形式だけを派生させる
- `safe_reply_pack` は安全応答専用として切り出す

### 5. 記録・まとめ系

対象例:

- `memory_note_board`
- `poststream_review_board`
- `archive_contact_sheet`
- `persona_sheet`
- `summary_sheet`
- `archive_index`
- `research_log_pack`
- `memory_pack`

問題:

- 記録、振り返り、回収、要約が近接していて、運用ルールが曖昧になりやすい

整理案:

- `memory_*` は記憶
- `review_*` は振り返り
- `archive_*` は回収・台帳
- `summary_*` は集約メモ

## 何を残すべきか

残すべきもの:

- `master_style`
- `character_kafka`
- `outfit_kafka`
- `negative_common`
- `text_style_jp`
- `effects_pack`
- 明確な役割を持つ `scene` / `pose` / `outfit`

削りにくいもの:

- 実例として価値がある `artifacts`
- 役割がはっきりした基礎ブロック

整理対象:

- 意味が近いテンプレートの複製
- `related` だけで親子っぽく見せているもの
- ほぼ同義の `pack` の乱立

## 推奨順位

1. `variant_of` / `related` / `uses` の定義を固定する
2. 朝系を系列化する
3. 旅行・読書・ゲーム系を共通雛形へ寄せる
4. ブランド系とリプライ系を束ねる
5. 一覧UIで系列表示を行う

## 実務上の判断基準

次のどれかに当てはまるなら、テンプレートは増やさず、既存系列に寄せる。

- 差分が背景だけ
- 差分が文言だけ
- 差分が衣装だけ
- 差分が季節だけ
- 差分がポーズだけ

次のどれかに当てはまるなら、新しいテンプレートとして残してよい。

- 出力の読み方が大きく変わる
- 画面構成が変わる
- 使う場面が明確に別
- 保守対象として分けた方が事故が減る

## まとめ

このDBは、今の段階では「ノード数が多すぎる」状態ではない。  
本当のリスクは、**似たテンプレートを増やし続けて系列を見失うこと**。

したがって、最初にやるべきことは削除ではなく、**系列の定義と共通雛形の固定** である。
