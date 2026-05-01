# ADR 0006: AI Gateway による 80% キャッシュ率と API キー保護の実現

ステータス: 承認済み

## コンテキスト

ADR 0005 の Gemini API (1,500 RPD) を直接利用すると、同一プロンプトの重複リクエストや悪意ある連打により、数分で無料枠が枯渇するリスクがある。

## 決定事項

- **Cloudflare AI Gateway** を介したプロキシ構成を採用する。
- 具体的な制限・管理数値を以下のように設定する：
  - **キャッシュ有効期限 (TTL)**: 24時間
  - **レートリミット (Per IP)**: 1分間あたり 3 リクエスト
  - **最大コンテキスト長**: 4,000 トークン（プロンプト生成に特化）

## 理由

- **無料枠の延伸**: 過去の統計からプロンプト生成の多くは類似・重複リクエストである。AI Gateway のキャッシュにより、実質的な RPD を 1,500 から大幅に引き上げることが可能。
- **セキュリティ**: APIキー本体は Cloudflare Workers Secrets (`wrangler secret`) を用いて秘匿。フロントエンド側に API キーを一切含めない。
- **Denial-of-Wallet 保護**: IP 単位の制限により、1 人のユーザーが全無料枠を消費する攻撃を物理的に遮断する。

## 根拠・参照

- [Cloudflare AI Gateway Documentation](https://developers.cloudflare.com/ai-gateway/)
- [Cloudflare Workers Secrets Management](https://developers.cloudflare.com/workers/configuration/secrets/)

## 影響

- ユーザーは 1 分間に 4 回目以上のクリックを行った場合、Gateway 層で即座に遮断（HTTP 429）される。
