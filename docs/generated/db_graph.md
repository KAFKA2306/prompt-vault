# Prompt Vault DB Graph

複数の視点を順番に並べた静的グラフ。まず全体、次に用途別、最後に焦点ビューを見る。

## Overview
- Prompt Vault DB Graph

### Template Composition

```mermaid
flowchart LR
  classDef template fill:#dbeafe,stroke:#2563eb,color:#0f172a,stroke-width:1px;
  classDef block fill:#dcfce7,stroke:#059669,color:#0f172a,stroke-width:1px;
  subgraph templates["Templates"]
    direction TB
    subgraph kind_01["social"]
      direction TB
      t_joinwars_post["Kafka JoinWars投稿<br/><small>joinwars_post</small>"]:::template
      t_morning_tweet_coffee["Kafka おはツイ コーヒー<br/><small>morning_tweet_coffee</small>"]:::template
      t_morning_tweet_winter["Kafka おはツイ 冬<br/><small>morning_tweet_winter</small>"]:::template
      t_morning_tweet_commute["Kafka おはツイ 出発前<br/><small>morning_tweet_commute</small>"]:::template
      t_morning_tweet_summer["Kafka おはツイ 夏<br/><small>morning_tweet_summer</small>"]:::template
      t_morning_tweet_sleepy["Kafka おはツイ 寝起き<br/><small>morning_tweet_sleepy</small>"]:::template
      t_morning_tweet_spring["Kafka おはツイ 春<br/><small>morning_tweet_spring</small>"]:::template
      t_morning_tweet_autumn["Kafka おはツイ 秋<br/><small>morning_tweet_autumn</small>"]:::template
      t_morning_tweet_window["Kafka おはツイ 窓際<br/><small>morning_tweet_window</small>"]:::template
      t_morning_tweet_rain["Kafka おはツイ 雨の日<br/><small>morning_tweet_rain</small>"]:::template
      t_goodnight_post["Kafka おやすみポスト<br/><small>goodnight_post</small>"]:::template
      t_cardgame_post["Kafka カードゲーム投稿<br/><small>cardgame_post</small>"]:::template
      t_cosplay_post["Kafka コスプレ投稿<br/><small>cosplay_post</small>"]:::template
      t_poker_post["Kafka ポーカー投稿<br/><small>poker_post</small>"]:::template
      t_break_post["Kafka 休憩ポスト<br/><small>break_post</small>"]:::template
      t_work_start_post["Kafka 作業開始ポスト<br/><small>work_start_post</small>"]:::template
      t_reading_post_seaside["Kafka 海辺の読書投稿<br/><small>reading_post_seaside</small>"]:::template
      t_reading_post_general["Kafka 読書投稿<br/><small>reading_post_general</small>"]:::template
      t_reading_post_anne["Kafka 赤毛のアン読書投稿<br/><small>reading_post_anne</small>"]:::template
      t_progress_post["Kafka 進捗ポスト<br/><small>progress_post</small>"]:::template
    end
    subgraph kind_02["design_sheet"]
      direction TB
      t_morning_tweet_index["Kafka おはツイ一覧<br/><small>morning_tweet_index</small>"]:::template
      t_character_design_sheet["Kafka キャラデザインシート<br/><small>character_design_sheet</small>"]:::template
      t_persona_poster["Kafka 人格ポスター<br/><small>persona_poster</small>"]:::template
      t_persona_sheet["Kafka 人格固定カード<br/><small>persona_sheet</small>"]:::template
      t_archive_contact_sheet["Kafka 成果物一覧<br/><small>archive_contact_sheet</small>"]:::template
      t_archive_index["Kafka 成果物回収カード<br/><small>archive_index</small>"]:::template
      t_photo_prompt_sheet["Kafka 生成素材台帳<br/><small>photo_prompt_sheet</small>"]:::template
      t_memory_note_board["Kafka 記憶メモボード<br/><small>memory_note_board</small>"]:::template
      t_memory_update_card["Kafka 記憶更新カード<br/><small>memory_update_card</small>"]:::template
      t_summary_sheet["Kafka 配信後まとめカード<br/><small>summary_sheet</small>"]:::template
      t_poststream_review_board["Kafka 配信後レビュー盤<br/><small>poststream_review_board</small>"]:::template
      t_daily_work_sheet["Kafka 配信運用カード<br/><small>daily_work_sheet</small>"]:::template
    end
    subgraph kind_03["brand"]
      direction TB
      t_icon_mark_sheet["Kafka アイコンデザイン<br/><small>icon_mark_sheet</small>"]:::template
      t_frame_sheet["Kafka フレームデザイン<br/><small>frame_sheet</small>"]:::template
      t_logo_only_sheet["Kafka ロゴデザイン<br/><small>logo_only_sheet</small>"]:::template
      t_wordmark_sheet["Kafka ワードマークデザイン<br/><small>wordmark_sheet</small>"]:::template
      t_orbit_logo_sheet["Kafka 宇宙ロゴデザイン<br/><small>orbit_logo_sheet</small>"]:::template
    end
    subgraph kind_04["system"]
      direction TB
      t_comment_reply_guide["Kafka コメント返しガイド<br/><small>comment_reply_guide</small>"]:::template
      t_slide_talk["Kafka スライド発表<br/><small>slide_talk</small>"]:::template
      t_ai_tuber_core_pack["Kafka 起動カード<br/><small>ai_tuber_core_pack</small>"]:::template
      t_ai_tuber_ops_pack["Kafka 配信後レビューカード<br/><small>ai_tuber_ops_pack</small>"]:::template
    end
    subgraph kind_05["announcement"]
      direction TB
      t_topic_redirect_banner["Kafka 話題切り替えバナー<br/><small>topic_redirect_banner</small>"]:::template
      t_announcement_thumbnail["Kafka 配信告知サムネイル<br/><small>announcement_thumbnail</small>"]:::template
      t_stream_start_banner["Kafka 配信開始バナー<br/><small>stream_start_banner</small>"]:::template
    end
    subgraph kind_06["reaction"]
      direction TB
      t_chat_reply_card["Kafka コメント返信カード<br/><small>chat_reply_card</small>"]:::template
      t_reaction_image["Kafka 反応画像<br/><small>reaction_image</small>"]:::template
      t_topic_redirect_card["Kafka 話題切り替えカード<br/><small>topic_redirect_card</small>"]:::template
    end
    subgraph kind_07["stamp"]
      direction TB
      t_stamp_sheet["Kafka 新しいスタンプ<br/><small>stamp_sheet</small>"]:::template
      t_reply_stamp_sheet["Kafka 返信スタンプ（一覧）<br/><small>reply_stamp_sheet</small>"]:::template
    end
    subgraph kind_08["comic"]
      direction TB
      t_twitter_comic["Kafka Twitter再調査漫画<br/><small>twitter_comic</small>"]:::template
    end
  end
  subgraph blocks["Blocks"]
    direction TB
    subgraph cat_01["形式・レイアウト"]
      direction TB
      b_sticker_sheet_layout["4x4 ステッカーシート<br/><small>sticker_sheet_layout</small>"]:::block
      b_joinwars_layout["JoinWars用レイアウト<br/><small>joinwars_layout</small>"]:::block
      b_character_sheet_kafka["Kafka キャラデザインシート<br/><small>character_sheet_kafka</small>"]:::block
      b_morning_tweet_layout["おはツイレイアウト<br/><small>morning_tweet_layout</small>"]:::block
      b_archive_index_vlog["アーカイブ索引<br/><small>archive_index_vlog</small>"]:::block
      b_cardgame_post_layout["カードゲームレイアウト<br/><small>cardgame_post_layout</small>"]:::block
      b_cosplay_post_layout["コスプレレイアウト<br/><small>cosplay_post_layout</small>"]:::block
      b_persona_sheet_vlog["パーソナ設定シート<br/><small>persona_sheet_vlog</small>"]:::block
      b_poker_post_layout["ポーカーレイアウト<br/><small>poker_post_layout</small>"]:::block
      b_persona_poster_viz["人格ポスター<br/><small>persona_poster_viz</small>"]:::block
      b_daily_work_sheet_vlog["作業管理テンプレート<br/><small>daily_work_sheet_vlog</small>"]:::block
      b_archive_contact_sheet_viz["成果物一覧（コンタクトシート）<br/><small>archive_contact_sheet_viz</small>"]:::block
      b_summary_sheet_vlog["振り返りサマリー<br/><small>summary_sheet_vlog</small>"]:::block
      b_status_post_layout["日常ステータスレイアウト<br/><small>status_post_layout</small>"]:::block
      b_comic_layout["漫画レイアウト<br/><small>comic_layout</small>"]:::block
      b_prompt_archive_sheet_vlog["生成台帳<br/><small>prompt_archive_sheet_vlog</small>"]:::block
      b_photo_prompt_sheet_vlog["画像生成台帳（詳細）<br/><small>photo_prompt_sheet_vlog</small>"]:::block
      b_memory_note_board_viz["記憶メモ（記録用ボード）<br/><small>memory_note_board_viz</small>"]:::block
      b_topic_redirect_banner_viz["話題切り替え用バナー<br/><small>topic_redirect_banner_viz</small>"]:::block
      b_reading_post_layout["読書シーン用レイアウト<br/><small>reading_post_layout</small>"]:::block
      b_reply_stamp_sheet_viz["返信スタンプ（グリッド）<br/><small>reply_stamp_sheet_viz</small>"]:::block
      b_poststream_review_board_viz["配信振り返り（レビュー用）<br/><small>poststream_review_board_viz</small>"]:::block
      b_stream_start_banner_viz["配信開始バナー<br/><small>stream_start_banner_viz</small>"]:::block
    end
    subgraph cat_02["背景"]
      direction TB
      b_joinwars_scene_kafka["JoinWars背景<br/><small>joinwars_scene_kafka</small>"]:::block
      b_goodnight_scene_kafka["おやすみ背景<br/><small>goodnight_scene_kafka</small>"]:::block
      b_cosplay_scene_kafka["コスプレ撮影背景<br/><small>cosplay_scene_kafka</small>"]:::block
      b_fantasy_card_game_scene_kafka["ファンタジーカード盤面<br/><small>fantasy_card_game_scene_kafka</small>"]:::block
      b_poker_table_scene_kafka["ポーカーテーブル背景<br/><small>poker_table_scene_kafka</small>"]:::block
      b_break_scene_kafka["休憩背景<br/><small>break_scene_kafka</small>"]:::block
      b_work_start_scene_kafka["作業開始背景<br/><small>work_start_scene_kafka</small>"]:::block
      b_morning_background_winter_kafka["冬朝背景<br/><small>morning_background_winter_kafka</small>"]:::block
      b_morning_scene_commute_kafka["出発前の朝背景<br/><small>morning_scene_commute_kafka</small>"]:::block
      b_morning_background_summer_kafka["夏朝背景<br/><small>morning_background_summer_kafka</small>"]:::block
      b_morning_scene_sleepy_kafka["寝起きの朝背景<br/><small>morning_scene_sleepy_kafka</small>"]:::block
      b_morning_background_spring_kafka["春朝背景<br/><small>morning_background_spring_kafka</small>"]:::block
      b_morning_scene_coffee_kafka["朝コーヒー背景<br/><small>morning_scene_coffee_kafka</small>"]:::block
      b_reading_scene_seaside_kafka["海辺の読書背景<br/><small>reading_scene_seaside_kafka</small>"]:::block
      b_morning_background_autumn_kafka["秋朝背景<br/><small>morning_background_autumn_kafka</small>"]:::block
      b_morning_scene_window_kafka["窓際の朝背景<br/><small>morning_scene_window_kafka</small>"]:::block
      b_reading_scene_general_kafka["読書背景<br/><small>reading_scene_general_kafka</small>"]:::block
      b_reading_scene_anne_kafka["赤毛のアン読書背景<br/><small>reading_scene_anne_kafka</small>"]:::block
      b_progress_scene_kafka["進捗背景<br/><small>progress_scene_kafka</small>"]:::block
      b_morning_scene_rain_kafka["雨の日の朝背景<br/><small>morning_scene_rain_kafka</small>"]:::block
    end
    subgraph cat_03["セリフ・フレーズ"]
      direction TB
      b_joinwars_status_text_pack["JoinWars文言<br/><small>joinwars_status_text_pack</small>"]:::block
      b_morning_tweet_text_pack["おはツイ文言<br/><small>morning_tweet_text_pack</small>"]:::block
      b_card_game_status_text_pack["カードゲーム文言<br/><small>card_game_status_text_pack</small>"]:::block
      b_cosplay_status_text_pack["コスプレ文言<br/><small>cosplay_status_text_pack</small>"]:::block
      b_poker_status_text_pack["ポーカーポスト文言<br/><small>poker_status_text_pack</small>"]:::block
      b_announcement_text_pack["告知文言<br/><small>announcement_text_pack</small>"]:::block
      b_daily_status_text_pack["日常ステータス文言<br/><small>daily_status_text_pack</small>"]:::block
      b_morning_situation_text_pack["朝シチュエーション文言<br/><small>morning_situation_text_pack</small>"]:::block
      b_text_content_pack["短い日本語セリフ<br/><small>text_content_pack</small>"]:::block
      b_reading_status_text_pack["読書文言<br/><small>reading_status_text_pack</small>"]:::block
    end
    subgraph cat_04["ポーズ"]
      direction TB
      b_morning_pose_coffee_kafka["コーヒーおはツイ姿勢<br/><small>morning_pose_coffee_kafka</small>"]:::block
      b_morning_pose_winter_kafka["冬おはツイ姿勢<br/><small>morning_pose_winter_kafka</small>"]:::block
      b_morning_pose_commute_kafka["出発前おはツイ姿勢<br/><small>morning_pose_commute_kafka</small>"]:::block
      b_morning_pose_summer_kafka["夏おはツイ姿勢<br/><small>morning_pose_summer_kafka</small>"]:::block
      b_morning_pose_sleepy_kafka["寝起きおはツイ姿勢<br/><small>morning_pose_sleepy_kafka</small>"]:::block
      b_morning_pose_spring_kafka["春おはツイ姿勢<br/><small>morning_pose_spring_kafka</small>"]:::block
      b_morning_pose_autumn_kafka["秋おはツイ姿勢<br/><small>morning_pose_autumn_kafka</small>"]:::block
      b_morning_pose_window_kafka["窓際おはツイ姿勢<br/><small>morning_pose_window_kafka</small>"]:::block
      b_reading_pose_kafka["読書ポーズ<br/><small>reading_pose_kafka</small>"]:::block
      b_morning_pose_rain_kafka["雨の日おはツイ姿勢<br/><small>morning_pose_rain_kafka</small>"]:::block
    end
    subgraph cat_05["衣装"]
      direction TB
      b_joinwars_style_kafka["JoinWars衣装<br/><small>joinwars_style_kafka</small>"]:::block
      b_cosplay_event_outfit_kafka["コスプレ衣装<br/><small>cosplay_event_outfit_kafka</small>"]:::block
      b_fantasy_card_game_style_kafka["ファンタジーカードゲーム衣装<br/><small>fantasy_card_game_style_kafka</small>"]:::block
      b_poker_dealer_style_kafka["ポーカーディーラー衣装<br/><small>poker_dealer_style_kafka</small>"]:::block
      b_seasonal_outfit_winter_kafka["冬衣装<br/><small>seasonal_outfit_winter_kafka</small>"]:::block
      b_seasonal_outfit_summer_kafka["夏衣装<br/><small>seasonal_outfit_summer_kafka</small>"]:::block
      b_seasonal_outfit_spring_kafka["春衣装<br/><small>seasonal_outfit_spring_kafka</small>"]:::block
      b_seasonal_outfit_autumn_kafka["秋衣装<br/><small>seasonal_outfit_autumn_kafka</small>"]:::block
      b_reading_outfit_kafka["読書衣装<br/><small>reading_outfit_kafka</small>"]:::block
    end
    subgraph cat_06["ブランド"]
      direction TB
      b_icon_mark_only_kafka["アイコン単独<br/><small>icon_mark_only_kafka</small>"]:::block
      b_frame_only_kafka["フレーム単独<br/><small>frame_only_kafka</small>"]:::block
      b_logo_only_kafka["ロゴ単独<br/><small>logo_only_kafka</small>"]:::block
      b_logo_orbit_kafka["宇宙ロゴ単独<br/><small>logo_orbit_kafka</small>"]:::block
      b_wordmark_only_kafka["文字ロゴ単独<br/><small>wordmark_only_kafka</small>"]:::block
    end
    subgraph cat_07["テキスト"]
      direction TB
      b_subtitle_pack["字幕・テロップ<br/><small>subtitle_pack</small>"]:::block
      b_text_style_jp["日本語文字<br/><small>text_style_jp</small>"]:::block
    end
    subgraph cat_08["リプライ・対話"]
      direction TB
      b_chat_reply_pack["コメント返し<br/><small>chat_reply_pack</small>"]:::block
      b_safe_reply_pack["話題切り替え<br/><small>safe_reply_pack</small>"]:::block
    end
    subgraph cat_09["演出"]
      direction TB
      b_vfx_trigger_pack["感情演出<br/><small>vfx_trigger_pack</small>"]:::block
      b_effects_pack["装飾効果<br/><small>effects_pack</small>"]:::block
    end
    subgraph cat_10["表情"]
      direction TB
      b_expressions_pack["反応集<br/><small>expressions_pack</small>"]:::block
      b_reaction_focus["表情強調<br/><small>reaction_focus</small>"]:::block
    end
    subgraph cat_11["アバター"]
      direction TB
      b_avatar_mode_pack["アバターモード<br/><small>avatar_mode_pack</small>"]:::block
    end
    subgraph cat_12["キャラクター"]
      direction TB
      b_character_kafka["KAFKA<br/><small>character_kafka</small>"]:::block
    end
    subgraph cat_13["キャラ衣装"]
      direction TB
      b_outfit_kafka["衣装<br/><small>outfit_kafka</small>"]:::block
    end
    subgraph cat_14["コンフィグ"]
      direction TB
      b_character_customization_pack["キャラ設定<br/><small>character_customization_pack</small>"]:::block
    end
    subgraph cat_15["システム・実行"]
      direction TB
      b_local_offline_pack["ローカル優先<br/><small>local_offline_pack</small>"]:::block
    end
    subgraph cat_16["ネガティブ"]
      direction TB
      b_negative_common["共通ネガティブ<br/><small>negative_common</small>"]:::block
    end
    subgraph cat_17["リサーチ"]
      direction TB
      b_source_research["再調査メモ<br/><small>source_research</small>"]:::block
    end
    subgraph cat_18["人格"]
      direction TB
      b_persona_pack["自律人格<br/><small>persona_pack</small>"]:::block
    end
    subgraph cat_19["制御"]
      direction TB
      b_control_panel_pack["操作パネル<br/><small>control_panel_pack</small>"]:::block
    end
    subgraph cat_20["基準"]
      direction TB
      b_master_style["マスタースタイル<br/><small>master_style</small>"]:::block
    end
    subgraph cat_21["安全"]
      direction TB
      b_moderation_pack["モデレーション<br/><small>moderation_pack</small>"]:::block
    end
    subgraph cat_22["展示・サイン"]
      direction TB
      b_demo_mode_pack["デモモード<br/><small>demo_mode_pack</small>"]:::block
    end
    subgraph cat_23["性格・トーン"]
      direction TB
      b_speech_mode_kafka["かふからしい発話モード<br/><small>speech_mode_kafka</small>"]:::block
    end
    subgraph cat_24["拡張"]
      direction TB
      b_plugin_pack["外部連携<br/><small>plugin_pack</small>"]:::block
    end
    subgraph cat_25["発表"]
      direction TB
      b_slide_pack["スライド発表<br/><small>slide_pack</small>"]:::block
    end
    subgraph cat_26["記憶"]
      direction TB
      b_memory_pack["記憶管理<br/><small>memory_pack</small>"]:::block
    end
    subgraph cat_27["記録・ログ"]
      direction TB
      b_research_log_pack["振り返りログ<br/><small>research_log_pack</small>"]:::block
    end
    subgraph cat_28["配信"]
      direction TB
      b_chat_platform_pack["配信チャット<br/><small>chat_platform_pack</small>"]:::block
    end
    subgraph cat_29["音声"]
      direction TB
      b_voice_pipeline_pack["音声パイプライン<br/><small>voice_pipeline_pack</small>"]:::block
    end
  end
  t_joinwars_post --> b_master_style
  t_joinwars_post --> b_character_kafka
  t_joinwars_post --> b_joinwars_layout
  t_joinwars_post --> b_joinwars_scene_kafka
  t_joinwars_post --> b_joinwars_style_kafka
  t_joinwars_post --> b_joinwars_status_text_pack
  t_joinwars_post --> b_text_style_jp
  t_joinwars_post --> b_negative_common
  t_twitter_comic --> b_source_research
  t_twitter_comic --> b_master_style
  t_twitter_comic --> b_character_kafka
  t_twitter_comic --> b_comic_layout
  t_twitter_comic --> b_reaction_focus
  t_twitter_comic --> b_text_style_jp
  t_twitter_comic --> b_text_content_pack
  t_twitter_comic --> b_effects_pack
  t_twitter_comic --> b_negative_common
  t_morning_tweet_coffee --> b_master_style
  t_morning_tweet_coffee --> b_character_kafka
  t_morning_tweet_coffee --> b_outfit_kafka
  t_morning_tweet_coffee --> b_morning_pose_coffee_kafka
  t_morning_tweet_coffee --> b_morning_scene_coffee_kafka
  t_morning_tweet_coffee --> b_morning_tweet_layout
  t_morning_tweet_coffee --> b_morning_situation_text_pack
  t_morning_tweet_coffee --> b_text_style_jp
  t_morning_tweet_coffee --> b_negative_common
  t_morning_tweet_winter --> b_master_style
  t_morning_tweet_winter --> b_character_kafka
  t_morning_tweet_winter --> b_seasonal_outfit_winter_kafka
  t_morning_tweet_winter --> b_morning_pose_winter_kafka
  t_morning_tweet_winter --> b_morning_background_winter_kafka
  t_morning_tweet_winter --> b_morning_tweet_layout
  t_morning_tweet_winter --> b_morning_tweet_text_pack
  t_morning_tweet_winter --> b_text_style_jp
  t_morning_tweet_winter --> b_effects_pack
  t_morning_tweet_winter --> b_negative_common
  t_morning_tweet_commute --> b_master_style
  t_morning_tweet_commute --> b_character_kafka
  t_morning_tweet_commute --> b_outfit_kafka
  t_morning_tweet_commute --> b_morning_pose_commute_kafka
  t_morning_tweet_commute --> b_morning_scene_commute_kafka
  t_morning_tweet_commute --> b_morning_tweet_layout
  t_morning_tweet_commute --> b_morning_situation_text_pack
  t_morning_tweet_commute --> b_text_style_jp
  t_morning_tweet_commute --> b_negative_common
  t_morning_tweet_summer --> b_master_style
  t_morning_tweet_summer --> b_character_kafka
  t_morning_tweet_summer --> b_seasonal_outfit_summer_kafka
  t_morning_tweet_summer --> b_morning_pose_summer_kafka
  t_morning_tweet_summer --> b_morning_background_summer_kafka
  t_morning_tweet_summer --> b_morning_tweet_layout
  t_morning_tweet_summer --> b_morning_tweet_text_pack
  t_morning_tweet_summer --> b_text_style_jp
  t_morning_tweet_summer --> b_effects_pack
  t_morning_tweet_summer --> b_negative_common
  t_morning_tweet_sleepy --> b_master_style
  t_morning_tweet_sleepy --> b_character_kafka
  t_morning_tweet_sleepy --> b_outfit_kafka
  t_morning_tweet_sleepy --> b_morning_pose_sleepy_kafka
  t_morning_tweet_sleepy --> b_morning_scene_sleepy_kafka
  t_morning_tweet_sleepy --> b_morning_tweet_layout
  t_morning_tweet_sleepy --> b_morning_situation_text_pack
  t_morning_tweet_sleepy --> b_text_style_jp
  t_morning_tweet_sleepy --> b_negative_common
  t_morning_tweet_spring --> b_master_style
  t_morning_tweet_spring --> b_character_kafka
  t_morning_tweet_spring --> b_seasonal_outfit_spring_kafka
  t_morning_tweet_spring --> b_morning_pose_spring_kafka
  t_morning_tweet_spring --> b_morning_background_spring_kafka
  t_morning_tweet_spring --> b_morning_tweet_layout
  t_morning_tweet_spring --> b_morning_tweet_text_pack
  t_morning_tweet_spring --> b_text_style_jp
  t_morning_tweet_spring --> b_effects_pack
  t_morning_tweet_spring --> b_negative_common
  t_morning_tweet_autumn --> b_master_style
  t_morning_tweet_autumn --> b_character_kafka
  t_morning_tweet_autumn --> b_seasonal_outfit_autumn_kafka
  t_morning_tweet_autumn --> b_morning_pose_autumn_kafka
  t_morning_tweet_autumn --> b_morning_background_autumn_kafka
  t_morning_tweet_autumn --> b_morning_tweet_layout
  t_morning_tweet_autumn --> b_morning_tweet_text_pack
  t_morning_tweet_autumn --> b_text_style_jp
  t_morning_tweet_autumn --> b_effects_pack
  t_morning_tweet_autumn --> b_negative_common
  t_morning_tweet_window --> b_master_style
  t_morning_tweet_window --> b_character_kafka
  t_morning_tweet_window --> b_outfit_kafka
  t_morning_tweet_window --> b_morning_pose_window_kafka
  t_morning_tweet_window --> b_morning_scene_window_kafka
  t_morning_tweet_window --> b_morning_tweet_layout
  t_morning_tweet_window --> b_morning_situation_text_pack
  t_morning_tweet_window --> b_text_style_jp
  t_morning_tweet_window --> b_negative_common
  t_morning_tweet_rain --> b_master_style
  t_morning_tweet_rain --> b_character_kafka
  t_morning_tweet_rain --> b_outfit_kafka
  t_morning_tweet_rain --> b_morning_pose_rain_kafka
  t_morning_tweet_rain --> b_morning_scene_rain_kafka
  t_morning_tweet_rain --> b_morning_tweet_layout
  t_morning_tweet_rain --> b_morning_situation_text_pack
  t_morning_tweet_rain --> b_text_style_jp
  t_morning_tweet_rain --> b_negative_common
  t_morning_tweet_index --> b_master_style
  t_morning_tweet_index --> b_character_kafka
  t_morning_tweet_index --> b_morning_tweet_layout
  t_morning_tweet_index --> b_morning_tweet_text_pack
  t_morning_tweet_index --> b_morning_situation_text_pack
  t_morning_tweet_index --> b_text_style_jp
  t_morning_tweet_index --> b_negative_common
  t_goodnight_post --> b_master_style
  t_goodnight_post --> b_character_kafka
  t_goodnight_post --> b_outfit_kafka
  t_goodnight_post --> b_goodnight_scene_kafka
  t_goodnight_post --> b_status_post_layout
  t_goodnight_post --> b_daily_status_text_pack
  t_goodnight_post --> b_text_style_jp
  t_goodnight_post --> b_negative_common
  t_icon_mark_sheet --> b_master_style
  t_icon_mark_sheet --> b_icon_mark_only_kafka
  t_icon_mark_sheet --> b_negative_common
  t_cardgame_post --> b_master_style
  t_cardgame_post --> b_character_kafka
  t_cardgame_post --> b_cardgame_post_layout
  t_cardgame_post --> b_fantasy_card_game_scene_kafka
  t_cardgame_post --> b_fantasy_card_game_style_kafka
  t_cardgame_post --> b_card_game_status_text_pack
  t_cardgame_post --> b_text_style_jp
  t_cardgame_post --> b_negative_common
  t_character_design_sheet --> b_character_sheet_kafka
  t_cosplay_post --> b_master_style
  t_cosplay_post --> b_character_kafka
  t_cosplay_post --> b_cosplay_post_layout
  t_cosplay_post --> b_cosplay_scene_kafka
  t_cosplay_post --> b_cosplay_event_outfit_kafka
  t_cosplay_post --> b_cosplay_status_text_pack
  t_cosplay_post --> b_text_style_jp
  t_cosplay_post --> b_negative_common
  t_comment_reply_guide --> b_master_style
  t_comment_reply_guide --> b_character_kafka
  t_comment_reply_guide --> b_chat_reply_pack
  t_comment_reply_guide --> b_speech_mode_kafka
  t_comment_reply_guide --> b_safe_reply_pack
  t_comment_reply_guide --> b_text_style_jp
  t_comment_reply_guide --> b_expressions_pack
  t_comment_reply_guide --> b_negative_common
  t_chat_reply_card --> b_master_style
  t_chat_reply_card --> b_character_kafka
  t_chat_reply_card --> b_chat_reply_pack
  t_chat_reply_card --> b_speech_mode_kafka
  t_chat_reply_card --> b_text_style_jp
  t_chat_reply_card --> b_text_content_pack
  t_chat_reply_card --> b_expressions_pack
  t_chat_reply_card --> b_negative_common
  t_chat_reply_card -.-> b_chat_reply_pack
  t_chat_reply_card -.-> b_speech_mode_kafka
  t_chat_reply_card -.-> b_text_style_jp
  t_chat_reply_card -.-> b_expressions_pack
  t_slide_talk --> b_master_style
  t_slide_talk --> b_character_kafka
  t_slide_talk --> b_slide_pack
  t_slide_talk --> b_text_style_jp
  t_slide_talk --> b_negative_common
  t_frame_sheet --> b_master_style
  t_frame_sheet --> b_frame_only_kafka
  t_frame_sheet --> b_negative_common
  t_poker_post --> b_master_style
  t_poker_post --> b_character_kafka
  t_poker_post --> b_poker_post_layout
  t_poker_post --> b_poker_table_scene_kafka
  t_poker_post --> b_poker_dealer_style_kafka
  t_poker_post --> b_poker_status_text_pack
  t_poker_post --> b_text_style_jp
  t_poker_post --> b_negative_common
  t_logo_only_sheet --> b_master_style
  t_logo_only_sheet --> b_logo_only_kafka
  t_logo_only_sheet --> b_wordmark_only_kafka
  t_logo_only_sheet --> b_icon_mark_only_kafka
  t_logo_only_sheet --> b_negative_common
  t_wordmark_sheet --> b_master_style
  t_wordmark_sheet --> b_wordmark_only_kafka
  t_wordmark_sheet --> b_text_style_jp
  t_wordmark_sheet --> b_negative_common
  t_persona_poster --> b_master_style
  t_persona_poster --> b_character_kafka
  t_persona_poster --> b_outfit_kafka
  t_persona_poster --> b_persona_poster_viz
  t_persona_poster --> b_persona_pack
  t_persona_poster --> b_text_style_jp
  t_persona_poster --> b_negative_common
  t_persona_poster -.-> b_persona_poster_viz
  t_persona_poster -.-> b_persona_pack
  t_persona_poster -.-> b_text_style_jp
  t_persona_sheet --> b_master_style
  t_persona_sheet --> b_character_kafka
  t_persona_sheet --> b_persona_sheet_vlog
  t_persona_sheet --> b_persona_pack
  t_persona_sheet --> b_speech_mode_kafka
  t_persona_sheet --> b_text_style_jp
  t_persona_sheet --> b_negative_common
  t_break_post --> b_master_style
  t_break_post --> b_character_kafka
  t_break_post --> b_outfit_kafka
  t_break_post --> b_break_scene_kafka
  t_break_post --> b_status_post_layout
  t_break_post --> b_daily_status_text_pack
  t_break_post --> b_text_style_jp
  t_break_post --> b_negative_common
  t_work_start_post --> b_master_style
  t_work_start_post --> b_character_kafka
  t_work_start_post --> b_outfit_kafka
  t_work_start_post --> b_work_start_scene_kafka
  t_work_start_post --> b_status_post_layout
  t_work_start_post --> b_daily_status_text_pack
  t_work_start_post --> b_text_style_jp
  t_work_start_post --> b_negative_common
  t_reaction_image --> b_master_style
  t_reaction_image --> b_character_kafka
  t_reaction_image --> b_outfit_kafka
  t_reaction_image --> b_reaction_focus
  t_reaction_image --> b_text_style_jp
  t_reaction_image --> b_text_content_pack
  t_reaction_image --> b_effects_pack
  t_reaction_image --> b_negative_common
  t_reaction_image -.-> b_reaction_focus
  t_reaction_image -.-> b_text_style_jp
  t_reaction_image -.-> b_text_content_pack
  t_reaction_image -.-> b_effects_pack
  t_orbit_logo_sheet --> b_master_style
  t_orbit_logo_sheet --> b_logo_orbit_kafka
  t_orbit_logo_sheet --> b_wordmark_only_kafka
  t_orbit_logo_sheet --> b_icon_mark_only_kafka
  t_orbit_logo_sheet --> b_negative_common
  t_archive_contact_sheet --> b_master_style
  t_archive_contact_sheet --> b_character_kafka
  t_archive_contact_sheet --> b_archive_contact_sheet_viz
  t_archive_contact_sheet --> b_archive_index_vlog
  t_archive_contact_sheet --> b_prompt_archive_sheet_vlog
  t_archive_contact_sheet --> b_negative_common
  t_archive_contact_sheet -.-> b_archive_contact_sheet_viz
  t_archive_contact_sheet -.-> b_archive_index_vlog
  t_archive_contact_sheet -.-> b_prompt_archive_sheet_vlog
  t_archive_index --> b_master_style
  t_archive_index --> b_character_kafka
  t_archive_index --> b_archive_index_vlog
  t_archive_index --> b_prompt_archive_sheet_vlog
  t_archive_index --> b_speech_mode_kafka
  t_archive_index --> b_negative_common
  t_stamp_sheet --> b_master_style
  t_stamp_sheet --> b_character_kafka
  t_stamp_sheet --> b_outfit_kafka
  t_stamp_sheet --> b_sticker_sheet_layout
  t_stamp_sheet --> b_expressions_pack
  t_stamp_sheet --> b_text_style_jp
  t_stamp_sheet --> b_text_content_pack
  t_stamp_sheet --> b_effects_pack
  t_stamp_sheet --> b_negative_common
  t_reading_post_seaside --> b_master_style
  t_reading_post_seaside --> b_character_kafka
  t_reading_post_seaside --> b_reading_post_layout
  t_reading_post_seaside --> b_reading_scene_seaside_kafka
  t_reading_post_seaside --> b_reading_pose_kafka
  t_reading_post_seaside --> b_reading_outfit_kafka
  t_reading_post_seaside --> b_reading_status_text_pack
  t_reading_post_seaside --> b_text_style_jp
  t_reading_post_seaside --> b_negative_common
  t_photo_prompt_sheet --> b_master_style
  t_photo_prompt_sheet --> b_character_kafka
  t_photo_prompt_sheet --> b_photo_prompt_sheet_vlog
  t_photo_prompt_sheet --> b_prompt_archive_sheet_vlog
  t_photo_prompt_sheet --> b_negative_common
  t_memory_note_board --> b_master_style
  t_memory_note_board --> b_character_kafka
  t_memory_note_board --> b_memory_note_board_viz
  t_memory_note_board --> b_memory_pack
  t_memory_note_board --> b_research_log_pack
  t_memory_note_board --> b_negative_common
  t_memory_note_board -.-> b_memory_note_board_viz
  t_memory_note_board -.-> b_memory_pack
  t_memory_note_board -.-> b_research_log_pack
  t_memory_update_card --> b_master_style
  t_memory_update_card --> b_character_kafka
  t_memory_update_card --> b_memory_pack
  t_memory_update_card --> b_speech_mode_kafka
  t_memory_update_card --> b_research_log_pack
  t_memory_update_card --> b_negative_common
  t_topic_redirect_card --> b_master_style
  t_topic_redirect_card --> b_character_kafka
  t_topic_redirect_card --> b_safe_reply_pack
  t_topic_redirect_card --> b_speech_mode_kafka
  t_topic_redirect_card --> b_text_style_jp
  t_topic_redirect_card --> b_negative_common
  t_topic_redirect_banner --> b_master_style
  t_topic_redirect_banner --> b_character_kafka
  t_topic_redirect_banner --> b_topic_redirect_banner_viz
  t_topic_redirect_banner --> b_safe_reply_pack
  t_topic_redirect_banner --> b_text_style_jp
  t_topic_redirect_banner --> b_negative_common
  t_reading_post_general --> b_master_style
  t_reading_post_general --> b_character_kafka
  t_reading_post_general --> b_reading_post_layout
  t_reading_post_general --> b_reading_scene_general_kafka
  t_reading_post_general --> b_reading_pose_kafka
  t_reading_post_general --> b_reading_outfit_kafka
  t_reading_post_general --> b_reading_status_text_pack
  t_reading_post_general --> b_text_style_jp
  t_reading_post_general --> b_negative_common
  t_reading_post_anne --> b_master_style
  t_reading_post_anne --> b_character_kafka
  t_reading_post_anne --> b_reading_post_layout
  t_reading_post_anne --> b_reading_scene_anne_kafka
  t_reading_post_anne --> b_reading_pose_kafka
  t_reading_post_anne --> b_reading_outfit_kafka
  t_reading_post_anne --> b_reading_status_text_pack
  t_reading_post_anne --> b_text_style_jp
  t_reading_post_anne --> b_negative_common
  t_ai_tuber_core_pack --> b_master_style
  t_ai_tuber_core_pack --> b_character_kafka
  t_ai_tuber_core_pack --> b_persona_pack
  t_ai_tuber_core_pack --> b_speech_mode_kafka
  t_ai_tuber_core_pack --> b_local_offline_pack
  t_ai_tuber_core_pack --> b_voice_pipeline_pack
  t_ai_tuber_core_pack --> b_chat_platform_pack
  t_ai_tuber_core_pack --> b_avatar_mode_pack
  t_ai_tuber_core_pack --> b_control_panel_pack
  t_ai_tuber_core_pack --> b_demo_mode_pack
  t_ai_tuber_core_pack --> b_moderation_pack
  t_ai_tuber_core_pack --> b_plugin_pack
  t_reply_stamp_sheet --> b_master_style
  t_reply_stamp_sheet --> b_character_kafka
  t_reply_stamp_sheet --> b_outfit_kafka
  t_reply_stamp_sheet --> b_reply_stamp_sheet_viz
  t_reply_stamp_sheet --> b_chat_reply_pack
  t_reply_stamp_sheet --> b_expressions_pack
  t_reply_stamp_sheet --> b_text_style_jp
  t_reply_stamp_sheet --> b_negative_common
  t_progress_post --> b_master_style
  t_progress_post --> b_character_kafka
  t_progress_post --> b_outfit_kafka
  t_progress_post --> b_progress_scene_kafka
  t_progress_post --> b_status_post_layout
  t_progress_post --> b_daily_status_text_pack
  t_progress_post --> b_text_style_jp
  t_progress_post --> b_negative_common
  t_announcement_thumbnail --> b_master_style
  t_announcement_thumbnail --> b_character_kafka
  t_announcement_thumbnail --> b_reaction_focus
  t_announcement_thumbnail --> b_announcement_text_pack
  t_announcement_thumbnail --> b_text_style_jp
  t_announcement_thumbnail --> b_effects_pack
  t_announcement_thumbnail --> b_negative_common
  t_summary_sheet --> b_master_style
  t_summary_sheet --> b_character_kafka
  t_summary_sheet --> b_summary_sheet_vlog
  t_summary_sheet --> b_speech_mode_kafka
  t_summary_sheet --> b_memory_pack
  t_summary_sheet --> b_research_log_pack
  t_summary_sheet --> b_negative_common
  t_ai_tuber_ops_pack --> b_master_style
  t_ai_tuber_ops_pack --> b_character_kafka
  t_ai_tuber_ops_pack --> b_chat_reply_pack
  t_ai_tuber_ops_pack --> b_safe_reply_pack
  t_ai_tuber_ops_pack --> b_speech_mode_kafka
  t_ai_tuber_ops_pack --> b_memory_pack
  t_ai_tuber_ops_pack --> b_vfx_trigger_pack
  t_ai_tuber_ops_pack --> b_subtitle_pack
  t_ai_tuber_ops_pack --> b_announcement_text_pack
  t_ai_tuber_ops_pack --> b_character_customization_pack
  t_ai_tuber_ops_pack --> b_research_log_pack
  t_poststream_review_board --> b_master_style
  t_poststream_review_board --> b_character_kafka
  t_poststream_review_board --> b_poststream_review_board_viz
  t_poststream_review_board --> b_research_log_pack
  t_poststream_review_board --> b_memory_pack
  t_poststream_review_board --> b_negative_common
  t_poststream_review_board -.-> b_poststream_review_board_viz
  t_poststream_review_board -.-> b_research_log_pack
  t_poststream_review_board -.-> b_memory_pack
  t_daily_work_sheet --> b_master_style
  t_daily_work_sheet --> b_character_kafka
  t_daily_work_sheet --> b_daily_work_sheet_vlog
  t_daily_work_sheet --> b_local_offline_pack
  t_daily_work_sheet --> b_speech_mode_kafka
  t_daily_work_sheet --> b_research_log_pack
  t_daily_work_sheet --> b_negative_common
  t_stream_start_banner --> b_master_style
  t_stream_start_banner --> b_character_kafka
  t_stream_start_banner --> b_reaction_focus
  t_stream_start_banner --> b_stream_start_banner_viz
  t_stream_start_banner --> b_announcement_text_pack
  t_stream_start_banner --> b_text_style_jp
  t_stream_start_banner --> b_effects_pack
  t_stream_start_banner --> b_negative_common
```

