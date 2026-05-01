# AGENTS.md

## まず見る

- [README.md](README.md): 何を置くリポジトリか、ローカル実行とビルドの入口
- [DESIGN.md](DESIGN.md): 画面の見た目、ギャラリー優先、モーダル優先の方針
- [db/prompts.json](db/prompts.json): テンプレート、ブロック、`artifacts` の本体
- [static/index.html](static/index.html): 画面構造とセクション配置
- [static/app.js](static/app.js): 一覧、検索、モーダル、画像表示のロジック
- [static/style.css](static/style.css): タイルサイズ、余白、画像/非画像の見た目
- [scripts/verify_pages.sh](scripts/verify_pages.sh): 公開表示の検証
- [docs/manual/001_cloudflare_pages.md](docs/manual/001_cloudflare_pages.md): Cloudflare Pages の確認手順
- [ローカル表示](http://127.0.0.1:8787/)
- [公開サイト](https://kafka2306.github.io/prompt-vault/)

## 変更の考え方

- 画像やテンプレートを増やすときは、まず `db/prompts.json` を直す
- 画像が一覧に出ない、カードが崩れる、画像あり/なしの区別が分かりにくいときは、`static/app.js` と `static/style.css` を直す
- セクションの並びや見出しを変えるときは、`static/index.html` を直す
- `dist/` は直接編集しない。`python3 build.py` で再生成する
- 補助スクリプトが必要なら `scripts/` に置く

## 変更手順

1. `db/prompts.json` を直す
   - テンプレートを増やす
   - `blocks` のつながりを整える
   - `artifacts` に実画像を追加する
2. 必要なら `static/app.js` を直す
   - 一覧の出し方を変える
   - 画像あり/なしの分岐を変える
   - モーダルやコピー動作を変える
3. 必要なら `static/style.css` を直す
   - タイルの大きさを変える
   - 画像あり/なしの見た目を分ける
   - モーダルのレイアウトを整える
4. 必要なら `static/index.html` を直す
   - セクションを増やす
   - 見出しや説明文を変える
5. `python3 build.py` を実行する
   - `dist/index.html`
   - `dist/style.css`
   - `dist/app.js`
   を更新する
6. `python3 app.py` で `http://127.0.0.1:8787/` を見る
   - 画像が大きすぎないか
   - `画像あり` と `画像なし` が一目で分かるか
   - モーダルで全文コピーできるか
7. `scripts/verify_pages.sh` を実行する
   - GitHub Pages の表示を確認する
   - Cloudflare Pages は `CF_PAGES_URL` があるときだけ確認する
8. 変更を出すなら `git add` → `git commit` → `git push` の順で進める
9. push 後は `gh run list` と `gh run view --log` を見る
10. 最後に [GitHub Pages](https://kafka2306.github.io/prompt-vault/) と [Cloudflare Pages 手順](docs/manual/001_cloudflare_pages.md) を確認する

## 例外なく守ること

- `dist/` を手で編集しない
- 重複した手順は増やさない
- 変更点に応じたファイルだけを直す
