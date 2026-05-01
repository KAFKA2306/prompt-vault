# 001 Cloudflare Pages 作成手順

この手順だけは、人間の Cloudflare アカウント操作が必要です。

## リンク集

- [GitHub リポジトリ](https://github.com/KAFKA2306/prompt-vault)
- [GitHub Pages 公開先](https://kafka2306.github.io/prompt-vault/)
- [Cloudflare Pages Git 連携](https://developers.cloudflare.com/pages/get-started/git-integration/)
- [Cloudflare Pages 設定](https://developers.cloudflare.com/pages/configuration/build-configuration/)
- [Cloudflare Dashboard](https://dash.cloudflare.com/)
- [表示検証スクリプト](../../scripts/verify_pages.sh)

## 目的

`prompt-vault` を Cloudflare Pages に公開する。

## 前提

- GitHub リポジトリ `KAFKA2306/prompt-vault` が存在する
- `main` ブランチに `build.py` と `db/prompts.json` が入っている

## 手順

1. Cloudflare にログインする
2. `Workers & Pages` を開く
3. `Create application` を押す
4. `Pages` を選ぶ
5. `Connect to Git` を選ぶ
6. GitHub を接続する
7. リポジトリ `KAFKA2306/prompt-vault` を選ぶ
8. 設定を次の通りにする
   - `Production branch`: `main`
   - `Build command`: `python build.py`
   - `Build output directory`: `dist`
9. `Save and Deploy` を押す

## 成功確認

- デプロイ完了後に公開 URL を開く
- `dist/index.html` の内容が表示されれば成功
- さらに `scripts/verify_pages.sh` を実行して GitHub Pages と Cloudflare Pages の両方を確認する

## 失敗したら見る点

- `build command` が `python build.py` になっているか
- `output directory` が `dist` になっているか
- GitHub 接続先が正しいか
- ログに `npx wrangler deploy` と出る場合は、Pages ではなく Workers 側のプロジェクトを作っている
- その場合は今のプロジェクトを消して、`Workers & Pages -> Pages -> Connect to Git` から作り直す