### Block Relations

```mermaid
flowchart LR
  classDef template fill:#dbeafe,stroke:#2563eb,color:#0f172a,stroke-width:1px;
  classDef block fill:#dcfce7,stroke:#059669,color:#0f172a,stroke-width:1px;
  subgraph blocks["Blocks"]
    direction TB
    subgraph cat_01["形式・レイアウト"]
      direction TB
      b_sticker_sheet_layout["4x4 ステッカーシート<br/><small>sticker_sheet_layout</small>"]:::block
      b_joinwars_layout["JoinWars用レイアウト<br/><small>joinwars_layout</small>"]:::block
      b_character_sheet_kafka["Kafka キャラデザインシート<br/><small>character_sheet_kafka</small>"]:::block
      b_morning_tweet_layout["おはツイレイアウト<br/><small>morning_tweet_layout</small>"]:::block
      b_archive_index_vlog["アーカイブ索引<br/><small>archive_index_vlog</small>"]:::block
      b_cardgame_post_layout["カードゲームレイアウト<br/><small>cardgame_post_layout</small>"]:::block
      b_cosplay_post_layout["コスプレレイアウト<br/><small>cosplay_post_layout</small>"]:::block
      b_persona_sheet_vlog["パーソナ設定シート<br/><small>persona_sheet_vlog</small>"]:::block
      b_poker_post_layout["ポーカーレイアウト<br/><small>poker_post_layout</small>"]:::block
      b_persona_poster_viz["人格ポスター<br/><small>persona_poster_viz</small>"]:::block
      b_daily_work_sheet_vlog["作業管理テンプレート<br/><small>daily_work_sheet_vlog</small>"]:::block
      b_archive_contact_sheet_viz["成果物一覧（コンタクトシート）<br/><small>archive_contact_sheet_viz</small>"]:::block
      b_summary_sheet_vlog["振り返りサマリー<br/><small>summary_sheet_vlog</small>"]:::block
      b_status_post_layout["日常ステータスレイアウト<br/><small>status_post_layout</small>"]:::block
      b_comic_layout["漫画レイアウト<br/><small>comic_layout</small>"]:::block
      b_prompt_archive_sheet_vlog["生成台帳<br/><small>prompt_archive_sheet_vlog</small>"]:::block
      b_photo_prompt_sheet_vlog["画像生成台帳（詳細）<br/><small>photo_prompt_sheet_vlog</small>"]:::block
      b_memory_note_board_viz["記憶メモ（記録用ボード）<br/><small>memory_note_board_viz</small>"]:::block
      b_topic_redirect_banner_viz["話題切り替え用バナー<br/><small>topic_redirect_banner_viz</small>"]:::block
      b_reading_post_layout["読書シーン用レイアウト<br/><small>reading_post_layout</small>"]:::block
      b_reply_stamp_sheet_viz["返信スタンプ（グリッド）<br/><small>reply_stamp_sheet_viz</small>"]:::block
      b_poststream_review_board_viz["配信振り返り（レビュー用）<br/><small>poststream_review_board_viz</small>"]:::block
      b_stream_start_banner_viz["配信開始バナー<br/><small>stream_start_banner_viz</small>"]:::block
    end
    subgraph cat_02["背景"]
      direction TB
      b_joinwars_scene_kafka["JoinWars背景<br/><small>joinwars_scene_kafka</small>"]:::block
      b_goodnight_scene_kafka["おやすみ背景<br/><small>goodnight_scene_kafka</small>"]:::block
      b_cosplay_scene_kafka["コスプレ撮影背景<br/><small>cosplay_scene_kafka</small>"]:::block
      b_fantasy_card_game_scene_kafka["ファンタジーカード盤面<br/><small>fantasy_card_game_scene_kafka</small>"]:::block
      b_poker_table_scene_kafka["ポーカーテーブル背景<br/><small>poker_table_scene_kafka</small>"]:::block
      b_break_scene_kafka["休憩背景<br/><small>break_scene_kafka</small>"]:::block
      b_work_start_scene_kafka["作業開始背景<br/><small>work_start_scene_kafka</small>"]:::block
      b_morning_background_winter_kafka["冬朝背景<br/><small>morning_background_winter_kafka</small>"]:::block
      b_morning_scene_commute_kafka["出発前の朝背景<br/><small>morning_scene_commute_kafka</small>"]:::block
      b_morning_background_summer_kafka["夏朝背景<br/><small>morning_background_summer_kafka</small>"]:::block
      b_morning_scene_sleepy_kafka["寝起きの朝背景<br/><small>morning_scene_sleepy_kafka</small>"]:::block
      b_morning_background_spring_kafka["春朝背景<br/><small>morning_background_spring_kafka</small>"]:::block
      b_morning_scene_coffee_kafka["朝コーヒー背景<br/><small>morning_scene_coffee_kafka</small>"]:::block
      b_reading_scene_seaside_kafka["海辺の読書背景<br/><small>reading_scene_seaside_kafka</small>"]:::block
      b_morning_background_autumn_kafka["秋朝背景<br/><small>morning_background_autumn_kafka</small>"]:::block
      b_morning_scene_window_kafka["窓際の朝背景<br/><small>morning_scene_window_kafka</small>"]:::block
      b_reading_scene_general_kafka["読書背景<br/><small>reading_scene_general_kafka</small>"]:::block
      b_reading_scene_anne_kafka["赤毛のアン読書背景<br/><small>reading_scene_anne_kafka</small>"]:::block
      b_progress_scene_kafka["進捗背景<br/><small>progress_scene_kafka</small>"]:::block
      b_morning_scene_rain_kafka["雨の日の朝背景<br/><small>morning_scene_rain_kafka</small>"]:::block
    end
    subgraph cat_03["セリフ・フレーズ"]
      direction TB
      b_joinwars_status_text_pack["JoinWars文言<br/><small>joinwars_status_text_pack</small>"]:::block
      b_morning_tweet_text_pack["おはツイ文言<br/><small>morning_tweet_text_pack</small>"]:::block
      b_card_game_status_text_pack["カードゲーム文言<br/><small>card_game_status_text_pack</small>"]:::block
      b_cosplay_status_text_pack["コスプレ文言<br/><small>cosplay_status_text_pack</small>"]:::block
      b_poker_status_text_pack["ポーカーポスト文言<br/><small>poker_status_text_pack</small>"]:::block
      b_announcement_text_pack["告知文言<br/><small>announcement_text_pack</small>"]:::block
      b_daily_status_text_pack["日常ステータス文言<br/><small>daily_status_text_pack</small>"]:::block
      b_morning_situation_text_pack["朝シチュエーション文言<br/><small>morning_situation_text_pack</small>"]:::block
      b_text_content_pack["短い日本語セリフ<br/><small>text_content_pack</small>"]:::block
      b_reading_status_text_pack["読書文言<br/><small>reading_status_text_pack</small>"]:::block
    end
    subgraph cat_04["ポーズ"]
      direction TB
      b_morning_pose_coffee_kafka["コーヒーおはツイ姿勢<br/><small>morning_pose_coffee_kafka</small>"]:::block
      b_morning_pose_winter_kafka["冬おはツイ姿勢<br/><small>morning_pose_winter_kafka</small>"]:::block
      b_morning_pose_commute_kafka["出発前おはツイ姿勢<br/><small>morning_pose_commute_kafka</small>"]:::block
      b_morning_pose_summer_kafka["夏おはツイ姿勢<br/><small>morning_pose_summer_kafka</small>"]:::block
      b_morning_pose_sleepy_kafka["寝起きおはツイ姿勢<br/><small>morning_pose_sleepy_kafka</small>"]:::block
      b_morning_pose_spring_kafka["春おはツイ姿勢<br/><small>morning_pose_spring_kafka</small>"]:::block
      b_morning_pose_autumn_kafka["秋おはツイ姿勢<br/><small>morning_pose_autumn_kafka</small>"]:::block
      b_morning_pose_window_kafka["窓際おはツイ姿勢<br/><small>morning_pose_window_kafka</small>"]:::block
      b_reading_pose_kafka["読書ポーズ<br/><small>reading_pose_kafka</small>"]:::block
      b_morning_pose_rain_kafka["雨の日おはツイ姿勢<br/><small>morning_pose_rain_kafka</small>"]:::block
    end
    subgraph cat_05["衣装"]
      direction TB
      b_joinwars_style_kafka["JoinWars衣装<br/><small>joinwars_style_kafka</small>"]:::block
      b_cosplay_event_outfit_kafka["コスプレ衣装<br/><small>cosplay_event_outfit_kafka</small>"]:::block
      b_fantasy_card_game_style_kafka["ファンタジーカードゲーム衣装<br/><small>fantasy_card_game_style_kafka</small>"]:::block
      b_poker_dealer_style_kafka["ポーカーディーラー衣装<br/><small>poker_dealer_style_kafka</small>"]:::block
      b_seasonal_outfit_winter_kafka["冬衣装<br/><small>seasonal_outfit_winter_kafka</small>"]:::block
      b_seasonal_outfit_summer_kafka["夏衣装<br/><small>seasonal_outfit_summer_kafka</small>"]:::block
      b_seasonal_outfit_spring_kafka["春衣装<br/><small>seasonal_outfit_spring_kafka</small>"]:::block
      b_seasonal_outfit_autumn_kafka["秋衣装<br/><small>seasonal_outfit_autumn_kafka</small>"]:::block
      b_reading_outfit_kafka["読書衣装<br/><small>reading_outfit_kafka</small>"]:::block
    end
    subgraph cat_06["ブランド"]
      direction TB
      b_icon_mark_only_kafka["アイコン単独<br/><small>icon_mark_only_kafka</small>"]:::block
      b_frame_only_kafka["フレーム単独<br/><small>frame_only_kafka</small>"]:::block
      b_logo_only_kafka["ロゴ単独<br/><small>logo_only_kafka</small>"]:::block
      b_logo_orbit_kafka["宇宙ロゴ単独<br/><small>logo_orbit_kafka</small>"]:::block
      b_wordmark_only_kafka["文字ロゴ単独<br/><small>wordmark_only_kafka</small>"]:::block
    end
    subgraph cat_07["テキスト"]
      direction TB
      b_subtitle_pack["字幕・テロップ<br/><small>subtitle_pack</small>"]:::block
      b_text_style_jp["日本語文字<br/><small>text_style_jp</small>"]:::block
    end
    subgraph cat_08["リプライ・対話"]
      direction TB
      b_chat_reply_pack["コメント返し<br/><small>chat_reply_pack</small>"]:::block
      b_safe_reply_pack["話題切り替え<br/><small>safe_reply_pack</small>"]:::block
    end
    subgraph cat_09["演出"]
      direction TB
      b_vfx_trigger_pack["感情演出<br/><small>vfx_trigger_pack</small>"]:::block
      b_effects_pack["装飾効果<br/><small>effects_pack</small>"]:::block
    end
    subgraph cat_10["表情"]
      direction TB
      b_expressions_pack["反応集<br/><small>expressions_pack</small>"]:::block
      b_reaction_focus["表情強調<br/><small>reaction_focus</small>"]:::block
    end
    subgraph cat_11["アバター"]
      direction TB
      b_avatar_mode_pack["アバターモード<br/><small>avatar_mode_pack</small>"]:::block
    end
    subgraph cat_12["キャラクター"]
      direction TB
      b_character_kafka["KAFKA<br/><small>character_kafka</small>"]:::block
    end
    subgraph cat_13["キャラ衣装"]
      direction TB
      b_outfit_kafka["衣装<br/><small>outfit_kafka</small>"]:::block
    end
    subgraph cat_14["コンフィグ"]
      direction TB
      b_character_customization_pack["キャラ設定<br/><small>character_customization_pack</small>"]:::block
    end
    subgraph cat_15["システム・実行"]
      direction TB
      b_local_offline_pack["ローカル優先<br/><small>local_offline_pack</small>"]:::block
    end
    subgraph cat_16["ネガティブ"]
      direction TB
      b_negative_common["共通ネガティブ<br/><small>negative_common</small>"]:::block
    end
    subgraph cat_17["リサーチ"]
      direction TB
      b_source_research["再調査メモ<br/><small>source_research</small>"]:::block
    end
    subgraph cat_18["人格"]
      direction TB
      b_persona_pack["自律人格<br/><small>persona_pack</small>"]:::block
    end
    subgraph cat_19["制御"]
      direction TB
      b_control_panel_pack["操作パネル<br/><small>control_panel_pack</small>"]:::block
    end
    subgraph cat_20["基準"]
      direction TB
      b_master_style["マスタースタイル<br/><small>master_style</small>"]:::block
    end
    subgraph cat_21["安全"]
      direction TB
      b_moderation_pack["モデレーション<br/><small>moderation_pack</small>"]:::block
    end
    subgraph cat_22["展示・サイン"]
      direction TB
      b_demo_mode_pack["デモモード<br/><small>demo_mode_pack</small>"]:::block
    end
    subgraph cat_23["性格・トーン"]
      direction TB
      b_speech_mode_kafka["かふからしい発話モード<br/><small>speech_mode_kafka</small>"]:::block
    end
    subgraph cat_24["拡張"]
      direction TB
      b_plugin_pack["外部連携<br/><small>plugin_pack</small>"]:::block
    end
    subgraph cat_25["発表"]
      direction TB
      b_slide_pack["スライド発表<br/><small>slide_pack</small>"]:::block
    end
    subgraph cat_26["記憶"]
      direction TB
      b_memory_pack["記憶管理<br/><small>memory_pack</small>"]:::block
    end
    subgraph cat_27["記録・ログ"]
      direction TB
      b_research_log_pack["振り返りログ<br/><small>research_log_pack</small>"]:::block
    end
    subgraph cat_28["配信"]
      direction TB
      b_chat_platform_pack["配信チャット<br/><small>chat_platform_pack</small>"]:::block
    end
    subgraph cat_29["音声"]
      direction TB
      b_voice_pipeline_pack["音声パイプライン<br/><small>voice_pipeline_pack</small>"]:::block
    end
  end
  subgraph templates["Referenced Templates"]
    direction TB
      t_comment_reply_guide["Kafka コメント返しガイド<br/><small>comment_reply_guide</small>"]:::template
      t_slide_talk["Kafka スライド発表<br/><small>slide_talk</small>"]:::template
      t_persona_sheet["Kafka 人格固定カード<br/><small>persona_sheet</small>"]:::template
      t_ai_tuber_ops_pack["Kafka 配信後レビューカード<br/><small>ai_tuber_ops_pack</small>"]:::template
      t_daily_work_sheet["Kafka 配信運用カード<br/><small>daily_work_sheet</small>"]:::template
  end
  b_morning_tweet_layout -.-> b_status_post_layout
  b_chat_reply_pack -.-> b_safe_reply_pack
  b_chat_reply_pack -.-> b_speech_mode_kafka
  b_slide_pack -.-> t_ai_tuber_ops_pack
  b_slide_pack -.-> t_comment_reply_guide
  b_slide_pack -.-> t_slide_talk
  b_persona_sheet_vlog -.-> t_persona_sheet
  b_persona_poster_viz -.-> b_persona_sheet_vlog
  b_persona_pack -.-> b_persona_sheet_vlog
  b_persona_pack -.-> b_persona_poster_viz
  b_persona_poster_viz -.-> b_speech_mode_kafka
  b_daily_work_sheet_vlog -.-> t_daily_work_sheet
  b_daily_work_sheet_vlog -.-> t_daily_work_sheet
  b_daily_work_sheet_vlog -.-> b_research_log_pack
  b_daily_work_sheet_vlog -.-> b_memory_pack
  b_expressions_pack -.-> b_reaction_focus
  b_archive_contact_sheet_viz -.-> b_prompt_archive_sheet_vlog
  b_archive_contact_sheet_viz -.-> b_prompt_archive_sheet_vlog
  b_archive_contact_sheet_viz -.-> b_archive_index_vlog
  b_morning_tweet_layout -.-> b_status_post_layout
  b_persona_pack -.-> b_speech_mode_kafka
  b_reaction_focus -.-> b_expressions_pack
  b_reaction_focus -.-> b_text_content_pack
  b_memory_note_board_viz -.-> b_memory_pack
  b_memory_note_board_viz -.-> b_memory_pack
  b_archive_contact_sheet_viz -.-> b_memory_note_board_viz
  b_chat_reply_pack -.-> b_topic_redirect_banner_viz
  b_safe_reply_pack -.-> b_topic_redirect_banner_viz
  b_reply_stamp_sheet_viz -.-> b_reaction_focus
  b_reaction_focus -.-> b_reply_stamp_sheet_viz
  b_reply_stamp_sheet_viz -.-> b_text_style_jp
  b_poststream_review_board_viz -.-> b_research_log_pack
  b_memory_pack -.-> b_poststream_review_board_viz
```

