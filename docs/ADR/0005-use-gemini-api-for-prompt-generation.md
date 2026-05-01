# ADR 0005: Gemini API (1,500 RPD) による生成機能のバックエンド構成

ステータス: 承認済み

## コンテキスト

フロントエンドのプロンプト生成ボタンにおいて、維持コスト 0 円を維持しつつ、ユーザー体験を損なわないリクエスト回数を確保する必要がある。現時点で最も数値的優位性が高く、かつ無料で永続利用可能なモデルを選定する。

## 決定事項

- **Google Gemini 1.5 Flash** を採用する。
- 無料枠の制約条件を以下の数値に固定する：
  - **15 RPM (Requests Per Minute)**
  - **1,500 RPD (Requests Per Day)**
  - **1M TPM (Tokens Per Minute)**

## 理由

- **コスト優位性**: 月額コスト 0 USD。他社（OpenAI/Anthropic）はAPIの永続的な無料枠を提供していないが、Geminiは1日1,500回まで無料で利用可能。
- **Grok との比較**: xAI (Grok) は初回登録時にプロモーションクレジット（$25〜$150程度）を配布することがあるが、永続的な無料枠（Monthly/Daily Free Quota）は2026年時点でも公式には提供されていない。

## 根拠・参照

- [Gemini API Pricing and Limits](https://ai.google.dev/pricing)
- [Google AI Studio Gemini 1.5 Flash Rate Limits](https://ai.google.dev/gemini-api/docs/models/gemini#gemini-1.5-flash)
- [xAI (Grok) API Documentation](https://docs.x.ai)

## 影響

- 1,500 RPD を超えるアクセスがあった場合、HTTP 429 エラーが返却されるため、フロントエンドで上限通知を表示するロジックが必要。
- 全文検索や複雑な推論が必要になった場合は、上位モデル（Pro）への切り替えを検討する。
