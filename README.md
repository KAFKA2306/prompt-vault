# Prompt Vault

画像生成プロンプトを、全文のまま積み上げるのではなく、
「あとで使えるかたち」にほどいて並べておくための保管庫です。

KAFKA の世界観を保ちながら、次の3つを大事にしています。

- すぐコピーできること
- 用途ごとに組み替えやすいこと
- ブレを減らして、再現しやすいこと

## すぐ開く場所

- [ローカル表示](http://127.0.0.1:8787/)
- [公開サイト](https://kafka2306.github.io/prompt-vault/)
- [Cloudflare Pages 公開先](https://prompt-vault-cg3.pages.dev/)
- [GitHub リポジトリ](https://github.com/KAFKA2306/prompt-vault)
- [Cloudflare Pages 手順](docs/manual/001_cloudflare_pages.md)
- [ADR](docs/ADR/README.md)
- [表示検証スクリプト](scripts/verify_pages.sh)
- [DESIGN.md](DESIGN.md)
- [AGENTS.md](AGENTS.md)

## このリポジトリでできること

- マスタースタイルを置く
- キャラクターや衣装を分けて置く
- 画像ギャラリーから、完成イメージを直感で探す
- 拡大モーダルから、全文プロンプトをそのままコピーする

## 使い方

### 1. ローカルで見る

```bash
python3 app.py
```

### 2. 静的に書き出す

```bash
python3 build.py
```

`dist/index.html` と `dist/style.css`、`dist/app.js` が生成されます。

## データの置き場所

- `db/prompts.json` がローカルDBです
- ブロック、テンプレート、`artifacts` はここで管理します
- 設計の確定事項は `docs/ADR/` に残します
- `static/index.html` が HTML の元です
- `static/style.css` と `static/app.js` が画面の本体です
- `dist/` は `python3 build.py` で作る生成物です
- `dist/` は直接編集しません

## 配信先

- GitHub Pages
- Cloudflare Pages

## 検証

- `scripts/verify_pages.sh` で GitHub Pages と Cloudflare Pages の表示を確認します
- Cloudflare Pages の URL は `CF_PAGES_URL` で渡します

## 補足

- 画面の見た目や操作方針は [DESIGN.md](DESIGN.md) を見てください
- 作業の進め方は [AGENTS.md](AGENTS.md) にまとめています
