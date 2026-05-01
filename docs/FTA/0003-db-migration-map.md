# FTA 0003: DB移行マップ

対象: [`db/prompts.json`](../../db/prompts.json)

## 目的

この移行マップは、現行のテンプレートとブロックをどの系列へ寄せるかを、作業単位で判断しやすくするためのもの。

ここでの方針は「削除」ではなく「統合先を決める」こと。

## 方針

1. 完全に意味が同じものは、親系列に寄せる
2. 差分が小さいものは、テンプレートを統合して差分をブロック化する
3. UI上で独立して見せたいものだけ、別IDとして残す
4. 画像実例は `artifacts` に残し、参照だけを移す

## テンプレート移行マップ

### 朝系

| 現行ID | 寄せ先 | 備考 |
|---|---|---|
| `morning_tweet_spring` | `morning_post` | 季節差分を属性化 |
| `morning_tweet_summer` | `morning_post` | 季節差分を属性化 |
| `morning_tweet_autumn` | `morning_post` | 季節差分を属性化 |
| `morning_tweet_winter` | `morning_post` | 季節差分を属性化 |
| `morning_tweet_window` | `morning_post` | scene 差分として扱う |
| `morning_tweet_coffee` | `morning_post` | scene 差分として扱う |
| `morning_tweet_commute` | `morning_post` | scene 差分として扱う |
| `morning_tweet_rain` | `morning_post` | scene 差分として扱う |
| `morning_tweet_sleepy` | `morning_post` | mood 差分として扱う |
| `morning_tweet_index` | `morning_post_index` | 一覧専用として残す |

### 旅行・読書・ゲーム・コスプレ

| 現行ID | 寄せ先 | 備考 |
|---|---|---|
| `travel_kyoto_post` | `social_scene_post` | scene = Kyoto |
| `travel_tokyo_post` | `social_scene_post` | scene = Tokyo |
| `travel_okinawa_post` | `social_scene_post` | scene = Okinawa |
| `travel_hokkaido_post` | `social_scene_post` | scene = Hokkaido |
| `reading_post_general` | `social_scene_post` | reading family |
| `reading_post_seaside` | `social_scene_post` | reading family |
| `reading_post_anne` | `social_scene_post` | reading family |
| `cosplay_post` | `social_scene_post` | outfit + scene 差分 |
| `poker_post` | `social_scene_post` | game family |
| `cardgame_post` | `social_scene_post` | game family |
| `joinwars_post` | `social_scene_post` | game family |

### ブランド

| 現行ID | 寄せ先 | 備考 |
|---|---|---|
| `logo_only_sheet` | `brand_identity_sheet` | logo_type = logo |
| `wordmark_sheet` | `brand_identity_sheet` | logo_type = wordmark |
| `frame_sheet` | `brand_identity_sheet` | logo_type = frame |
| `icon_mark_sheet` | `brand_identity_sheet` | logo_type = icon |
| `orbit_logo_sheet` | `brand_identity_sheet` | logo_type = orbit |

### リプライ・反応・安全

| 現行ID | 寄せ先 | 備考 |
|---|---|---|
| `reaction_image` | `reply_core_pack` | reaction_card 出力 |
| `reply_stamp_sheet` | `reply_core_pack` | stamp 出力 |
| `comment_reply_guide` | `reply_core_pack` | ガイド系に統合 |
| `topic_redirect_banner` | `reply_core_pack` | redirect_banner 出力 |
| `safe_reply_pack` | `reply_core_pack` | safe mode |
| `chat_reply_pack` | `reply_core_pack` | chat mode |

### 記録・まとめ・回収

| 現行ID | 寄せ先 | 備考 |
|---|---|---|
| `memory_note_board` | `memory_review_pack` | 記憶の記録面 |
| `poststream_review_board` | `review_pack` | 振り返り面 |
| `archive_contact_sheet` | `archive_pack` | 台帳・回収面 |
| `persona_sheet` | `persona_pack` | 人格系に寄せる |
| `summary_sheet` | `summary_pack` | 集約面 |
| `archive_index` | `archive_pack` | 索引面 |
| `research_log_pack` | `review_pack` | 分析ログへ寄せる |
| `memory_pack` | `memory_pack` | そのまま中核として残す |

## ブロック移行マップ

### 朝系

