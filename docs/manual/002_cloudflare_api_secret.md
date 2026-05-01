# 002 Cloudflare Pages API シークレット設定手順

この手順は人間による Cloudflare ダッシュボード操作が必要です。
ADR 0006 の「cloud では GEMINI_API_KEY を環境変数で管理する」決定を実現するための設定です。

## リンク集

- [Cloudflare Dashboard](https://dash.cloudflare.com/)
- [Cloudflare Pages 環境変数ドキュメント](https://developers.cloudflare.com/pages/configuration/environment-variables/)
- [Google AI Studio](https://aistudio.google.com/app/apikey)
- [ADR 0006](../ADR/0006-secret-management-with-ai-gateway.md)

## 前提

- Cloudflare Pages プロジェクト `prompt-vault` が作成済みであること（[001_cloudflare_pages.md](001_cloudflare_pages.md) 参照）
- Google AI Studio で Gemini API キーを取得済みであること

## Gemini API キーの取得

1. [Google AI Studio](https://aistudio.google.com/app/apikey) を開く
2. `Create API key` を押す
3. 生成されたキーをコピーして安全な場所に保管する

## Cloudflare Pages へのシークレット設定手順

1. [Cloudflare Dashboard](https://dash.cloudflare.com/) にログインする
2. 左メニューから `Workers & Pages` を開く
3. `Pages` タブを選び、`prompt-vault` プロジェクトを選択する
4. `Settings` タブを開く
5. `Environment variables` セクションに移動する
6. `Add variable` を押す
7. 次の通りに入力する
   - `Variable name`: `GEMINI_API_KEY`
   - `Type`: `Secret`（暗号化保存）
   - `Value`: 取得した Gemini API キーを貼り付ける
8. `Production` と `Preview` の両方に設定する
9. `Save` を押す

## ローカル開発用の設定

ローカルで `wrangler pages dev` を使う場合は `.dev.vars` を作成する。

```
GEMINI_API_KEY=your_actual_key_here
```

`.dev.vars` はリポジトリにコミットしない（`.gitignore` に追記すること）。

## 確認方法

設定後、Pages Function（`functions/api/prompt-generate.js`）内で次のようにキーを参照できる。

```js
const apiKey = context.env.GEMINI_API_KEY;
```

キーが未設定の場合、生成 API は 500 エラーを返す。

## 注意事項

- `Secret` 型を選ぶこと。`Plain text` だとダッシュボード上でキーが平文表示される
- キーをフロントエンドの HTML や JS に書かない
- `.dev.vars` を `.gitignore` に追加することを忘れない
