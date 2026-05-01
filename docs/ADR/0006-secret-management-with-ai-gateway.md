# ADR 0006: cloud の Gemini API キー管理

ステータス: 承認済み

## コンテキスト

cloud で `POST /api/prompt-generate` が Gemini API を呼ぶとき、API キーをフロントエンドに置くと漏えいする。
local は Codex CLI を使うので、このキーは不要になる。

## 決定事項

- cloud の Gemini API キーはサーバー側の秘密情報として扱う。
- cloud では `GEMINI_API_KEY` 環境変数を使う。
- フロントエンドの `static/app.js` と HTML にはキーを書かない。
- local では Gemini キーを使わない。

## 理由

- キーが画面に出ないので、漏えい経路が単純になる。
- local と cloud で責務を分けやすい。
- 生成機能だけを先に作り、cloud 側の秘密管理は最小限にできる。

## 根拠・参照

- [Cloudflare Workers Secrets Management](https://developers.cloudflare.com/workers/configuration/secrets/)

## 影響

- cloud で `GEMINI_API_KEY` が未設定なら、生成APIは失敗する。
- local では `codex` CLI が無ければ失敗する。
- 生成失敗時は、フロントエンドにエラーを返す。
