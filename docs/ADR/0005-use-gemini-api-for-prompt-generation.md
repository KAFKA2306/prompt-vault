# ADR 0005: local は Codex CLI / cloud は Gemini API の生成バックエンド

ステータス: 承認済み

## コンテキスト

既存の `blocks` と `templates` に、ユーザーの追加指示を組み合わせて新しいプロンプトを作りたい。
ただし、既存ブロックを毎回言い換えてしまうと、モジュール志向が崩れて再利用性が落ちる。
そのため、既存部分はそのまま流用し、生成は「新しい追加分」だけに絞る。

## 決定事項

- 生成APIは `POST /api/prompt-generate` とする。
- 入力は `template_id`、`block_ids`、`instruction` の3つを基本にする。
- ローカルの生成バックエンドは **Codex CLI** にする。
- cloud の生成バックエンドは **Google Gemini 1.5 Flash** にする。
- 既存ブロックは原則流用しつつ、シチュエーションが異なるときは `block_updates` で差し替える。
- 返却はコピー用の完成プロンプト1本と、その元になった生成メタデータにする。
- 生成テンプレートのタイトルは、元テンプレート名だけでなくユーザー指示も含む入力由来にする。
- フロントから Codex を呼ぶときの生成プロンプト本体は `prompts/frontend_codex.md` で管理する。
- ローカルでは生成結果を `db/prompts.json` の `generated_prompts` に追記する。
- `db/prompts.json` は canonical データと生成履歴を同居させる。
- cloud では生成結果を保存しない。
- 採用は手動で行う。

## 理由

- local と cloud の責務が分かれるので、環境差分が単純になる。
- 同じDBに入るので、ローカルでは探索と確認が一つのファイルで済む。
- cloud では保存しないので、配信面の静的性を壊さない。
- ユーザーは生成結果をコピーして ChatGPT GUI に貼るだけでよい。

## 根拠・参照

- [Codex CLI help](https://github.com/openai/codex)
- [Gemini API Pricing and Limits](https://ai.google.dev/pricing)
- [Google AI Studio Gemini 1.5 Flash Rate Limits](https://ai.google.dev/gemini-api/docs/models/gemini#gemini-1.5-flash)

## 影響

- ローカルでは `codex` CLI が必要になる。
- cloud では `GEMINI_API_KEY` をサーバー側で設定する必要がある。
- フロントエンドには API キーを置かない。
- ローカルでは `db/prompts.json` に `generated_prompts` が増えていく。
- cloud では生成履歴は残らない。
- 生成テンプレートは一覧に混ざる。タイトルは毎回再生成し、ブロックも必要なら更新する。
- Codex 用 prompt は `prompts/` 配下を日々更新して安定化できる。