## Templates / social
- Prompt Vault DB Graph | Templates | kind:social

### Template Composition

```mermaid
flowchart LR
  classDef template fill:#dbeafe,stroke:#2563eb,color:#0f172a,stroke-width:1px;
  classDef block fill:#dcfce7,stroke:#059669,color:#0f172a,stroke-width:1px;
  subgraph templates["Templates"]
    direction TB
    subgraph kind_01["social"]
      direction TB
      t_joinwars_post["Kafka JoinWars投稿<br/><small>joinwars_post</small>"]:::template
      t_morning_tweet_coffee["Kafka おはツイ コーヒー<br/><small>morning_tweet_coffee</small>"]:::template
      t_morning_tweet_winter["Kafka おはツイ 冬<br/><small>morning_tweet_winter</small>"]:::template
      t_morning_tweet_commute["Kafka おはツイ 出発前<br/><small>morning_tweet_commute</small>"]:::template
      t_morning_tweet_summer["Kafka おはツイ 夏<br/><small>morning_tweet_summer</small>"]:::template
      t_morning_tweet_sleepy["Kafka おはツイ 寝起き<br/><small>morning_tweet_sleepy</small>"]:::template
      t_morning_tweet_spring["Kafka おはツイ 春<br/><small>morning_tweet_spring</small>"]:::template
      t_morning_tweet_autumn["Kafka おはツイ 秋<br/><small>morning_tweet_autumn</small>"]:::template
      t_morning_tweet_window["Kafka おはツイ 窓際<br/><small>morning_tweet_window</small>"]:::template
      t_morning_tweet_rain["Kafka おはツイ 雨の日<br/><small>morning_tweet_rain</small>"]:::template
      t_goodnight_post["Kafka おやすみポスト<br/><small>goodnight_post</small>"]:::template
      t_cardgame_post["Kafka カードゲーム投稿<br/><small>cardgame_post</small>"]:::template
      t_cosplay_post["Kafka コスプレ投稿<br/><small>cosplay_post</small>"]:::template
      t_poker_post["Kafka ポーカー投稿<br/><small>poker_post</small>"]:::template
      t_break_post["Kafka 休憩ポスト<br/><small>break_post</small>"]:::template
      t_work_start_post["Kafka 作業開始ポスト<br/><small>work_start_post</small>"]:::template
      t_reading_post_seaside["Kafka 海辺の読書投稿<br/><small>reading_post_seaside</small>"]:::template
      t_reading_post_general["Kafka 読書投稿<br/><small>reading_post_general</small>"]:::template
      t_reading_post_anne["Kafka 赤毛のアン読書投稿<br/><small>reading_post_anne</small>"]:::template
      t_progress_post["Kafka 進捗ポスト<br/><small>progress_post</small>"]:::template
    end
  end
  subgraph blocks["Blocks"]
    direction TB
    subgraph cat_01["形式・レイアウト"]
      direction TB
      b_sticker_sheet_layout["4x4 ステッカーシート<br/><small>sticker_sheet_layout</small>"]:::block
      b_joinwars_layout["JoinWars用レイアウト<br/><small>joinwars_layout</small>"]:::block
      b_character_sheet_kafka["Kafka キャラデザインシート<br/><small>character_sheet_kafka</small>"]:::block
      b_morning_tweet_layout["おはツイレイアウト<br/><small>morning_tweet_layout</small>"]:::block
      b_archive_index_vlog["アーカイブ索引<br/><small>archive_index_vlog</small>"]:::block
      b_cardgame_post_layout["カードゲームレイアウト<br/><small>cardgame_post_layout</small>"]:::block
      b_cosplay_post_layout["コスプレレイアウト<br/><small>cosplay_post_layout</small>"]:::block
      b_persona_sheet_vlog["パーソナ設定シート<br/><small>persona_sheet_vlog</small>"]:::block
      b_poker_post_layout["ポーカーレイアウト<br/><small>poker_post_layout</small>"]:::block
      b_persona_poster_viz["人格ポスター<br/><small>persona_poster_viz</small>"]:::block
      b_daily_work_sheet_vlog["作業管理テンプレート<br/><small>daily_work_sheet_vlog</small>"]:::block
      b_archive_contact_sheet_viz["成果物一覧（コンタクトシート）<br/><small>archive_contact_sheet_viz</small>"]:::block
      b_summary_sheet_vlog["振り返りサマリー<br/><small>summary_sheet_vlog</small>"]:::block
      b_status_post_layout["日常ステータスレイアウト<br/><small>status_post_layout</small>"]:::block
      b_comic_layout["漫画レイアウト<br/><small>comic_layout</small>"]:::block
      b_prompt_archive_sheet_vlog["生成台帳<br/><small>prompt_archive_sheet_vlog</small>"]:::block
      b_photo_prompt_sheet_vlog["画像生成台帳（詳細）<br/><small>photo_prompt_sheet_vlog</small>"]:::block
      b_memory_note_board_viz["記憶メモ（記録用ボード）<br/><small>memory_note_board_viz</small>"]:::block
      b_topic_redirect_banner_viz["話題切り替え用バナー<br/><small>topic_redirect_banner_viz</small>"]:::block
      b_reading_post_layout["読書シーン用レイアウト<br/><small>reading_post_layout</small>"]:::block
      b_reply_stamp_sheet_viz["返信スタンプ（グリッド）<br/><small>reply_stamp_sheet_viz</small>"]:::block
      b_poststream_review_board_viz["配信振り返り（レビュー用）<br/><small>poststream_review_board_viz</small>"]:::block
      b_stream_start_banner_viz["配信開始バナー<br/><small>stream_start_banner_viz</small>"]:::block
    end
    subgraph cat_02["背景"]
      direction TB
      b_joinwars_scene_kafka["JoinWars背景<br/><small>joinwars_scene_kafka</small>"]:::block
      b_goodnight_scene_kafka["おやすみ背景<br/><small>goodnight_scene_kafka</small>"]:::block
      b_cosplay_scene_kafka["コスプレ撮影背景<br/><small>cosplay_scene_kafka</small>"]:::block
      b_fantasy_card_game_scene_kafka["ファンタジーカード盤面<br/><small>fantasy_card_game_scene_kafka</small>"]:::block
      b_poker_table_scene_kafka["ポーカーテーブル背景<br/><small>poker_table_scene_kafka</small>"]:::block
      b_break_scene_kafka["休憩背景<br/><small>break_scene_kafka</small>"]:::block
      b_work_start_scene_kafka["作業開始背景<br/><small>work_start_scene_kafka</small>"]:::block
      b_morning_background_winter_kafka["冬朝背景<br/><small>morning_background_winter_kafka</small>"]:::block
      b_morning_scene_commute_kafka["出発前の朝背景<br/><small>morning_scene_commute_kafka</small>"]:::block
      b_morning_background_summer_kafka["夏朝背景<br/><small>morning_background_summer_kafka</small>"]:::block
      b_morning_scene_sleepy_kafka["寝起きの朝背景<br/><small>morning_scene_sleepy_kafka</small>"]:::block
      b_morning_background_spring_kafka["春朝背景<br/><small>morning_background_spring_kafka</small>"]:::block
      b_morning_scene_coffee_kafka["朝コーヒー背景<br/><small>morning_scene_coffee_kafka</small>"]:::block
      b_reading_scene_seaside_kafka["海辺の読書背景<br/><small>reading_scene_seaside_kafka</small>"]:::block
      b_morning_background_autumn_kafka["秋朝背景<br/><small>morning_background_autumn_kafka</small>"]:::block
      b_morning_scene_window_kafka["窓際の朝背景<br/><small>morning_scene_window_kafka</small>"]:::block
      b_reading_scene_general_kafka["読書背景<br/><small>reading_scene_general_kafka</small>"]:::block
      b_reading_scene_anne_kafka["赤毛のアン読書背景<br/><small>reading_scene_anne_kafka</small>"]:::block
      b_progress_scene_kafka["進捗背景<br/><small>progress_scene_kafka</small>"]:::block
      b_morning_scene_rain_kafka["雨の日の朝背景<br/><small>morning_scene_rain_kafka</small>"]:::block
    end
    subgraph cat_03["セリフ・フレーズ"]
      direction TB
      b_joinwars_status_text_pack["JoinWars文言<br/><small>joinwars_status_text_pack</small>"]:::block
      b_morning_tweet_text_pack["おはツイ文言<br/><small>morning_tweet_text_pack</small>"]:::block
      b_card_game_status_text_pack["カードゲーム文言<br/><small>card_game_status_text_pack</small>"]:::block
      b_cosplay_status_text_pack["コスプレ文言<br/><small>cosplay_status_text_pack</small>"]:::block
      b_poker_status_text_pack["ポーカーポスト文言<br/><small>poker_status_text_pack</small>"]:::block
      b_announcement_text_pack["告知文言<br/><small>announcement_text_pack</small>"]:::block
      b_daily_status_text_pack["日常ステータス文言<br/><small>daily_status_text_pack</small>"]:::block
      b_morning_situation_text_pack["朝シチュエーション文言<br/><small>morning_situation_text_pack</small>"]:::block
      b_text_content_pack["短い日本語セリフ<br/><small>text_content_pack</small>"]:::block
      b_reading_status_text_pack["読書文言<br/><small>reading_status_text_pack</small>"]:::block
    end
    subgraph cat_04["ポーズ"]
      direction TB
      b_morning_pose_coffee_kafka["コーヒーおはツイ姿勢<br/><small>morning_pose_coffee_kafka</small>"]:::block
      b_morning_pose_winter_kafka["冬おはツイ姿勢<br/><small>morning_pose_winter_kafka</small>"]:::block
      b_morning_pose_commute_kafka["出発前おはツイ姿勢<br/><small>morning_pose_commute_kafka</small>"]:::block
      b_morning_pose_summer_kafka["夏おはツイ姿勢<br/><small>morning_pose_summer_kafka</small>"]:::block
      b_morning_pose_sleepy_kafka["寝起きおはツイ姿勢<br/><small>morning_pose_sleepy_kafka</small>"]:::block
      b_morning_pose_spring_kafka["春おはツイ姿勢<br/><small>morning_pose_spring_kafka</small>"]:::block
      b_morning_pose_autumn_kafka["秋おはツイ姿勢<br/><small>morning_pose_autumn_kafka</small>"]:::block
      b_morning_pose_window_kafka["窓際おはツイ姿勢<br/><small>morning_pose_window_kafka</small>"]:::block
      b_reading_pose_kafka["読書ポーズ<br/><small>reading_pose_kafka</small>"]:::block
      b_morning_pose_rain_kafka["雨の日おはツイ姿勢<br/><small>morning_pose_rain_kafka</small>"]:::block
    end
    subgraph cat_05["衣装"]
      direction TB
      b_joinwars_style_kafka["JoinWars衣装<br/><small>joinwars_style_kafka</small>"]:::block
      b_cosplay_event_outfit_kafka["コスプレ衣装<br/><small>cosplay_event_outfit_kafka</small>"]:::block
      b_fantasy_card_game_style_kafka["ファンタジーカードゲーム衣装<br/><small>fantasy_card_game_style_kafka</small>"]:::block
      b_poker_dealer_style_kafka["ポーカーディーラー衣装<br/><small>poker_dealer_style_kafka</small>"]:::block
      b_seasonal_outfit_winter_kafka["冬衣装<br/><small>seasonal_outfit_winter_kafka</small>"]:::block
      b_seasonal_outfit_summer_kafka["夏衣装<br/><small>seasonal_outfit_summer_kafka</small>"]:::block
      b_seasonal_outfit_spring_kafka["春衣装<br/><small>seasonal_outfit_spring_kafka</small>"]:::block
      b_seasonal_outfit_autumn_kafka["秋衣装<br/><small>seasonal_outfit_autumn_kafka</small>"]:::block
      b_reading_outfit_kafka["読書衣装<br/><small>reading_outfit_kafka</small>"]:::block
    end
    subgraph cat_06["ブランド"]
      direction TB
      b_icon_mark_only_kafka["アイコン単独<br/><small>icon_mark_only_kafka</small>"]:::block
      b_frame_only_kafka["フレーム単独<br/><small>frame_only_kafka</small>"]:::block
      b_logo_only_kafka["ロゴ単独<br/><small>logo_only_kafka</small>"]:::block
      b_logo_orbit_kafka["宇宙ロゴ単独<br/><small>logo_orbit_kafka</small>"]:::block
      b_wordmark_only_kafka["文字ロゴ単独<br/><small>wordmark_only_kafka</small>"]:::block
    end
    subgraph cat_07["テキスト"]
      direction TB
      b_subtitle_pack["字幕・テロップ<br/><small>subtitle_pack</small>"]:::block
      b_text_style_jp["日本語文字<br/><small>text_style_jp</small>"]:::block
    end
    subgraph cat_08["リプライ・対話"]
      direction TB
      b_chat_reply_pack["コメント返し<br/><small>chat_reply_pack</small>"]:::block
      b_safe_reply_pack["話題切り替え<br/><small>safe_reply_pack</small>"]:::block
    end
    subgraph cat_09["演出"]
      direction TB
      b_vfx_trigger_pack["感情演出<br/><small>vfx_trigger_pack</small>"]:::block
      b_effects_pack["装飾効果<br/><small>effects_pack</small>"]:::block
    end
    subgraph cat_10["表情"]
      direction TB
      b_expressions_pack["反応集<br/><small>expressions_pack</small>"]:::block
      b_reaction_focus["表情強調<br/><small>reaction_focus</small>"]:::block
    end
    subgraph cat_11["アバター"]
      direction TB
      b_avatar_mode_pack["アバターモード<br/><small>avatar_mode_pack</small>"]:::block
    end
    subgraph cat_12["キャラクター"]
      direction TB
      b_character_kafka["KAFKA<br/><small>character_kafka</small>"]:::block
    end
    subgraph cat_13["キャラ衣装"]
      direction TB
      b_outfit_kafka["衣装<br/><small>outfit_kafka</small>"]:::block
    end
    subgraph cat_14["コンフィグ"]
      direction TB
      b_character_customization_pack["キャラ設定<br/><small>character_customization_pack</small>"]:::block
    end
    subgraph cat_15["システム・実行"]
      direction TB
      b_local_offline_pack["ローカル優先<br/><small>local_offline_pack</small>"]:::block
    end
    subgraph cat_16["ネガティブ"]
      direction TB
      b_negative_common["共通ネガティブ<br/><small>negative_common</small>"]:::block
    end
    subgraph cat_17["リサーチ"]
      direction TB
      b_source_research["再調査メモ<br/><small>source_research</small>"]:::block
    end
    subgraph cat_18["人格"]
      direction TB
      b_persona_pack["自律人格<br/><small>persona_pack</small>"]:::block
    end
    subgraph cat_19["制御"]
      direction TB
      b_control_panel_pack["操作パネル<br/><small>control_panel_pack</small>"]:::block
    end
    subgraph cat_20["基準"]
      direction TB
      b_master_style["マスタースタイル<br/><small>master_style</small>"]:::block
    end
    subgraph cat_21["安全"]
      direction TB
      b_moderation_pack["モデレーション<br/><small>moderation_pack</small>"]:::block
    end
    subgraph cat_22["展示・サイン"]
      direction TB
      b_demo_mode_pack["デモモード<br/><small>demo_mode_pack</small>"]:::block
    end
    subgraph cat_23["性格・トーン"]
      direction TB
      b_speech_mode_kafka["かふからしい発話モード<br/><small>speech_mode_kafka</small>"]:::block
    end
    subgraph cat_24["拡張"]
      direction TB
      b_plugin_pack["外部連携<br/><small>plugin_pack</small>"]:::block
    end
    subgraph cat_25["発表"]
      direction TB
      b_slide_pack["スライド発表<br/><small>slide_pack</small>"]:::block
    end
    subgraph cat_26["記憶"]
      direction TB
      b_memory_pack["記憶管理<br/><small>memory_pack</small>"]:::block
    end
    subgraph cat_27["記録・ログ"]
      direction TB
      b_research_log_pack["振り返りログ<br/><small>research_log_pack</small>"]:::block
    end
    subgraph cat_28["配信"]
      direction TB
      b_chat_platform_pack["配信チャット<br/><small>chat_platform_pack</small>"]:::block
    end
    subgraph cat_29["音声"]
      direction TB
      b_voice_pipeline_pack["音声パイプライン<br/><small>voice_pipeline_pack</small>"]:::block
    end
  end
  t_joinwars_post --> b_master_style
  t_joinwars_post --> b_character_kafka
  t_joinwars_post --> b_joinwars_layout
  t_joinwars_post --> b_joinwars_scene_kafka
  t_joinwars_post --> b_joinwars_style_kafka
  t_joinwars_post --> b_joinwars_status_text_pack
  t_joinwars_post --> b_text_style_jp
  t_joinwars_post --> b_negative_common
  t_morning_tweet_coffee --> b_master_style
  t_morning_tweet_coffee --> b_character_kafka
  t_morning_tweet_coffee --> b_outfit_kafka
  t_morning_tweet_coffee --> b_morning_pose_coffee_kafka
  t_morning_tweet_coffee --> b_morning_scene_coffee_kafka
  t_morning_tweet_coffee --> b_morning_tweet_layout
  t_morning_tweet_coffee --> b_morning_situation_text_pack
  t_morning_tweet_coffee --> b_text_style_jp
  t_morning_tweet_coffee --> b_negative_common
  t_morning_tweet_winter --> b_master_style
  t_morning_tweet_winter --> b_character_kafka
  t_morning_tweet_winter --> b_seasonal_outfit_winter_kafka
  t_morning_tweet_winter --> b_morning_pose_winter_kafka
  t_morning_tweet_winter --> b_morning_background_winter_kafka
  t_morning_tweet_winter --> b_morning_tweet_layout
  t_morning_tweet_winter --> b_morning_tweet_text_pack
  t_morning_tweet_winter --> b_text_style_jp
  t_morning_tweet_winter --> b_effects_pack
  t_morning_tweet_winter --> b_negative_common
  t_morning_tweet_commute --> b_master_style
  t_morning_tweet_commute --> b_character_kafka
  t_morning_tweet_commute --> b_outfit_kafka
  t_morning_tweet_commute --> b_morning_pose_commute_kafka
  t_morning_tweet_commute --> b_morning_scene_commute_kafka
  t_morning_tweet_commute --> b_morning_tweet_layout
  t_morning_tweet_commute --> b_morning_situation_text_pack
  t_morning_tweet_commute --> b_text_style_jp
  t_morning_tweet_commute --> b_negative_common
  t_morning_tweet_summer --> b_master_style
  t_morning_tweet_summer --> b_character_kafka
  t_morning_tweet_summer --> b_seasonal_outfit_summer_kafka
  t_morning_tweet_summer --> b_morning_pose_summer_kafka
  t_morning_tweet_summer --> b_morning_background_summer_kafka
  t_morning_tweet_summer --> b_morning_tweet_layout
  t_morning_tweet_summer --> b_morning_tweet_text_pack
  t_morning_tweet_summer --> b_text_style_jp
  t_morning_tweet_summer --> b_effects_pack
  t_morning_tweet_summer --> b_negative_common
  t_morning_tweet_sleepy --> b_master_style
  t_morning_tweet_sleepy --> b_character_kafka
  t_morning_tweet_sleepy --> b_outfit_kafka
  t_morning_tweet_sleepy --> b_morning_pose_sleepy_kafka
  t_morning_tweet_sleepy --> b_morning_scene_sleepy_kafka
  t_morning_tweet_sleepy --> b_morning_tweet_layout
  t_morning_tweet_sleepy --> b_morning_situation_text_pack
  t_morning_tweet_sleepy --> b_text_style_jp
  t_morning_tweet_sleepy --> b_negative_common
  t_morning_tweet_spring --> b_master_style
  t_morning_tweet_spring --> b_character_kafka
  t_morning_tweet_spring --> b_seasonal_outfit_spring_kafka
  t_morning_tweet_spring --> b_morning_pose_spring_kafka
  t_morning_tweet_spring --> b_morning_background_spring_kafka
  t_morning_tweet_spring --> b_morning_tweet_layout
  t_morning_tweet_spring --> b_morning_tweet_text_pack
  t_morning_tweet_spring --> b_text_style_jp
  t_morning_tweet_spring --> b_effects_pack
  t_morning_tweet_spring --> b_negative_common
  t_morning_tweet_autumn --> b_master_style
  t_morning_tweet_autumn --> b_character_kafka
  t_morning_tweet_autumn --> b_seasonal_outfit_autumn_kafka
  t_morning_tweet_autumn --> b_morning_pose_autumn_kafka
  t_morning_tweet_autumn --> b_morning_background_autumn_kafka
  t_morning_tweet_autumn --> b_morning_tweet_layout
  t_morning_tweet_autumn --> b_morning_tweet_text_pack
  t_morning_tweet_autumn --> b_text_style_jp
  t_morning_tweet_autumn --> b_effects_pack
  t_morning_tweet_autumn --> b_negative_common
  t_morning_tweet_window --> b_master_style
  t_morning_tweet_window --> b_character_kafka
  t_morning_tweet_window --> b_outfit_kafka
  t_morning_tweet_window --> b_morning_pose_window_kafka
  t_morning_tweet_window --> b_morning_scene_window_kafka
  t_morning_tweet_window --> b_morning_tweet_layout
  t_morning_tweet_window --> b_morning_situation_text_pack
  t_morning_tweet_window --> b_text_style_jp
  t_morning_tweet_window --> b_negative_common
  t_morning_tweet_rain --> b_master_style
  t_morning_tweet_rain --> b_character_kafka
  t_morning_tweet_rain --> b_outfit_kafka
  t_morning_tweet_rain --> b_morning_pose_rain_kafka
  t_morning_tweet_rain --> b_morning_scene_rain_kafka
  t_morning_tweet_rain --> b_morning_tweet_layout
  t_morning_tweet_rain --> b_morning_situation_text_pack
  t_morning_tweet_rain --> b_text_style_jp
  t_morning_tweet_rain --> b_negative_common
  t_goodnight_post --> b_master_style
  t_goodnight_post --> b_character_kafka
  t_goodnight_post --> b_outfit_kafka
  t_goodnight_post --> b_goodnight_scene_kafka
  t_goodnight_post --> b_status_post_layout
  t_goodnight_post --> b_daily_status_text_pack
  t_goodnight_post --> b_text_style_jp
  t_goodnight_post --> b_negative_common
  t_cardgame_post --> b_master_style
  t_cardgame_post --> b_character_kafka
  t_cardgame_post --> b_cardgame_post_layout
  t_cardgame_post --> b_fantasy_card_game_scene_kafka
  t_cardgame_post --> b_fantasy_card_game_style_kafka
  t_cardgame_post --> b_card_game_status_text_pack
  t_cardgame_post --> b_text_style_jp
  t_cardgame_post --> b_negative_common
  t_cosplay_post --> b_master_style
  t_cosplay_post --> b_character_kafka
  t_cosplay_post --> b_cosplay_post_layout
  t_cosplay_post --> b_cosplay_scene_kafka
  t_cosplay_post --> b_cosplay_event_outfit_kafka
  t_cosplay_post --> b_cosplay_status_text_pack
  t_cosplay_post --> b_text_style_jp
  t_cosplay_post --> b_negative_common
  t_poker_post --> b_master_style
  t_poker_post --> b_character_kafka
  t_poker_post --> b_poker_post_layout
  t_poker_post --> b_poker_table_scene_kafka
  t_poker_post --> b_poker_dealer_style_kafka
  t_poker_post --> b_poker_status_text_pack
  t_poker_post --> b_text_style_jp
  t_poker_post --> b_negative_common
  t_break_post --> b_master_style
  t_break_post --> b_character_kafka
  t_break_post --> b_outfit_kafka
  t_break_post --> b_break_scene_kafka
  t_break_post --> b_status_post_layout
  t_break_post --> b_daily_status_text_pack
  t_break_post --> b_text_style_jp
  t_break_post --> b_negative_common
  t_work_start_post --> b_master_style
  t_work_start_post --> b_character_kafka
  t_work_start_post --> b_outfit_kafka
  t_work_start_post --> b_work_start_scene_kafka
  t_work_start_post --> b_status_post_layout
  t_work_start_post --> b_daily_status_text_pack
  t_work_start_post --> b_text_style_jp
  t_work_start_post --> b_negative_common
  t_reading_post_seaside --> b_master_style
  t_reading_post_seaside --> b_character_kafka
  t_reading_post_seaside --> b_reading_post_layout
  t_reading_post_seaside --> b_reading_scene_seaside_kafka
  t_reading_post_seaside --> b_reading_pose_kafka
  t_reading_post_seaside --> b_reading_outfit_kafka
  t_reading_post_seaside --> b_reading_status_text_pack
  t_reading_post_seaside --> b_text_style_jp
  t_reading_post_seaside --> b_negative_common
  t_reading_post_general --> b_master_style
  t_reading_post_general --> b_character_kafka
  t_reading_post_general --> b_reading_post_layout
  t_reading_post_general --> b_reading_scene_general_kafka
  t_reading_post_general --> b_reading_pose_kafka
  t_reading_post_general --> b_reading_outfit_kafka
  t_reading_post_general --> b_reading_status_text_pack
  t_reading_post_general --> b_text_style_jp
  t_reading_post_general --> b_negative_common
  t_reading_post_anne --> b_master_style
  t_reading_post_anne --> b_character_kafka
  t_reading_post_anne --> b_reading_post_layout
  t_reading_post_anne --> b_reading_scene_anne_kafka
  t_reading_post_anne --> b_reading_pose_kafka
  t_reading_post_anne --> b_reading_outfit_kafka
  t_reading_post_anne --> b_reading_status_text_pack
  t_reading_post_anne --> b_text_style_jp
  t_reading_post_anne --> b_negative_common
  t_progress_post --> b_master_style
  t_progress_post --> b_character_kafka
  t_progress_post --> b_outfit_kafka
  t_progress_post --> b_progress_scene_kafka
  t_progress_post --> b_status_post_layout
  t_progress_post --> b_daily_status_text_pack
  t_progress_post --> b_text_style_jp
  t_progress_post --> b_negative_common
```

