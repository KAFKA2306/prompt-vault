# Prompt Vault

画像生成プロンプトを、全文のまま積み上げるのではなく、
あとで使えるかたちにほどいて並べておく保管庫です。

KAFKA の世界観を保ちながら、
「すぐコピーできる」「組み替えやすい」「再現しやすい」を大事にしています。

## なぜつくったのか

- 毎回、長いプロンプトを最初から書きたくないから
- 似た出力を、少ない差分で再現したいから
- 完成イメージを先に見て、迷わず選びたいから

## どんなものができたのか

- 画像ギャラリーから完成イメージを探せる画面
- 拡大モーダルから全文プロンプトを1クリックでコピーできる画面
- ブロック、テンプレート、`artifacts` を JSON で管理するローカルDB
- GitHub Pages と Cloudflare Pages でそのまま配信できる静的構成

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
- [データベース定義 (SCHEMA.md)](docs/SCHEMA.md)

## どうやって簡単に再現するのか

### 1. ローカルで見る

```bash
python3 app.py
```

### 2. 静的に書き出す

```bash
python3 build.py
```

`dist/index.html` と `dist/style.css`、`dist/app.js` が生成されます。

### 3. 公開表示を確認する

```bash
bash scripts/verify_pages.sh
```

Cloudflare Pages を確認したいときは `CF_PAGES_URL` を渡します。

## データの置き場所

- `db/prompts.json` がローカルDBです
- ブロック、テンプレート、`artifacts` はここで管理します（名称には `カテゴリ: 名称` の規則を適用）
- 設計の確定事項は `docs/ADR/` に残します
- `static/index.html` が HTML の元です
- `static/style.css` と `static/app.js` が画面の本体です
- `dist/` は `python3 build.py` で作る生成物です
- `dist/` は直接編集しません

## 配信先

- [GitHub Pages](https://kafka2306.github.io/prompt-vault/)
- [Cloudflare Pages](https://prompt-vault-cg3.pages.dev/)

## 補足

- 画面の見た目や操作方針は [DESIGN.md](DESIGN.md) を見てください
- 作業の進め方は [AGENTS.md](AGENTS.md) にまとめています
