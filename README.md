# Prompt Vault

## リンク集

- [公開サイト](https://kafka2306.github.io/prompt-vault/)
- [GitHub リポジトリ](https://github.com/KAFKA2306/prompt-vault)
- [Cloudflare Pages 手順](docs/manual/001_cloudflare_pages.md)
- [表示検証スクリプト](scripts/verify_pages.sh)
- [DESIGN.md](DESIGN.md)
- [AGENTS.md](AGENTS.md)

画像生成プロンプトを、全文ではなく「使える部品」に分解して置いておく保管庫です。

KAFKA の世界観を保ちながら、
- すぐコピーできる
- 用途別に組み直せる
- ブレを減らせる

そんな最小構成を目指しています。

## 何をするか

- マスタースタイルを置く
- キャラクターや衣装を分けて置く
- 用途別テンプレートで全文を組み立てる
- ブロック単位でも全文でもコピーする

## 使い方

### ローカル表示

```bash
python3 app.py
```

### 静的書き出し

```bash
python3 build.py
```

`dist/index.html` と `dist/style.css`、`dist/app.js` が生成されます。

## データ

- `db/prompts.json` がローカルDBです
- ここにブロックとテンプレートを保存します
- `static/index.html` が HTML の元です
- `static/style.css` と `static/app.js` が画面の本体です
- `dist/` は `python3 build.py` で作る生成物です
- `dist/` は直接編集しません

## 配信

- GitHub Pages
- Cloudflare Pages

## 検証

- `scripts/verify_pages.sh` で GitHub Pages と Cloudflare Pages の表示を確認します
- Cloudflare Pages の URL は `CF_PAGES_URL` で渡します