## Templates / design_sheet
- Prompt Vault DB Graph | Templates | kind:design_sheet

### Template Composition

```mermaid
flowchart LR
  classDef template fill:#dbeafe,stroke:#2563eb,color:#0f172a,stroke-width:1px;
  classDef block fill:#dcfce7,stroke:#059669,color:#0f172a,stroke-width:1px;
  subgraph templates["Templates"]
    direction TB
    subgraph kind_01["design_sheet"]
      direction TB
      t_morning_tweet_index["Kafka おはツイ一覧<br/><small>morning_tweet_index</small>"]:::template
      t_character_design_sheet["Kafka キャラデザインシート<br/><small>character_design_sheet</small>"]:::template
      t_persona_poster["Kafka 人格ポスター<br/><small>persona_poster</small>"]:::template
      t_persona_sheet["Kafka 人格固定カード<br/><small>persona_sheet</small>"]:::template
      t_archive_contact_sheet["Kafka 成果物一覧<br/><small>archive_contact_sheet</small>"]:::template
      t_archive_index["Kafka 成果物回収カード<br/><small>archive_index</small>"]:::template
      t_photo_prompt_sheet["Kafka 生成素材台帳<br/><small>photo_prompt_sheet</small>"]:::template
      t_memory_note_board["Kafka 記憶メモボード<br/><small>memory_note_board</small>"]:::template
      t_memory_update_card["Kafka 記憶更新カード<br/><small>memory_update_card</small>"]:::template
      t_summary_sheet["Kafka 配信後まとめカード<br/><small>summary_sheet</small>"]:::template
      t_poststream_review_board["Kafka 配信後レビュー盤<br/><small>poststream_review_board</small>"]:::template
      t_daily_work_sheet["Kafka 配信運用カード<br/><small>daily_work_sheet</small>"]:::template
    end
  end
  subgraph blocks["Blocks"]
    direction TB
    subgraph cat_01["形式・レイアウト"]
      direction TB
      b_sticker_sheet_layout["4x4 ステッカーシート<br/><small>sticker_sheet_layout</small>"]:::block
      b_joinwars_layout["JoinWars用レイアウト<br/><small>joinwars_layout</small>"]:::block
      b_character_sheet_kafka["Kafka キャラデザインシート<br/><small>character_sheet_kafka</small>"]:::block
      b_morning_tweet_layout["おはツイレイアウト<br/><small>morning_tweet_layout</small>"]:::block
      b_archive_index_vlog["アーカイブ索引<br/><small>archive_index_vlog</small>"]:::block
      b_cardgame_post_layout["カードゲームレイアウト<br/><small>cardgame_post_layout</small>"]:::block
      b_cosplay_post_layout["コスプレレイアウト<br/><small>cosplay_post_layout</small>"]:::block
      b_persona_sheet_vlog["パーソナ設定シート<br/><small>persona_sheet_vlog</small>"]:::block
      b_poker_post_layout["ポーカーレイアウト<br/><small>poker_post_layout</small>"]:::block
      b_persona_poster_viz["人格ポスター<br/><small>persona_poster_viz</small>"]:::block
      b_daily_work_sheet_vlog["作業管理テンプレート<br/><small>daily_work_sheet_vlog</small>"]:::block
      b_archive_contact_sheet_viz["成果物一覧（コンタクトシート）<br/><small>archive_contact_sheet_viz</small>"]:::block
      b_summary_sheet_vlog["振り返りサマリー<br/><small>summary_sheet_vlog</small>"]:::block
      b_status_post_layout["日常ステータスレイアウト<br/><small>status_post_layout</small>"]:::block
      b_comic_layout["漫画レイアウト<br/><small>comic_layout</small>"]:::block
      b_prompt_archive_sheet_vlog["生成台帳<br/><small>prompt_archive_sheet_vlog</small>"]:::block
      b_photo_prompt_sheet_vlog["画像生成台帳（詳細）<br/><small>photo_prompt_sheet_vlog</small>"]:::block
      b_memory_note_board_viz["記憶メモ（記録用ボード）<br/><small>memory_note_board_viz</small>"]:::block
      b_topic_redirect_banner_viz["話題切り替え用バナー<br/><small>topic_redirect_banner_viz</small>"]:::block
      b_reading_post_layout["読書シーン用レイアウト<br/><small>reading_post_layout</small>"]:::block
      b_reply_stamp_sheet_viz["返信スタンプ（グリッド）<br/><small>reply_stamp_sheet_viz</small>"]:::block
      b_poststream_review_board_viz["配信振り返り（レビュー用）<br/><small>poststream_review_board_viz</small>"]:::block
      b_stream_start_banner_viz["配信開始バナー<br/><small>stream_start_banner_viz</small>"]:::block
    end
    subgraph cat_02["背景"]
      direction TB
      b_joinwars_scene_kafka["JoinWars背景<br/><small>joinwars_scene_kafka</small>"]:::block
      b_goodnight_scene_kafka["おやすみ背景<br/><small>goodnight_scene_kafka</small>"]:::block
      b_cosplay_scene_kafka["コスプレ撮影背景<br/><small>cosplay_scene_kafka</small>"]:::block
      b_fantasy_card_game_scene_kafka["ファンタジーカード盤面<br/><small>fantasy_card_game_scene_kafka</small>"]:::block
      b_poker_table_scene_kafka["ポーカーテーブル背景<br/><small>poker_table_scene_kafka</small>"]:::block
      b_break_scene_kafka["休憩背景<br/><small>break_scene_kafka</small>"]:::block
      b_work_start_scene_kafka["作業開始背景<br/><small>work_start_scene_kafka</small>"]:::block
      b_morning_background_winter_kafka["冬朝背景<br/><small>morning_background_winter_kafka</small>"]:::block
      b_morning_scene_commute_kafka["出発前の朝背景<br/><small>morning_scene_commute_kafka</small>"]:::block
      b_morning_background_summer_kafka["夏朝背景<br/><small>morning_background_summer_kafka</small>"]:::block
      b_morning_scene_sleepy_kafka["寝起きの朝背景<br/><small>morning_scene_sleepy_kafka</small>"]:::block
      b_morning_background_spring_kafka["春朝背景<br/><small>morning_background_spring_kafka</small>"]:::block
      b_morning_scene_coffee_kafka["朝コーヒー背景<br/><small>morning_scene_coffee_kafka</small>"]:::block
      b_reading_scene_seaside_kafka["海辺の読書背景<br/><small>reading_scene_seaside_kafka</small>"]:::block
      b_morning_background_autumn_kafka["秋朝背景<br/><small>morning_background_autumn_kafka</small>"]:::block
      b_morning_scene_window_kafka["窓際の朝背景<br/><small>morning_scene_window_kafka</small>"]:::block
      b_reading_scene_general_kafka["読書背景<br/><small>reading_scene_general_kafka</small>"]:::block
      b_reading_scene_anne_kafka["赤毛のアン読書背景<br/><small>reading_scene_anne_kafka</small>"]:::block
      b_progress_scene_kafka["進捗背景<br/><small>progress_scene_kafka</small>"]:::block
      b_morning_scene_rain_kafka["雨の日の朝背景<br/><small>morning_scene_rain_kafka</small>"]:::block
    end
    subgraph cat_03["セリフ・フレーズ"]
      direction TB
      b_joinwars_status_text_pack["JoinWars文言<br/><small>joinwars_status_text_pack</small>"]:::block
      b_morning_tweet_text_pack["おはツイ文言<br/><small>morning_tweet_text_pack</small>"]:::block
      b_card_game_status_text_pack["カードゲーム文言<br/><small>card_game_status_text_pack</small>"]:::block
      b_cosplay_status_text_pack["コスプレ文言<br/><small>cosplay_status_text_pack</small>"]:::block
      b_poker_status_text_pack["ポーカーポスト文言<br/><small>poker_status_text_pack</small>"]:::block
      b_announcement_text_pack["告知文言<br/><small>announcement_text_pack</small>"]:::block
      b_daily_status_text_pack["日常ステータス文言<br/><small>daily_status_text_pack</small>"]:::block
      b_morning_situation_text_pack["朝シチュエーション文言<br/><small>morning_situation_text_pack</small>"]:::block
      b_text_content_pack["短い日本語セリフ<br/><small>text_content_pack</small>"]:::block
      b_reading_status_text_pack["読書文言<br/><small>reading_status_text_pack</small>"]:::block
    end
    subgraph cat_04["ポーズ"]
      direction TB
      b_morning_pose_coffee_kafka["コーヒーおはツイ姿勢<br/><small>morning_pose_coffee_kafka</small>"]:::block
      b_morning_pose_winter_kafka["冬おはツイ姿勢<br/><small>morning_pose_winter_kafka</small>"]:::block
      b_morning_pose_commute_kafka["出発前おはツイ姿勢<br/><small>morning_pose_commute_kafka</small>"]:::block
      b_morning_pose_summer_kafka["夏おはツイ姿勢<br/><small>morning_pose_summer_kafka</small>"]:::block
      b_morning_pose_sleepy_kafka["寝起きおはツイ姿勢<br/><small>morning_pose_sleepy_kafka</small>"]:::block
      b_morning_pose_spring_kafka["春おはツイ姿勢<br/><small>morning_pose_spring_kafka</small>"]:::block
      b_morning_pose_autumn_kafka["秋おはツイ姿勢<br/><small>morning_pose_autumn_kafka</small>"]:::block
      b_morning_pose_window_kafka["窓際おはツイ姿勢<br/><small>morning_pose_window_kafka</small>"]:::block
      b_reading_pose_kafka["読書ポーズ<br/><small>reading_pose_kafka</small>"]:::block
      b_morning_pose_rain_kafka["雨の日おはツイ姿勢<br/><small>morning_pose_rain_kafka</small>"]:::block
    end
    subgraph cat_05["衣装"]
      direction TB
      b_joinwars_style_kafka["JoinWars衣装<br/><small>joinwars_style_kafka</small>"]:::block
      b_cosplay_event_outfit_kafka["コスプレ衣装<br/><small>cosplay_event_outfit_kafka</small>"]:::block
      b_fantasy_card_game_style_kafka["ファンタジーカードゲーム衣装<br/><small>fantasy_card_game_style_kafka</small>"]:::block
      b_poker_dealer_style_kafka["ポーカーディーラー衣装<br/><small>poker_dealer_style_kafka</small>"]:::block
      b_seasonal_outfit_winter_kafka["冬衣装<br/><small>seasonal_outfit_winter_kafka</small>"]:::block
      b_seasonal_outfit_summer_kafka["夏衣装<br/><small>seasonal_outfit_summer_kafka</small>"]:::block
      b_seasonal_outfit_spring_kafka["春衣装<br/><small>seasonal_outfit_spring_kafka</small>"]:::block
      b_seasonal_outfit_autumn_kafka["秋衣装<br/><small>seasonal_outfit_autumn_kafka</small>"]:::block
      b_reading_outfit_kafka["読書衣装<br/><small>reading_outfit_kafka</small>"]:::block
    end
    subgraph cat_06["ブランド"]
      direction TB
      b_icon_mark_only_kafka["アイコン単独<br/><small>icon_mark_only_kafka</small>"]:::block
      b_frame_only_kafka["フレーム単独<br/><small>frame_only_kafka</small>"]:::block
      b_logo_only_kafka["ロゴ単独<br/><small>logo_only_kafka</small>"]:::block
      b_logo_orbit_kafka["宇宙ロゴ単独<br/><small>logo_orbit_kafka</small>"]:::block
      b_wordmark_only_kafka["文字ロゴ単独<br/><small>wordmark_only_kafka</small>"]:::block
    end
    subgraph cat_07["テキスト"]
      direction TB
      b_subtitle_pack["字幕・テロップ<br/><small>subtitle_pack</small>"]:::block
      b_text_style_jp["日本語文字<br/><small>text_style_jp</small>"]:::block
    end
    subgraph cat_08["リプライ・対話"]
      direction TB
      b_chat_reply_pack["コメント返し<br/><small>chat_reply_pack</small>"]:::block
      b_safe_reply_pack["話題切り替え<br/><small>safe_reply_pack</small>"]:::block
    end
    subgraph cat_09["演出"]
      direction TB
      b_vfx_trigger_pack["感情演出<br/><small>vfx_trigger_pack</small>"]:::block
      b_effects_pack["装飾効果<br/><small>effects_pack</small>"]:::block
    end
    subgraph cat_10["表情"]
      direction TB
      b_expressions_pack["反応集<br/><small>expressions_pack</small>"]:::block
      b_reaction_focus["表情強調<br/><small>reaction_focus</small>"]:::block
    end
    subgraph cat_11["アバター"]
      direction TB
      b_avatar_mode_pack["アバターモード<br/><small>avatar_mode_pack</small>"]:::block
    end
    subgraph cat_12["キャラクター"]
      direction TB
      b_character_kafka["KAFKA<br/><small>character_kafka</small>"]:::block
    end
    subgraph cat_13["キャラ衣装"]
      direction TB
      b_outfit_kafka["衣装<br/><small>outfit_kafka</small>"]:::block
    end
    subgraph cat_14["コンフィグ"]
      direction TB
      b_character_customization_pack["キャラ設定<br/><small>character_customization_pack</small>"]:::block
    end
    subgraph cat_15["システム・実行"]
      direction TB
      b_local_offline_pack["ローカル優先<br/><small>local_offline_pack</small>"]:::block
    end
    subgraph cat_16["ネガティブ"]
      direction TB
      b_negative_common["共通ネガティブ<br/><small>negative_common</small>"]:::block
    end
    subgraph cat_17["リサーチ"]
      direction TB
      b_source_research["再調査メモ<br/><small>source_research</small>"]:::block
    end
    subgraph cat_18["人格"]
      direction TB
      b_persona_pack["自律人格<br/><small>persona_pack</small>"]:::block
    end
    subgraph cat_19["制御"]
      direction TB
      b_control_panel_pack["操作パネル<br/><small>control_panel_pack</small>"]:::block
    end
    subgraph cat_20["基準"]
      direction TB
      b_master_style["マスタースタイル<br/><small>master_style</small>"]:::block
    end
    subgraph cat_21["安全"]
      direction TB
      b_moderation_pack["モデレーション<br/><small>moderation_pack</small>"]:::block
    end
    subgraph cat_22["展示・サイン"]
      direction TB
      b_demo_mode_pack["デモモード<br/><small>demo_mode_pack</small>"]:::block
    end
    subgraph cat_23["性格・トーン"]
      direction TB
      b_speech_mode_kafka["かふからしい発話モード<br/><small>speech_mode_kafka</small>"]:::block
    end
    subgraph cat_24["拡張"]
      direction TB
      b_plugin_pack["外部連携<br/><small>plugin_pack</small>"]:::block
    end
    subgraph cat_25["発表"]
      direction TB
      b_slide_pack["スライド発表<br/><small>slide_pack</small>"]:::block
    end
    subgraph cat_26["記憶"]
      direction TB
      b_memory_pack["記憶管理<br/><small>memory_pack</small>"]:::block
    end
    subgraph cat_27["記録・ログ"]
      direction TB
      b_research_log_pack["振り返りログ<br/><small>research_log_pack</small>"]:::block
    end
    subgraph cat_28["配信"]
      direction TB
      b_chat_platform_pack["配信チャット<br/><small>chat_platform_pack</small>"]:::block
    end
    subgraph cat_29["音声"]
      direction TB
      b_voice_pipeline_pack["音声パイプライン<br/><small>voice_pipeline_pack</small>"]:::block
    end
  end
  t_morning_tweet_index --> b_master_style
  t_morning_tweet_index --> b_character_kafka
  t_morning_tweet_index --> b_morning_tweet_layout
  t_morning_tweet_index --> b_morning_tweet_text_pack
  t_morning_tweet_index --> b_morning_situation_text_pack
  t_morning_tweet_index --> b_text_style_jp
  t_morning_tweet_index --> b_negative_common
  t_character_design_sheet --> b_character_sheet_kafka
  t_persona_poster --> b_master_style
  t_persona_poster --> b_character_kafka
  t_persona_poster --> b_outfit_kafka
  t_persona_poster --> b_persona_poster_viz
  t_persona_poster --> b_persona_pack
  t_persona_poster --> b_text_style_jp
  t_persona_poster --> b_negative_common
  t_persona_poster -.-> b_persona_poster_viz
  t_persona_poster -.-> b_persona_pack
  t_persona_poster -.-> b_text_style_jp
  t_persona_sheet --> b_master_style
  t_persona_sheet --> b_character_kafka
  t_persona_sheet --> b_persona_sheet_vlog
  t_persona_sheet --> b_persona_pack
  t_persona_sheet --> b_speech_mode_kafka
  t_persona_sheet --> b_text_style_jp
  t_persona_sheet --> b_negative_common
  t_archive_contact_sheet --> b_master_style
  t_archive_contact_sheet --> b_character_kafka
  t_archive_contact_sheet --> b_archive_contact_sheet_viz
  t_archive_contact_sheet --> b_archive_index_vlog
  t_archive_contact_sheet --> b_prompt_archive_sheet_vlog
  t_archive_contact_sheet --> b_negative_common
  t_archive_contact_sheet -.-> b_archive_contact_sheet_viz
  t_archive_contact_sheet -.-> b_archive_index_vlog
  t_archive_contact_sheet -.-> b_prompt_archive_sheet_vlog
  t_archive_index --> b_master_style
  t_archive_index --> b_character_kafka
  t_archive_index --> b_archive_index_vlog
  t_archive_index --> b_prompt_archive_sheet_vlog
  t_archive_index --> b_speech_mode_kafka
  t_archive_index --> b_negative_common
  t_photo_prompt_sheet --> b_master_style
  t_photo_prompt_sheet --> b_character_kafka
  t_photo_prompt_sheet --> b_photo_prompt_sheet_vlog
  t_photo_prompt_sheet --> b_prompt_archive_sheet_vlog
  t_photo_prompt_sheet --> b_negative_common
  t_memory_note_board --> b_master_style
  t_memory_note_board --> b_character_kafka
  t_memory_note_board --> b_memory_note_board_viz
  t_memory_note_board --> b_memory_pack
  t_memory_note_board --> b_research_log_pack
  t_memory_note_board --> b_negative_common
  t_memory_note_board -.-> b_memory_note_board_viz
  t_memory_note_board -.-> b_memory_pack
  t_memory_note_board -.-> b_research_log_pack
  t_memory_update_card --> b_master_style
  t_memory_update_card --> b_character_kafka
  t_memory_update_card --> b_memory_pack
  t_memory_update_card --> b_speech_mode_kafka
  t_memory_update_card --> b_research_log_pack
  t_memory_update_card --> b_negative_common
  t_summary_sheet --> b_master_style
  t_summary_sheet --> b_character_kafka
  t_summary_sheet --> b_summary_sheet_vlog
  t_summary_sheet --> b_speech_mode_kafka
  t_summary_sheet --> b_memory_pack
  t_summary_sheet --> b_research_log_pack
  t_summary_sheet --> b_negative_common
  t_poststream_review_board --> b_master_style
  t_poststream_review_board --> b_character_kafka
  t_poststream_review_board --> b_poststream_review_board_viz
  t_poststream_review_board --> b_research_log_pack
  t_poststream_review_board --> b_memory_pack
  t_poststream_review_board --> b_negative_common
  t_poststream_review_board -.-> b_poststream_review_board_viz
  t_poststream_review_board -.-> b_research_log_pack
  t_poststream_review_board -.-> b_memory_pack
  t_daily_work_sheet --> b_master_style
  t_daily_work_sheet --> b_character_kafka
  t_daily_work_sheet --> b_daily_work_sheet_vlog
  t_daily_work_sheet --> b_local_offline_pack
  t_daily_work_sheet --> b_speech_mode_kafka
  t_daily_work_sheet --> b_research_log_pack
  t_daily_work_sheet --> b_negative_common
```

