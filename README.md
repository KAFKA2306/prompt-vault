# Prompt Vault

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
python app.py
```

### 静的書き出し

```bash
python build.py
```

`dist/index.html` が生成されます。

## データ

- `db/prompts.json` がローカルDBです
- ここにブロックとテンプレートを保存します

## 配信

- GitHub Pages
- Cloudflare Pages

## 補足

- Cloudflare Pages の手順は [`docs/manual/001_cloudflare_pages.md`](docs/manual/001_cloudflare_pages.md)
- 公開URLは [GitHub Pages](https://kafka2306.github.io/prompt-vault-/)

