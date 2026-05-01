# 001 AI Tuber Packs

## 目的

`vlog/data` を参考に、AI-Tuber 系で新しく創造するための部品と型を整理する。

## 参考にした構造

- 日付ベースで並ぶ
- 同じ内容でも用途別に分かれる
- 完成物をそのまま使える形にする
- `discord_ready` のように出力先を明示する

## ここから創造したいもの

- Persona を1枚で固定する資料
- Work を日次で回す運用資料
- Summary を読むだけで再利用できる要約資料
- Photo prompt を日付で積む生成台帳
- ChatGPT 画像を用途別に整理する出力台帳
- Archives を成果物ごとに回収する保管台帳

## 参照元

- `\\wsl.localhost\Ubuntu-22.04\home\kafka\projects\vlog\data\skills\vlog_user\manifest.json`
- `\\wsl.localhost\Ubuntu-22.04\home\kafka\projects\vlog\data\skills\vlog_user\SKILL.md`
- `\\wsl.localhost\Ubuntu-22.04\home\kafka\projects\vlog\data\skills\vlog_user\persona.md`
- `\\wsl.localhost\Ubuntu-22.04\home\kafka\projects\vlog\data\skills\vlog_user\work.md`
- `\\wsl.localhost\Ubuntu-22.04\home\kafka\projects\vlog\data\photos_prompts\`
- `\\wsl.localhost\Ubuntu-22.04\home\kafka\projects\vlog\data\summaries\`
- https://github.com/Open-LLM-VTuber/Open-LLM-VTuber
- https://github.com/tegnike/aituber-kit
- https://github.com/AIVTDevPKevin/AI-VTuber-System
- https://github.com/0Xiaohei0/LocalAIVtuber
- https://github.com/hansjm10/ai-vtuber-companion
- https://github.com/Scthe/ai-iris-avatar
- https://github.com/ZeroMirai/Waifu_AI_Vtuber
- https://github.com/topics/ai-vtuber

## まとめる候補

### persona_pack

- 口調
- 感情
- 距離感
- 禁止事項

### persona_sheet

- 一人称
- 口調
- 反応速度
- 言わないこと

### chat_reply_pack

- 短い返答
- コメント返し
- 質問への返事
- 反応の定型文

### daily_work_sheet

- その日の作業
- 優先順
- 進行状況
- 片付け

### local_offline_pack

- ローカル優先
- 低遅延
- 省リソース

### prompt_archive_sheet

- 日付
- 目的
- 出力先
- 再利用メモ

### memory_pack

- 短期記憶
- 長期記憶
- ログ要約

### summary_sheet

- 出来事
- 要点
- 感情
- 再利用タグ

### vfx_trigger_pack

- 感情ごとの表情
- エフェクト
- 演出

### photo_prompt_sheet

- 1枚絵
- 漫画
- スタンプ
- 告知

### subtitle_pack

- 字幕
- テロップ
- 見出し
- 表示文言

### output_library

- PNG
- WEBP
- TXT
- MD

### announcement_thumbnail

- 配信開始
- 新衣装
- 告知
- 記念日投稿

### discord_ready_sheet

- 16枚スタンプ
- 1枚見出し
- そのまま配布
- すぐ投稿

### voice_pipeline_pack

- 音声入力
- 音声出力
- 割り込み応答
- 返答待ち時間

### archive_index

- 日付
- 種別
- 派生物
- 保管先

### chat_platform_pack

- YouTube
- Twitch
- Discord
- コメント取得

### manga_prompt_book

- 1ページ漫画
- 7コマ構成
- 吹き出しなし
- 物語の流れ

### avatar_mode_pack

- Live2D
- VRM
- PNGTuber
- 3D

### character_output_matrix

- 顔
- 体
- 小物
- 表情差分

### control_panel_pack

- モデル切替
- 音声切替
- 表情切替
- 状態表示

### daily_prompt_log

- 何を作ったか
- 何を直したか
- 何を残すか
- 次の一手

### demo_mode_pack

- デモ端末
- サイネージ
- アイドルモード
- 自動発話

### stream_mode_sheet

- 配信待機
- 配信中
- 告知中
- 休止中

### moderation_pack

- NGワード
- 禁止話題
- 安全な返答
- 出力フィルタ

### safe_reply_sheet

- 危険回避
- 短く返す
- 話題変更
- 失礼回避

### slide_pack

- スライド発表
- 画面共有
- 説明文
- チュートリアル

### tutorial_sheet

- 手順
- 注意点
- 失敗例
- 成功例

### plugin_pack

- 外部連携
- WebSocket
- 拡張機能
- 追加コマンド

### extension_index

- 何とつながるか
- 何を受けるか
- 何を返すか
- 何を残すか

### character_customization_pack

- 見た目
- 性格
- 言い回し
- 設定差分

### persona_variation_sheet

- 本人っぽさ
- 役割
- 例外
- 固定

### research_log_pack

- 会話ログ
- 評価ログ
- 要約ログ
- 振り返り

### archive_reuse_sheet

- 保存
- 再利用
- 変換
- 再出力

## db に落としたもの

- `人格ポスター`
- `配信開始バナー`
- `返信スタンプシート`
- `話題切り替えバナー`
- `記憶メモボード`
- `配信後レビュー盤`
- `成果物コンタクトシート`
- `Kafka 人格固定カード`
- `配信運用シート`
- `配信後まとめカード`
- `生成素材台帳`
- `成果物回収台帳`
- `コメント返信カード`
- `話題切り替えカード`
- `記憶更新カード`
- `AI-Tuber 起動カード`
- `AI-Tuber 配信後レビューカード`

これで `persona.md` / `work.md` / `summaries` / `photos_prompts` / `archives` を、配信でそのまま使えるカードや台帳に変換できる。
さらに、画像生成にそのまま回せる派生テンプレートを別に切ってある。

## ひとまずの使い方

1. ここに候補を足す
2. 必要なものだけ `db/prompts.json` に移す
3. 用途ごとのテンプレートに分ける

## メモ

- まずは単純に分ける
- 後で重複を消す
- 1つのテンプレートに詰め込みすぎない