## Blocks / layout
- Prompt Vault DB Graph | Blocks | category:形式・レイアウト

### Block Relations

```mermaid
flowchart LR
  classDef template fill:#dbeafe,stroke:#2563eb,color:#0f172a,stroke-width:1px;
  classDef block fill:#dcfce7,stroke:#059669,color:#0f172a,stroke-width:1px;
  subgraph blocks["Blocks"]
    direction TB
    subgraph cat_01["形式・レイアウト"]
      direction TB
      b_sticker_sheet_layout["4x4 ステッカーシート<br/><small>sticker_sheet_layout</small>"]:::block
      b_joinwars_layout["JoinWars用レイアウト<br/><small>joinwars_layout</small>"]:::block
      b_character_sheet_kafka["Kafka キャラデザインシート<br/><small>character_sheet_kafka</small>"]:::block
      b_morning_tweet_layout["おはツイレイアウト<br/><small>morning_tweet_layout</small>"]:::block
      b_archive_index_vlog["アーカイブ索引<br/><small>archive_index_vlog</small>"]:::block
      b_cardgame_post_layout["カードゲームレイアウト<br/><small>cardgame_post_layout</small>"]:::block
      b_cosplay_post_layout["コスプレレイアウト<br/><small>cosplay_post_layout</small>"]:::block
      b_persona_sheet_vlog["パーソナ設定シート<br/><small>persona_sheet_vlog</small>"]:::block
      b_poker_post_layout["ポーカーレイアウト<br/><small>poker_post_layout</small>"]:::block
      b_persona_poster_viz["人格ポスター<br/><small>persona_poster_viz</small>"]:::block
      b_daily_work_sheet_vlog["作業管理テンプレート<br/><small>daily_work_sheet_vlog</small>"]:::block
      b_archive_contact_sheet_viz["成果物一覧（コンタクトシート）<br/><small>archive_contact_sheet_viz</small>"]:::block
      b_summary_sheet_vlog["振り返りサマリー<br/><small>summary_sheet_vlog</small>"]:::block
      b_status_post_layout["日常ステータスレイアウト<br/><small>status_post_layout</small>"]:::block
      b_comic_layout["漫画レイアウト<br/><small>comic_layout</small>"]:::block
      b_prompt_archive_sheet_vlog["生成台帳<br/><small>prompt_archive_sheet_vlog</small>"]:::block
      b_photo_prompt_sheet_vlog["画像生成台帳（詳細）<br/><small>photo_prompt_sheet_vlog</small>"]:::block
      b_memory_note_board_viz["記憶メモ（記録用ボード）<br/><small>memory_note_board_viz</small>"]:::block
      b_topic_redirect_banner_viz["話題切り替え用バナー<br/><small>topic_redirect_banner_viz</small>"]:::block
      b_reading_post_layout["読書シーン用レイアウト<br/><small>reading_post_layout</small>"]:::block
      b_reply_stamp_sheet_viz["返信スタンプ（グリッド）<br/><small>reply_stamp_sheet_viz</small>"]:::block
      b_poststream_review_board_viz["配信振り返り（レビュー用）<br/><small>poststream_review_board_viz</small>"]:::block
      b_stream_start_banner_viz["配信開始バナー<br/><small>stream_start_banner_viz</small>"]:::block
    end
  end
  subgraph templates["Referenced Templates"]
    direction TB
      t_persona_sheet["Kafka 人格固定カード<br/><small>persona_sheet</small>"]:::template
      t_daily_work_sheet["Kafka 配信運用カード<br/><small>daily_work_sheet</small>"]:::template
  end
  b_morning_tweet_layout -.-> b_status_post_layout
  b_persona_sheet_vlog -.-> t_persona_sheet
  b_persona_poster_viz -.-> b_persona_sheet_vlog
  b_daily_work_sheet_vlog -.-> t_daily_work_sheet
  b_daily_work_sheet_vlog -.-> t_daily_work_sheet
  b_archive_contact_sheet_viz -.-> b_prompt_archive_sheet_vlog
  b_archive_contact_sheet_viz -.-> b_prompt_archive_sheet_vlog
  b_archive_contact_sheet_viz -.-> b_archive_index_vlog
  b_morning_tweet_layout -.-> b_status_post_layout
  b_archive_contact_sheet_viz -.-> b_memory_note_board_viz
```

