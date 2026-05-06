# 001 Cloudflare Pages 作成手順

この手順だけは、人間の Cloudflare アカウント操作が必要です。
最重要: Workers を作らない。Pages だけを作る。

## リンク集

- [ローカル表示](http://127.0.0.1:8787/)
- [GitHub リポジトリ](https://github.com/KAFKA2306/prompt-vault)
- [GitHub Pages 公開先](https://kafka2306.github.io/prompt-vault/)
- [Cloudflare Pages Git 連携](https://developers.cloudflare.com/pages/get-started/git-integration/)
- [Cloudflare Pages 設定](https://developers.cloudflare.com/pages/configuration/build-configuration/)
- [Cloudflare Dashboard](https://dash.cloudflare.com/)
- [表示検証スクリプト](../../scripts/verify_pages.sh)

## 目的

`prompt-vault` を Cloudflare Pages に公開する。ビルド工程をローカルで行うため、Cloudflare 側での環境構築やシークレット設定は不要。

## 前提

- GitHub リポジトリ `KAFKA2306/prompt-vault` が存在する
- `dist/` ディレクトリ（ビルド済み成果物）がリポジトリに含まれている

## 手順

1. Cloudflare にログインする
2. `Workers & Pages -> Pages -> Connect to Git` を選ぶ
3. リポジトリ `KAFKA2306/prompt-vault` を選ぶ
4. 設定を次の通りにする
   - `Build command`: **なし (空欄)**
   - `Build output directory`: `dist`
5. `Save and Deploy` を押す

## なぜこの設定なのか

ビルド済みの `dist/` フォルダを直接リポジトリに含めることで、Cloudflare 側でのビルド失敗（Pillow 等の不足）を物理的に防ぎ、100% 確実に配信するため。

## 成功確認

- `curl -s https://your-site.pages.dev/ | grep "Build:"` を実行し、最新のコミットハッシュが表示されれば成功。
- `scripts/verify_pages.sh` を実行して表示を確認。

## 失敗したら見る点

- `output directory` が `dist` になっているか
- GitHub 接続先が正しいか
- `dist/index.html` がリポジトリに入っているか
- ログに `npx wrangler deploy` と出る場合は、Pages ではなく Workers 側のプロジェクトを作っている
- その場合は今のプロジェクトを消して、`Workers & Pages -> Pages -> Connect to Git` から作り直す