| 現行ID | 寄せ先 | 備考 |
|---|---|---|
| `morning_pose_spring_kafka` | `morning_pose_pack` | season = spring |
| `morning_pose_summer_kafka` | `morning_pose_pack` | season = summer |
| `morning_pose_autumn_kafka` | `morning_pose_pack` | season = autumn |
| `morning_pose_winter_kafka` | `morning_pose_pack` | season = winter |
| `morning_pose_window_kafka` | `morning_pose_pack` | scene = window |
| `morning_pose_coffee_kafka` | `morning_pose_pack` | scene = coffee |
| `morning_pose_commute_kafka` | `morning_pose_pack` | scene = commute |
| `morning_pose_rain_kafka` | `morning_pose_pack` | scene = rain |
| `morning_pose_sleepy_kafka` | `morning_pose_pack` | mood = sleepy |
| `morning_background_spring_kafka` | `morning_scene_pack` | season = spring |
| `morning_background_summer_kafka` | `morning_scene_pack` | season = summer |
| `morning_background_autumn_kafka` | `morning_scene_pack` | season = autumn |
| `morning_background_winter_kafka` | `morning_scene_pack` | season = winter |
| `morning_scene_window_kafka` | `morning_scene_pack` | scene = window |
| `morning_scene_coffee_kafka` | `morning_scene_pack` | scene = coffee |
| `morning_scene_commute_kafka` | `morning_scene_pack` | scene = commute |
| `morning_scene_rain_kafka` | `morning_scene_pack` | scene = rain |
| `morning_scene_sleepy_kafka` | `morning_scene_pack` | mood = sleepy |
| `morning_tweet_text_pack` | `morning_text_pack` | 朝文言に統合 |
| `morning_situation_text_pack` | `morning_text_pack` | 文言の種類を属性化 |

### 旅行・読書・ゲーム・コスプレ

| 現行ID | 寄せ先 | 備考 |
|---|---|---|
| `travel_bg_kyoto` | `travel_scene_pack` | city = Kyoto |
| `travel_bg_tokyo` | `travel_scene_pack` | city = Tokyo |
| `travel_bg_okinawa` | `travel_scene_pack` | city = Okinawa |
| `travel_bg_hokkaido` | `travel_scene_pack` | city = Hokkaido |
| `reading_scene_general_kafka` | `reading_scene_pack` | general |
| `reading_scene_seaside_kafka` | `reading_scene_pack` | seaside |
| `reading_scene_anne_kafka` | `reading_scene_pack` | anne |
| `reading_pose_kafka` | `reading_pose_pack` | 読書姿勢に統合 |
| `reading_outfit_kafka` | `reading_outfit_pack` | 読書衣装に統合 |
| `cosplay_event_outfit_kafka` | `cosplay_outfit_pack` | event = cosplay |
| `cosplay_scene_kafka` | `cosplay_scene_pack` | 撮影背景に統合 |
| `poker_dealer_style_kafka` | `game_outfit_pack` | game = poker |
| `poker_table_scene_kafka` | `game_scene_pack` | game = poker |
| `joinwars_style_kafka` | `game_outfit_pack` | game = joinwars |
| `joinwars_scene_kafka` | `game_scene_pack` | game = joinwars |
| `joinwars_layout` | `game_layout_pack` | game = joinwars |
| `poker_status_text_pack` | `game_text_pack` | game = poker |
| `card_game_status_text_pack` | `game_text_pack` | game = cardgame |
| `joinwars_status_text_pack` | `game_text_pack` | game = joinwars |
| `reading_status_text_pack` | `reading_text_pack` | 読書文言に統合 |

### 既存のまま残す候補

| ID | 理由 |
|---|---|
| `master_style` | 最上位の共通基盤 |
| `character_kafka` | 参照中心の中核キャラ |
| `outfit_kafka` | 全体の共通衣装ベース |
| `negative_common` | 共通ネガティブの再利用価値が高い |
| `text_style_jp` | 多用途で共通利用できる |
| `effects_pack` | 装飾の共通部品として有効 |
| `speech_mode_kafka` | 性格トーンの中核 |
| `persona_pack` | 人格の中核 |

## 実施時の注意

1. 旧IDをいきなり削除しない
2. まず新IDを追加し、参照先を切り替える
3. UIと検証を通してから旧IDを縮退する
4. `artifacts` の参照切れは必ず確認する

## 成功条件

- 同じ意味のテンプレートが系列ごとに束ねられている
- 新しい派生を足す時、既存の親系列を選べる
- 一覧UIが「似たものの並び」ではなく「系列の比較」になる