## Focus / morning_tweet_layout
- Prompt Vault DB Graph | focus:morning_tweet_layout

### Template Composition

```mermaid
flowchart LR
  classDef template fill:#dbeafe,stroke:#2563eb,color:#0f172a,stroke-width:1px;
  classDef block fill:#dcfce7,stroke:#059669,color:#0f172a,stroke-width:1px;
  subgraph templates["Templates"]
    direction TB
    subgraph kind_01["social"]
      direction TB
      t_morning_tweet_coffee["Kafka おはツイ コーヒー<br/><small>morning_tweet_coffee</small>"]:::template
      t_morning_tweet_winter["Kafka おはツイ 冬<br/><small>morning_tweet_winter</small>"]:::template
      t_morning_tweet_commute["Kafka おはツイ 出発前<br/><small>morning_tweet_commute</small>"]:::template
      t_morning_tweet_summer["Kafka おはツイ 夏<br/><small>morning_tweet_summer</small>"]:::template
      t_morning_tweet_sleepy["Kafka おはツイ 寝起き<br/><small>morning_tweet_sleepy</small>"]:::template
      t_morning_tweet_spring["Kafka おはツイ 春<br/><small>morning_tweet_spring</small>"]:::template
      t_morning_tweet_autumn["Kafka おはツイ 秋<br/><small>morning_tweet_autumn</small>"]:::template
      t_morning_tweet_window["Kafka おはツイ 窓際<br/><small>morning_tweet_window</small>"]:::template
      t_morning_tweet_rain["Kafka おはツイ 雨の日<br/><small>morning_tweet_rain</small>"]:::template
      t_goodnight_post["Kafka おやすみポスト<br/><small>goodnight_post</small>"]:::template
      t_break_post["Kafka 休憩ポスト<br/><small>break_post</small>"]:::template
      t_work_start_post["Kafka 作業開始ポスト<br/><small>work_start_post</small>"]:::template
      t_progress_post["Kafka 進捗ポスト<br/><small>progress_post</small>"]:::template
    end
    subgraph kind_02["design_sheet"]
      direction TB
      t_morning_tweet_index["Kafka おはツイ一覧<br/><small>morning_tweet_index</small>"]:::template
    end
  end
  subgraph blocks["Blocks"]
    direction TB
    subgraph cat_01["形式・レイアウト"]
      direction TB
      b_morning_tweet_layout["おはツイレイアウト<br/><small>morning_tweet_layout</small>"]:::block
      b_status_post_layout["日常ステータスレイアウト<br/><small>status_post_layout</small>"]:::block
    end
  end
  t_morning_tweet_coffee --> b_morning_tweet_layout
  t_morning_tweet_winter --> b_morning_tweet_layout
  t_morning_tweet_commute --> b_morning_tweet_layout
  t_morning_tweet_summer --> b_morning_tweet_layout
  t_morning_tweet_sleepy --> b_morning_tweet_layout
  t_morning_tweet_spring --> b_morning_tweet_layout
  t_morning_tweet_autumn --> b_morning_tweet_layout
  t_morning_tweet_window --> b_morning_tweet_layout
  t_morning_tweet_rain --> b_morning_tweet_layout
  t_morning_tweet_index --> b_morning_tweet_layout
  t_goodnight_post --> b_status_post_layout
  t_break_post --> b_status_post_layout
  t_work_start_post --> b_status_post_layout
  t_progress_post --> b_status_post_layout
```

### Block Relations

```mermaid
flowchart LR
  classDef template fill:#dbeafe,stroke:#2563eb,color:#0f172a,stroke-width:1px;
  classDef block fill:#dcfce7,stroke:#059669,color:#0f172a,stroke-width:1px;
  subgraph blocks["Blocks"]
    direction TB
    subgraph cat_01["形式・レイアウト"]
      direction TB
      b_morning_tweet_layout["おはツイレイアウト<br/><small>morning_tweet_layout</small>"]:::block
      b_status_post_layout["日常ステータスレイアウト<br/><small>status_post_layout</small>"]:::block
    end
  end
  b_morning_tweet_layout -.-> b_status_post_layout
  b_morning_tweet_layout -.-> b_status_post_layout
```

## Node List

