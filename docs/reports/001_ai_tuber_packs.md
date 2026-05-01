# 001 AI Tuber Packs

## 目的

`vlog/data` を参考に、AI-Tuber 系で再利用しやすい部品を先に整理する。

## 参考にした構造

- 日付ベースで並ぶ
- 同じ内容でも用途別に分かれる
- 完成物をそのまま使える形にする
- `discord_ready` のように出力先を明示する

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

### chat_reply_pack

- 短い返答
- コメント返し
- 質問への返事
- 反応の定型文

### local_offline_pack

- ローカル優先
- 低遅延
- 省リソース

### memory_pack

- 短期記憶
- 長期記憶
- ログ要約

### vfx_trigger_pack

- 感情ごとの表情
- エフェクト
- 演出

### subtitle_pack

- 字幕
- テロップ
- 見出し
- 表示文言

### announcement_thumbnail

- 配信開始
- 新衣装
- 告知
- 記念日投稿

### voice_pipeline_pack

- 音声入力
- 音声出力
- 割り込み応答
- 返答待ち時間

### chat_platform_pack

- YouTube
- Twitch
- Discord
- コメント取得

### avatar_mode_pack

- Live2D
- VRM
- PNGTuber
- 3D

### control_panel_pack

- モデル切替
- 音声切替
- 表情切替
- 状態表示

### demo_mode_pack

- デモ端末
- サイネージ
- アイドルモード
- 自動発話

### moderation_pack

- NGワード
- 禁止話題
- 安全な返答
- 出力フィルタ

### slide_pack

- スライド発表
- 画面共有
- 説明文
- チュートリアル

### plugin_pack

- 外部連携
- WebSocket
- 拡張機能
- 追加コマンド

### character_customization_pack

- 見た目
- 性格
- 言い回し
- 設定差分

### research_log_pack

- 会話ログ
- 評価ログ
- 要約ログ
- 振り返り

## ひとまずの使い方

1. ここに候補を足す
2. 必要なものだけ `db/prompts.json` に移す
3. 用途ごとのテンプレートに分ける

## メモ

- まずは単純に分ける
- 後で重複を消す
- 1つのテンプレートに詰め込みすぎない