| Type | ID | Title | Kind / Category |
| --- | --- | --- | --- |
| block | `sticker_sheet_layout` | 4x4 ステッカーシート | 形式・レイアウト |
| block | `joinwars_status_text_pack` | JoinWars文言 | セリフ・フレーズ |
| block | `joinwars_layout` | JoinWars用レイアウト | 形式・レイアウト |
| block | `joinwars_scene_kafka` | JoinWars背景 | 背景 |
| block | `joinwars_style_kafka` | JoinWars衣装 | 衣装 |
| block | `character_kafka` | KAFKA | キャラクター |
| block | `character_sheet_kafka` | Kafka キャラデザインシート | 形式・レイアウト |
| block | `morning_tweet_layout` | おはツイレイアウト | 形式・レイアウト |
| block | `morning_tweet_text_pack` | おはツイ文言 | セリフ・フレーズ |
| block | `goodnight_scene_kafka` | おやすみ背景 | 背景 |
| block | `speech_mode_kafka` | かふからしい発話モード | 性格・トーン |
| block | `icon_mark_only_kafka` | アイコン単独 | ブランド |
| block | `avatar_mode_pack` | アバターモード | アバター |
| block | `archive_index_vlog` | アーカイブ索引 | 形式・レイアウト |
| block | `cardgame_post_layout` | カードゲームレイアウト | 形式・レイアウト |
| block | `card_game_status_text_pack` | カードゲーム文言 | セリフ・フレーズ |
| block | `character_customization_pack` | キャラ設定 | コンフィグ |
| block | `cosplay_post_layout` | コスプレレイアウト | 形式・レイアウト |
| block | `cosplay_scene_kafka` | コスプレ撮影背景 | 背景 |
| block | `cosplay_status_text_pack` | コスプレ文言 | セリフ・フレーズ |
| block | `cosplay_event_outfit_kafka` | コスプレ衣装 | 衣装 |
| block | `chat_reply_pack` | コメント返し | リプライ・対話 |
| block | `morning_pose_coffee_kafka` | コーヒーおはツイ姿勢 | ポーズ |
| block | `slide_pack` | スライド発表 | 発表 |
| block | `demo_mode_pack` | デモモード | 展示・サイン |
| block | `persona_sheet_vlog` | パーソナ設定シート | 形式・レイアウト |
| block | `fantasy_card_game_style_kafka` | ファンタジーカードゲーム衣装 | 衣装 |
| block | `fantasy_card_game_scene_kafka` | ファンタジーカード盤面 | 背景 |
| block | `frame_only_kafka` | フレーム単独 | ブランド |
| block | `poker_table_scene_kafka` | ポーカーテーブル背景 | 背景 |
| block | `poker_dealer_style_kafka` | ポーカーディーラー衣装 | 衣装 |
| block | `poker_status_text_pack` | ポーカーポスト文言 | セリフ・フレーズ |
| block | `poker_post_layout` | ポーカーレイアウト | 形式・レイアウト |
| block | `master_style` | マスタースタイル | 基準 |
| block | `moderation_pack` | モデレーション | 安全 |
| block | `logo_only_kafka` | ロゴ単独 | ブランド |
| block | `local_offline_pack` | ローカル優先 | システム・実行 |
| block | `persona_poster_viz` | 人格ポスター | 形式・レイアウト |
| block | `break_scene_kafka` | 休憩背景 | 背景 |
| block | `daily_work_sheet_vlog` | 作業管理テンプレート | 形式・レイアウト |
| block | `work_start_scene_kafka` | 作業開始背景 | 背景 |
| block | `negative_common` | 共通ネガティブ | ネガティブ |
| block | `source_research` | 再調査メモ | リサーチ |
| block | `morning_pose_winter_kafka` | 冬おはツイ姿勢 | ポーズ |
| block | `morning_background_winter_kafka` | 冬朝背景 | 背景 |
| block | `seasonal_outfit_winter_kafka` | 冬衣装 | 衣装 |
| block | `morning_pose_commute_kafka` | 出発前おはツイ姿勢 | ポーズ |
| block | `morning_scene_commute_kafka` | 出発前の朝背景 | 背景 |
| block | `expressions_pack` | 反応集 | 表情 |
| block | `announcement_text_pack` | 告知文言 | セリフ・フレーズ |
| block | `morning_pose_summer_kafka` | 夏おはツイ姿勢 | ポーズ |
| block | `morning_background_summer_kafka` | 夏朝背景 | 背景 |
| block | `seasonal_outfit_summer_kafka` | 夏衣装 | 衣装 |
| block | `plugin_pack` | 外部連携 | 拡張 |
| block | `subtitle_pack` | 字幕・テロップ | テキスト |
| block | `logo_orbit_kafka` | 宇宙ロゴ単独 | ブランド |
| block | `morning_pose_sleepy_kafka` | 寝起きおはツイ姿勢 | ポーズ |
| block | `morning_scene_sleepy_kafka` | 寝起きの朝背景 | 背景 |
| block | `vfx_trigger_pack` | 感情演出 | 演出 |
| block | `archive_contact_sheet_viz` | 成果物一覧（コンタクトシート） | 形式・レイアウト |
| block | `summary_sheet_vlog` | 振り返りサマリー | 形式・レイアウト |
| block | `research_log_pack` | 振り返りログ | 記録・ログ |
| block | `control_panel_pack` | 操作パネル | 制御 |
| block | `wordmark_only_kafka` | 文字ロゴ単独 | ブランド |
| block | `status_post_layout` | 日常ステータスレイアウト | 形式・レイアウト |
| block | `daily_status_text_pack` | 日常ステータス文言 | セリフ・フレーズ |
| block | `text_style_jp` | 日本語文字 | テキスト |
| block | `morning_pose_spring_kafka` | 春おはツイ姿勢 | ポーズ |
| block | `morning_background_spring_kafka` | 春朝背景 | 背景 |
| block | `seasonal_outfit_spring_kafka` | 春衣装 | 衣装 |
| block | `morning_scene_coffee_kafka` | 朝コーヒー背景 | 背景 |
| block | `morning_situation_text_pack` | 朝シチュエーション文言 | セリフ・フレーズ |
| block | `reading_scene_seaside_kafka` | 海辺の読書背景 | 背景 |
| block | `comic_layout` | 漫画レイアウト | 形式・レイアウト |
| block | `prompt_archive_sheet_vlog` | 生成台帳 | 形式・レイアウト |
| block | `photo_prompt_sheet_vlog` | 画像生成台帳（詳細） | 形式・レイアウト |
| block | `text_content_pack` | 短い日本語セリフ | セリフ・フレーズ |
| block | `morning_pose_autumn_kafka` | 秋おはツイ姿勢 | ポーズ |
| block | `morning_background_autumn_kafka` | 秋朝背景 | 背景 |
| block | `seasonal_outfit_autumn_kafka` | 秋衣装 | 衣装 |
| block | `morning_pose_window_kafka` | 窓際おはツイ姿勢 | ポーズ |
| block | `morning_scene_window_kafka` | 窓際の朝背景 | 背景 |
| block | `persona_pack` | 自律人格 | 人格 |
| block | `outfit_kafka` | 衣装 | キャラ衣装 |
| block | `reaction_focus` | 表情強調 | 表情 |
| block | `effects_pack` | 装飾効果 | 演出 |
| block | `memory_note_board_viz` | 記憶メモ（記録用ボード） | 形式・レイアウト |
| block | `memory_pack` | 記憶管理 | 記憶 |
| block | `safe_reply_pack` | 話題切り替え | リプライ・対話 |
| block | `topic_redirect_banner_viz` | 話題切り替え用バナー | 形式・レイアウト |
| block | `reading_post_layout` | 読書シーン用レイアウト | 形式・レイアウト |
| block | `reading_pose_kafka` | 読書ポーズ | ポーズ |
| block | `reading_status_text_pack` | 読書文言 | セリフ・フレーズ |
| block | `reading_scene_general_kafka` | 読書背景 | 背景 |
| block | `reading_outfit_kafka` | 読書衣装 | 衣装 |
| block | `reading_scene_anne_kafka` | 赤毛のアン読書背景 | 背景 |
| block | `reply_stamp_sheet_viz` | 返信スタンプ（グリッド） | 形式・レイアウト |
| block | `progress_scene_kafka` | 進捗背景 | 背景 |
| block | `chat_platform_pack` | 配信チャット | 配信 |
| block | `poststream_review_board_viz` | 配信振り返り（レビュー用） | 形式・レイアウト |
| block | `stream_start_banner_viz` | 配信開始バナー | 形式・レイアウト |
| block | `morning_pose_rain_kafka` | 雨の日おはツイ姿勢 | ポーズ |
| block | `morning_scene_rain_kafka` | 雨の日の朝背景 | 背景 |
| block | `voice_pipeline_pack` | 音声パイプライン | 音声 |
| template | `joinwars_post` | Kafka JoinWars投稿 | social |
| template | `twitter_comic` | Kafka Twitter再調査漫画 | comic |
| template | `morning_tweet_coffee` | Kafka おはツイ コーヒー | social |
| template | `morning_tweet_winter` | Kafka おはツイ 冬 | social |
| template | `morning_tweet_commute` | Kafka おはツイ 出発前 | social |
| template | `morning_tweet_summer` | Kafka おはツイ 夏 | social |
| template | `morning_tweet_sleepy` | Kafka おはツイ 寝起き | social |
| template | `morning_tweet_spring` | Kafka おはツイ 春 | social |
| template | `morning_tweet_autumn` | Kafka おはツイ 秋 | social |
| template | `morning_tweet_window` | Kafka おはツイ 窓際 | social |
| template | `morning_tweet_rain` | Kafka おはツイ 雨の日 | social |
| template | `morning_tweet_index` | Kafka おはツイ一覧 | design_sheet |
| template | `goodnight_post` | Kafka おやすみポスト | social |
| template | `icon_mark_sheet` | Kafka アイコンデザイン | brand |
| template | `cardgame_post` | Kafka カードゲーム投稿 | social |
| template | `character_design_sheet` | Kafka キャラデザインシート | design_sheet |
| template | `cosplay_post` | Kafka コスプレ投稿 | social |
| template | `comment_reply_guide` | Kafka コメント返しガイド | system |
| template | `chat_reply_card` | Kafka コメント返信カード | reaction |
| template | `slide_talk` | Kafka スライド発表 | system |
| template | `frame_sheet` | Kafka フレームデザイン | brand |
| template | `poker_post` | Kafka ポーカー投稿 | social |
| template | `logo_only_sheet` | Kafka ロゴデザイン | brand |
| template | `wordmark_sheet` | Kafka ワードマークデザイン | brand |
| template | `persona_poster` | Kafka 人格ポスター | design_sheet |
| template | `persona_sheet` | Kafka 人格固定カード | design_sheet |
| template | `break_post` | Kafka 休憩ポスト | social |
| template | `work_start_post` | Kafka 作業開始ポスト | social |
| template | `reaction_image` | Kafka 反応画像 | reaction |
| template | `orbit_logo_sheet` | Kafka 宇宙ロゴデザイン | brand |
| template | `archive_contact_sheet` | Kafka 成果物一覧 | design_sheet |
| template | `archive_index` | Kafka 成果物回収カード | design_sheet |
| template | `stamp_sheet` | Kafka 新しいスタンプ | stamp |
| template | `reading_post_seaside` | Kafka 海辺の読書投稿 | social |
| template | `photo_prompt_sheet` | Kafka 生成素材台帳 | design_sheet |
| template | `memory_note_board` | Kafka 記憶メモボード | design_sheet |
| template | `memory_update_card` | Kafka 記憶更新カード | design_sheet |
| template | `topic_redirect_card` | Kafka 話題切り替えカード | reaction |
| template | `topic_redirect_banner` | Kafka 話題切り替えバナー | announcement |
| template | `reading_post_general` | Kafka 読書投稿 | social |
| template | `reading_post_anne` | Kafka 赤毛のアン読書投稿 | social |
| template | `ai_tuber_core_pack` | Kafka 起動カード | system |
| template | `reply_stamp_sheet` | Kafka 返信スタンプ（一覧） | stamp |
| template | `progress_post` | Kafka 進捗ポスト | social |
| template | `announcement_thumbnail` | Kafka 配信告知サムネイル | announcement |
| template | `summary_sheet` | Kafka 配信後まとめカード | design_sheet |
| template | `ai_tuber_ops_pack` | Kafka 配信後レビューカード | system |
| template | `poststream_review_board` | Kafka 配信後レビュー盤 | design_sheet |
| template | `daily_work_sheet` | Kafka 配信運用カード | design_sheet |
| template | `stream_start_banner` | Kafka 配信開始バナー | announcement |

## Relation List

| From | Relation | To |
| --- | --- | --- |
| `joinwars_post` | blocks | `master_style` |
| `joinwars_post` | blocks | `character_kafka` |
| `joinwars_post` | blocks | `joinwars_layout` |
| `joinwars_post` | blocks | `joinwars_scene_kafka` |
| `joinwars_post` | blocks | `joinwars_style_kafka` |
| `joinwars_post` | blocks | `joinwars_status_text_pack` |
| `joinwars_post` | blocks | `text_style_jp` |
| `joinwars_post` | blocks | `negative_common` |
| `twitter_comic` | blocks | `source_research` |
| `twitter_comic` | blocks | `master_style` |
| `twitter_comic` | blocks | `character_kafka` |
| `twitter_comic` | blocks | `comic_layout` |
| `twitter_comic` | blocks | `reaction_focus` |
| `twitter_comic` | blocks | `text_style_jp` |
| `twitter_comic` | blocks | `text_content_pack` |
| `twitter_comic` | blocks | `effects_pack` |
| `twitter_comic` | blocks | `negative_common` |
| `morning_tweet_coffee` | blocks | `master_style` |
| `morning_tweet_coffee` | blocks | `character_kafka` |
| `morning_tweet_coffee` | blocks | `outfit_kafka` |
| `morning_tweet_coffee` | blocks | `morning_pose_coffee_kafka` |
| `morning_tweet_coffee` | blocks | `morning_scene_coffee_kafka` |
| `morning_tweet_coffee` | blocks | `morning_tweet_layout` |
| `morning_tweet_coffee` | blocks | `morning_situation_text_pack` |
| `morning_tweet_coffee` | blocks | `text_style_jp` |
| `morning_tweet_coffee` | blocks | `negative_common` |
| `morning_tweet_winter` | blocks | `master_style` |
| `morning_tweet_winter` | blocks | `character_kafka` |
| `morning_tweet_winter` | blocks | `seasonal_outfit_winter_kafka` |
| `morning_tweet_winter` | blocks | `morning_pose_winter_kafka` |
| `morning_tweet_winter` | blocks | `morning_background_winter_kafka` |
| `morning_tweet_winter` | blocks | `morning_tweet_layout` |
| `morning_tweet_winter` | blocks | `morning_tweet_text_pack` |
| `morning_tweet_winter` | blocks | `text_style_jp` |
| `morning_tweet_winter` | blocks | `effects_pack` |
| `morning_tweet_winter` | blocks | `negative_common` |
| `morning_tweet_commute` | blocks | `master_style` |
| `morning_tweet_commute` | blocks | `character_kafka` |
| `morning_tweet_commute` | blocks | `outfit_kafka` |
| `morning_tweet_commute` | blocks | `morning_pose_commute_kafka` |
| `morning_tweet_commute` | blocks | `morning_scene_commute_kafka` |
| `morning_tweet_commute` | blocks | `morning_tweet_layout` |
| `morning_tweet_commute` | blocks | `morning_situation_text_pack` |
| `morning_tweet_commute` | blocks | `text_style_jp` |
| `morning_tweet_commute` | blocks | `negative_common` |
| `morning_tweet_summer` | blocks | `master_style` |
| `morning_tweet_summer` | blocks | `character_kafka` |
| `morning_tweet_summer` | blocks | `seasonal_outfit_summer_kafka` |
| `morning_tweet_summer` | blocks | `morning_pose_summer_kafka` |
| `morning_tweet_summer` | blocks | `morning_background_summer_kafka` |
| `morning_tweet_summer` | blocks | `morning_tweet_layout` |
| `morning_tweet_summer` | blocks | `morning_tweet_text_pack` |
| `morning_tweet_summer` | blocks | `text_style_jp` |
| `morning_tweet_summer` | blocks | `effects_pack` |
| `morning_tweet_summer` | blocks | `negative_common` |
| `morning_tweet_sleepy` | blocks | `master_style` |
| `morning_tweet_sleepy` | blocks | `character_kafka` |
| `morning_tweet_sleepy` | blocks | `outfit_kafka` |
| `morning_tweet_sleepy` | blocks | `morning_pose_sleepy_kafka` |
| `morning_tweet_sleepy` | blocks | `morning_scene_sleepy_kafka` |
| `morning_tweet_sleepy` | blocks | `morning_tweet_layout` |
| `morning_tweet_sleepy` | blocks | `morning_situation_text_pack` |
| `morning_tweet_sleepy` | blocks | `text_style_jp` |
| `morning_tweet_sleepy` | blocks | `negative_common` |
| `morning_tweet_spring` | blocks | `master_style` |
| `morning_tweet_spring` | blocks | `character_kafka` |
| `morning_tweet_spring` | blocks | `seasonal_outfit_spring_kafka` |
| `morning_tweet_spring` | blocks | `morning_pose_spring_kafka` |
| `morning_tweet_spring` | blocks | `morning_background_spring_kafka` |
| `morning_tweet_spring` | blocks | `morning_tweet_layout` |
| `morning_tweet_spring` | blocks | `morning_tweet_text_pack` |
| `morning_tweet_spring` | blocks | `text_style_jp` |
| `morning_tweet_spring` | blocks | `effects_pack` |
| `morning_tweet_spring` | blocks | `negative_common` |
| `morning_tweet_autumn` | blocks | `master_style` |
| `morning_tweet_autumn` | blocks | `character_kafka` |
| `morning_tweet_autumn` | blocks | `seasonal_outfit_autumn_kafka` |
| `morning_tweet_autumn` | blocks | `morning_pose_autumn_kafka` |
| `morning_tweet_autumn` | blocks | `morning_background_autumn_kafka` |
| `morning_tweet_autumn` | blocks | `morning_tweet_layout` |
| `morning_tweet_autumn` | blocks | `morning_tweet_text_pack` |
| `morning_tweet_autumn` | blocks | `text_style_jp` |
| `morning_tweet_autumn` | blocks | `effects_pack` |
| `morning_tweet_autumn` | blocks | `negative_common` |
| `morning_tweet_window` | blocks | `master_style` |
| `morning_tweet_window` | blocks | `character_kafka` |
| `morning_tweet_window` | blocks | `outfit_kafka` |
| `morning_tweet_window` | blocks | `morning_pose_window_kafka` |
| `morning_tweet_window` | blocks | `morning_scene_window_kafka` |
| `morning_tweet_window` | blocks | `morning_tweet_layout` |
| `morning_tweet_window` | blocks | `morning_situation_text_pack` |
| `morning_tweet_window` | blocks | `text_style_jp` |
| `morning_tweet_window` | blocks | `negative_common` |
| `morning_tweet_rain` | blocks | `master_style` |
| `morning_tweet_rain` | blocks | `character_kafka` |
| `morning_tweet_rain` | blocks | `outfit_kafka` |
| `morning_tweet_rain` | blocks | `morning_pose_rain_kafka` |
| `morning_tweet_rain` | blocks | `morning_scene_rain_kafka` |
| `morning_tweet_rain` | blocks | `morning_tweet_layout` |
| `morning_tweet_rain` | blocks | `morning_situation_text_pack` |
| `morning_tweet_rain` | blocks | `text_style_jp` |
| `morning_tweet_rain` | blocks | `negative_common` |
| `morning_tweet_index` | blocks | `master_style` |
| `morning_tweet_index` | blocks | `character_kafka` |
| `morning_tweet_index` | blocks | `morning_tweet_layout` |
| `morning_tweet_index` | blocks | `morning_tweet_text_pack` |
| `morning_tweet_index` | blocks | `morning_situation_text_pack` |
| `morning_tweet_index` | blocks | `text_style_jp` |
| `morning_tweet_index` | blocks | `negative_common` |
| `goodnight_post` | blocks | `master_style` |
| `goodnight_post` | blocks | `character_kafka` |
| `goodnight_post` | blocks | `outfit_kafka` |
| `goodnight_post` | blocks | `goodnight_scene_kafka` |
| `goodnight_post` | blocks | `status_post_layout` |
| `goodnight_post` | blocks | `daily_status_text_pack` |
| `goodnight_post` | blocks | `text_style_jp` |
| `goodnight_post` | blocks | `negative_common` |
| `icon_mark_sheet` | blocks | `master_style` |
| `icon_mark_sheet` | blocks | `icon_mark_only_kafka` |
| `icon_mark_sheet` | blocks | `negative_common` |
| `cardgame_post` | blocks | `master_style` |
| `cardgame_post` | blocks | `character_kafka` |
| `cardgame_post` | blocks | `cardgame_post_layout` |
| `cardgame_post` | blocks | `fantasy_card_game_scene_kafka` |
| `cardgame_post` | blocks | `fantasy_card_game_style_kafka` |
| `cardgame_post` | blocks | `card_game_status_text_pack` |
| `cardgame_post` | blocks | `text_style_jp` |
| `cardgame_post` | blocks | `negative_common` |
| `character_design_sheet` | blocks | `character_sheet_kafka` |
| `cosplay_post` | blocks | `master_style` |
| `cosplay_post` | blocks | `character_kafka` |
| `cosplay_post` | blocks | `cosplay_post_layout` |
| `cosplay_post` | blocks | `cosplay_scene_kafka` |
| `cosplay_post` | blocks | `cosplay_event_outfit_kafka` |
| `cosplay_post` | blocks | `cosplay_status_text_pack` |
| `cosplay_post` | blocks | `text_style_jp` |
| `cosplay_post` | blocks | `negative_common` |
| `comment_reply_guide` | blocks | `master_style` |
| `comment_reply_guide` | blocks | `character_kafka` |
| `comment_reply_guide` | blocks | `chat_reply_pack` |
| `comment_reply_guide` | blocks | `speech_mode_kafka` |
| `comment_reply_guide` | blocks | `safe_reply_pack` |
| `comment_reply_guide` | blocks | `text_style_jp` |
| `comment_reply_guide` | blocks | `expressions_pack` |
| `comment_reply_guide` | blocks | `negative_common` |
| `chat_reply_card` | blocks | `master_style` |
| `chat_reply_card` | blocks | `character_kafka` |
| `chat_reply_card` | blocks | `chat_reply_pack` |
| `chat_reply_card` | blocks | `speech_mode_kafka` |
| `chat_reply_card` | blocks | `text_style_jp` |
| `chat_reply_card` | blocks | `text_content_pack` |
| `chat_reply_card` | blocks | `expressions_pack` |
| `chat_reply_card` | blocks | `negative_common` |
| `chat_reply_card` | uses | `chat_reply_pack` |
| `chat_reply_card` | uses | `speech_mode_kafka` |
| `chat_reply_card` | uses | `text_style_jp` |
| `chat_reply_card` | uses | `expressions_pack` |
| `slide_talk` | blocks | `master_style` |
| `slide_talk` | blocks | `character_kafka` |
| `slide_talk` | blocks | `slide_pack` |
| `slide_talk` | blocks | `text_style_jp` |
| `slide_talk` | blocks | `negative_common` |
| `frame_sheet` | blocks | `master_style` |
| `frame_sheet` | blocks | `frame_only_kafka` |
| `frame_sheet` | blocks | `negative_common` |
| `poker_post` | blocks | `master_style` |
| `poker_post` | blocks | `character_kafka` |
| `poker_post` | blocks | `poker_post_layout` |
| `poker_post` | blocks | `poker_table_scene_kafka` |
| `poker_post` | blocks | `poker_dealer_style_kafka` |
| `poker_post` | blocks | `poker_status_text_pack` |
| `poker_post` | blocks | `text_style_jp` |
| `poker_post` | blocks | `negative_common` |
| `logo_only_sheet` | blocks | `master_style` |
| `logo_only_sheet` | blocks | `logo_only_kafka` |
| `logo_only_sheet` | blocks | `wordmark_only_kafka` |
| `logo_only_sheet` | blocks | `icon_mark_only_kafka` |
| `logo_only_sheet` | blocks | `negative_common` |
| `wordmark_sheet` | blocks | `master_style` |
| `wordmark_sheet` | blocks | `wordmark_only_kafka` |
| `wordmark_sheet` | blocks | `text_style_jp` |
| `wordmark_sheet` | blocks | `negative_common` |
| `persona_poster` | blocks | `master_style` |
| `persona_poster` | blocks | `character_kafka` |
| `persona_poster` | blocks | `outfit_kafka` |
| `persona_poster` | blocks | `persona_poster_viz` |
| `persona_poster` | blocks | `persona_pack` |
| `persona_poster` | blocks | `text_style_jp` |
| `persona_poster` | blocks | `negative_common` |
| `persona_poster` | uses | `persona_poster_viz` |
| `persona_poster` | uses | `persona_pack` |
| `persona_poster` | uses | `text_style_jp` |
| `persona_sheet` | blocks | `master_style` |
| `persona_sheet` | blocks | `character_kafka` |
| `persona_sheet` | blocks | `persona_sheet_vlog` |
| `persona_sheet` | blocks | `persona_pack` |
| `persona_sheet` | blocks | `speech_mode_kafka` |
| `persona_sheet` | blocks | `text_style_jp` |
| `persona_sheet` | blocks | `negative_common` |
| `break_post` | blocks | `master_style` |
| `break_post` | blocks | `character_kafka` |
| `break_post` | blocks | `outfit_kafka` |
| `break_post` | blocks | `break_scene_kafka` |
| `break_post` | blocks | `status_post_layout` |
| `break_post` | blocks | `daily_status_text_pack` |
| `break_post` | blocks | `text_style_jp` |
| `break_post` | blocks | `negative_common` |
| `work_start_post` | blocks | `master_style` |
| `work_start_post` | blocks | `character_kafka` |
| `work_start_post` | blocks | `outfit_kafka` |
| `work_start_post` | blocks | `work_start_scene_kafka` |
| `work_start_post` | blocks | `status_post_layout` |
| `work_start_post` | blocks | `daily_status_text_pack` |
| `work_start_post` | blocks | `text_style_jp` |
| `work_start_post` | blocks | `negative_common` |
| `reaction_image` | blocks | `master_style` |
| `reaction_image` | blocks | `character_kafka` |
| `reaction_image` | blocks | `outfit_kafka` |
| `reaction_image` | blocks | `reaction_focus` |
| `reaction_image` | blocks | `text_style_jp` |
| `reaction_image` | blocks | `text_content_pack` |
| `reaction_image` | blocks | `effects_pack` |
| `reaction_image` | blocks | `negative_common` |
| `reaction_image` | uses | `reaction_focus` |
| `reaction_image` | uses | `text_style_jp` |
| `reaction_image` | uses | `text_content_pack` |
| `reaction_image` | uses | `effects_pack` |
| `orbit_logo_sheet` | blocks | `master_style` |
| `orbit_logo_sheet` | blocks | `logo_orbit_kafka` |
| `orbit_logo_sheet` | blocks | `wordmark_only_kafka` |
| `orbit_logo_sheet` | blocks | `icon_mark_only_kafka` |
| `orbit_logo_sheet` | blocks | `negative_common` |
| `archive_contact_sheet` | blocks | `master_style` |
| `archive_contact_sheet` | blocks | `character_kafka` |
| `archive_contact_sheet` | blocks | `archive_contact_sheet_viz` |
| `archive_contact_sheet` | blocks | `archive_index_vlog` |
| `archive_contact_sheet` | blocks | `prompt_archive_sheet_vlog` |
| `archive_contact_sheet` | blocks | `negative_common` |
| `archive_contact_sheet` | uses | `archive_contact_sheet_viz` |
| `archive_contact_sheet` | uses | `archive_index_vlog` |
| `archive_contact_sheet` | uses | `prompt_archive_sheet_vlog` |
| `archive_index` | blocks | `master_style` |
| `archive_index` | blocks | `character_kafka` |
| `archive_index` | blocks | `archive_index_vlog` |
| `archive_index` | blocks | `prompt_archive_sheet_vlog` |
| `archive_index` | blocks | `speech_mode_kafka` |
| `archive_index` | blocks | `negative_common` |
| `stamp_sheet` | blocks | `master_style` |
| `stamp_sheet` | blocks | `character_kafka` |
| `stamp_sheet` | blocks | `outfit_kafka` |
| `stamp_sheet` | blocks | `sticker_sheet_layout` |
| `stamp_sheet` | blocks | `expressions_pack` |
| `stamp_sheet` | blocks | `text_style_jp` |
| `stamp_sheet` | blocks | `text_content_pack` |
| `stamp_sheet` | blocks | `effects_pack` |
| `stamp_sheet` | blocks | `negative_common` |
| `reading_post_seaside` | blocks | `master_style` |
| `reading_post_seaside` | blocks | `character_kafka` |
| `reading_post_seaside` | blocks | `reading_post_layout` |
| `reading_post_seaside` | blocks | `reading_scene_seaside_kafka` |
| `reading_post_seaside` | blocks | `reading_pose_kafka` |
| `reading_post_seaside` | blocks | `reading_outfit_kafka` |
| `reading_post_seaside` | blocks | `reading_status_text_pack` |
| `reading_post_seaside` | blocks | `text_style_jp` |
| `reading_post_seaside` | blocks | `negative_common` |
| `photo_prompt_sheet` | blocks | `master_style` |
| `photo_prompt_sheet` | blocks | `character_kafka` |
| `photo_prompt_sheet` | blocks | `photo_prompt_sheet_vlog` |
| `photo_prompt_sheet` | blocks | `prompt_archive_sheet_vlog` |
| `photo_prompt_sheet` | blocks | `negative_common` |
| `memory_note_board` | blocks | `master_style` |
| `memory_note_board` | blocks | `character_kafka` |
| `memory_note_board` | blocks | `memory_note_board_viz` |
| `memory_note_board` | blocks | `memory_pack` |
| `memory_note_board` | blocks | `research_log_pack` |
| `memory_note_board` | blocks | `negative_common` |
| `memory_note_board` | uses | `memory_note_board_viz` |
| `memory_note_board` | uses | `memory_pack` |
| `memory_note_board` | uses | `research_log_pack` |
| `memory_update_card` | blocks | `master_style` |
| `memory_update_card` | blocks | `character_kafka` |
| `memory_update_card` | blocks | `memory_pack` |
| `memory_update_card` | blocks | `speech_mode_kafka` |
| `memory_update_card` | blocks | `research_log_pack` |
| `memory_update_card` | blocks | `negative_common` |
| `topic_redirect_card` | blocks | `master_style` |
| `topic_redirect_card` | blocks | `character_kafka` |
| `topic_redirect_card` | blocks | `safe_reply_pack` |
| `topic_redirect_card` | blocks | `speech_mode_kafka` |
| `topic_redirect_card` | blocks | `text_style_jp` |
| `topic_redirect_card` | blocks | `negative_common` |
| `topic_redirect_banner` | blocks | `master_style` |
| `topic_redirect_banner` | blocks | `character_kafka` |
| `topic_redirect_banner` | blocks | `topic_redirect_banner_viz` |
| `topic_redirect_banner` | blocks | `safe_reply_pack` |
| `topic_redirect_banner` | blocks | `text_style_jp` |
| `topic_redirect_banner` | blocks | `negative_common` |
| `reading_post_general` | blocks | `master_style` |
| `reading_post_general` | blocks | `character_kafka` |
| `reading_post_general` | blocks | `reading_post_layout` |
| `reading_post_general` | blocks | `reading_scene_general_kafka` |
| `reading_post_general` | blocks | `reading_pose_kafka` |
| `reading_post_general` | blocks | `reading_outfit_kafka` |
| `reading_post_general` | blocks | `reading_status_text_pack` |
| `reading_post_general` | blocks | `text_style_jp` |
| `reading_post_general` | blocks | `negative_common` |
| `reading_post_anne` | blocks | `master_style` |
| `reading_post_anne` | blocks | `character_kafka` |
| `reading_post_anne` | blocks | `reading_post_layout` |
| `reading_post_anne` | blocks | `reading_scene_anne_kafka` |
| `reading_post_anne` | blocks | `reading_pose_kafka` |
| `reading_post_anne` | blocks | `reading_outfit_kafka` |
| `reading_post_anne` | blocks | `reading_status_text_pack` |
| `reading_post_anne` | blocks | `text_style_jp` |
| `reading_post_anne` | blocks | `negative_common` |
| `ai_tuber_core_pack` | blocks | `master_style` |
| `ai_tuber_core_pack` | blocks | `character_kafka` |
| `ai_tuber_core_pack` | blocks | `persona_pack` |
| `ai_tuber_core_pack` | blocks | `speech_mode_kafka` |
| `ai_tuber_core_pack` | blocks | `local_offline_pack` |
| `ai_tuber_core_pack` | blocks | `voice_pipeline_pack` |
| `ai_tuber_core_pack` | blocks | `chat_platform_pack` |
| `ai_tuber_core_pack` | blocks | `avatar_mode_pack` |
| `ai_tuber_core_pack` | blocks | `control_panel_pack` |
| `ai_tuber_core_pack` | blocks | `demo_mode_pack` |
| `ai_tuber_core_pack` | blocks | `moderation_pack` |
| `ai_tuber_core_pack` | blocks | `plugin_pack` |
| `reply_stamp_sheet` | blocks | `master_style` |
| `reply_stamp_sheet` | blocks | `character_kafka` |
| `reply_stamp_sheet` | blocks | `outfit_kafka` |
| `reply_stamp_sheet` | blocks | `reply_stamp_sheet_viz` |
| `reply_stamp_sheet` | blocks | `chat_reply_pack` |
| `reply_stamp_sheet` | blocks | `expressions_pack` |
| `reply_stamp_sheet` | blocks | `text_style_jp` |
| `reply_stamp_sheet` | blocks | `negative_common` |
| `progress_post` | blocks | `master_style` |
| `progress_post` | blocks | `character_kafka` |
| `progress_post` | blocks | `outfit_kafka` |
| `progress_post` | blocks | `progress_scene_kafka` |
| `progress_post` | blocks | `status_post_layout` |
| `progress_post` | blocks | `daily_status_text_pack` |
| `progress_post` | blocks | `text_style_jp` |
| `progress_post` | blocks | `negative_common` |
| `announcement_thumbnail` | blocks | `master_style` |
| `announcement_thumbnail` | blocks | `character_kafka` |
| `announcement_thumbnail` | blocks | `reaction_focus` |
| `announcement_thumbnail` | blocks | `announcement_text_pack` |
| `announcement_thumbnail` | blocks | `text_style_jp` |
| `announcement_thumbnail` | blocks | `effects_pack` |
| `announcement_thumbnail` | blocks | `negative_common` |
| `summary_sheet` | blocks | `master_style` |
| `summary_sheet` | blocks | `character_kafka` |
| `summary_sheet` | blocks | `summary_sheet_vlog` |
| `summary_sheet` | blocks | `speech_mode_kafka` |
| `summary_sheet` | blocks | `memory_pack` |
| `summary_sheet` | blocks | `research_log_pack` |
| `summary_sheet` | blocks | `negative_common` |
| `ai_tuber_ops_pack` | blocks | `master_style` |
| `ai_tuber_ops_pack` | blocks | `character_kafka` |
| `ai_tuber_ops_pack` | blocks | `chat_reply_pack` |
| `ai_tuber_ops_pack` | blocks | `safe_reply_pack` |
| `ai_tuber_ops_pack` | blocks | `speech_mode_kafka` |
| `ai_tuber_ops_pack` | blocks | `memory_pack` |
| `ai_tuber_ops_pack` | blocks | `vfx_trigger_pack` |
| `ai_tuber_ops_pack` | blocks | `subtitle_pack` |
| `ai_tuber_ops_pack` | blocks | `announcement_text_pack` |
| `ai_tuber_ops_pack` | blocks | `character_customization_pack` |
| `ai_tuber_ops_pack` | blocks | `research_log_pack` |
| `poststream_review_board` | blocks | `master_style` |
| `poststream_review_board` | blocks | `character_kafka` |
| `poststream_review_board` | blocks | `poststream_review_board_viz` |
| `poststream_review_board` | blocks | `research_log_pack` |
| `poststream_review_board` | blocks | `memory_pack` |
| `poststream_review_board` | blocks | `negative_common` |
| `poststream_review_board` | uses | `poststream_review_board_viz` |
| `poststream_review_board` | uses | `research_log_pack` |
| `poststream_review_board` | uses | `memory_pack` |
| `daily_work_sheet` | blocks | `master_style` |
| `daily_work_sheet` | blocks | `character_kafka` |
| `daily_work_sheet` | blocks | `daily_work_sheet_vlog` |
| `daily_work_sheet` | blocks | `local_offline_pack` |
| `daily_work_sheet` | blocks | `speech_mode_kafka` |
| `daily_work_sheet` | blocks | `research_log_pack` |
| `daily_work_sheet` | blocks | `negative_common` |
| `stream_start_banner` | blocks | `master_style` |
| `stream_start_banner` | blocks | `character_kafka` |
| `stream_start_banner` | blocks | `reaction_focus` |
| `stream_start_banner` | blocks | `stream_start_banner_viz` |
| `stream_start_banner` | blocks | `announcement_text_pack` |
| `stream_start_banner` | blocks | `text_style_jp` |
| `stream_start_banner` | blocks | `effects_pack` |
| `stream_start_banner` | blocks | `negative_common` |
| `morning_tweet_layout` | variant_of | `status_post_layout` |
| `chat_reply_pack` | related | `safe_reply_pack` |
| `chat_reply_pack` | related | `speech_mode_kafka` |
| `slide_pack` | related | `ai_tuber_ops_pack` |
| `slide_pack` | related | `comment_reply_guide` |
| `slide_pack` | related | `slide_talk` |
| `persona_sheet_vlog` | related | `persona_sheet` |
| `persona_sheet_vlog` | related | `persona_poster_viz` |
| `persona_sheet_vlog` | related | `persona_pack` |
| `persona_poster_viz` | related | `persona_pack` |
| `persona_poster_viz` | related | `speech_mode_kafka` |
| `daily_work_sheet_vlog` | related | `daily_work_sheet` |
| `daily_work_sheet_vlog` | related | `research_log_pack` |
| `daily_work_sheet_vlog` | related | `memory_pack` |
| `daily_work_sheet_vlog` | variant_of | `daily_work_sheet` |
| `expressions_pack` | related | `reaction_focus` |
| `archive_contact_sheet_viz` | related | `prompt_archive_sheet_vlog` |
| `archive_contact_sheet_viz` | related | `archive_index_vlog` |
| `archive_contact_sheet_viz` | variant_of | `prompt_archive_sheet_vlog` |
| `status_post_layout` | related | `morning_tweet_layout` |
| `persona_pack` | related | `persona_poster_viz` |
| `persona_pack` | related | `speech_mode_kafka` |
| `reaction_focus` | related | `expressions_pack` |
| `reaction_focus` | related | `text_content_pack` |
| `reaction_focus` | variant_of | `expressions_pack` |
| `memory_note_board_viz` | related | `memory_pack` |
| `memory_note_board_viz` | related | `archive_contact_sheet_viz` |
| `memory_note_board_viz` | variant_of | `memory_pack` |
| `topic_redirect_banner_viz` | related | `chat_reply_pack` |
| `topic_redirect_banner_viz` | related | `safe_reply_pack` |
| `reply_stamp_sheet_viz` | related | `reaction_focus` |
| `reply_stamp_sheet_viz` | related | `text_style_jp` |
| `reply_stamp_sheet_viz` | variant_of | `reaction_focus` |
| `poststream_review_board_viz` | related | `research_log_pack` |
| `poststream_review_board_viz` | related | `memory_pack` |
