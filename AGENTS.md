# AGENTS.md

## いつも見るところ

- [README.md](README.md)
- [DESIGN.md](DESIGN.md)
- [ローカル表示](http://127.0.0.1:8787/)
- [公開サイト](https://kafka2306.github.io/prompt-vault/)
- [GitHub リポジトリ](https://github.com/KAFKA2306/prompt-vault)
- [Cloudflare Pages 手順](docs/manual/001_cloudflare_pages.md)
- [表示検証スクリプト](scripts/verify_pages.sh)

## 実行方針

- `README.md` と `DESIGN.md` を先に読む
- `db/prompts.json` を先に直す
- 必要なら `static/app.js` を直す
- `python3 build.py` を実行する
- `python3 app.py` でローカル表示を見る
- `scripts/verify_pages.sh` で公開表示を見る
- `git add` → `git commit` → `git push` の順で出す
- `gh run list` を見る
- `gh run view --log` を見る
- [GitHub Pages](https://kafka2306.github.io/prompt-vault/) を見る
- [Cloudflare Pages 手順](docs/manual/001_cloudflare_pages.md) を見る
- `dist/` は直接編集しない
- 補助スクリプトは `scripts/` に置く

## いつもの手順

1. `db/prompts.json` を直す
2. `static/app.js` を直す
3. `python3 build.py` を実行する
4. `python3 app.py` でローカル表示を見る
5. `scripts/verify_pages.sh` で公開表示を見る
6. `git add` して `git commit` する
7. `git push` する
8. `gh run list` で GitHub Actions の実行一覧を見る
9. `gh run view --log` で GitHub Actions のログを見る
10. [GitHub Pages](https://kafka2306.github.io/prompt-vault/) を見る
11. [Cloudflare Pages 手順](docs/manual/001_cloudflare_pages.md) を見る
12. `dist/` は直接編集しない
13. 補助スクリプトは `scripts/` に置く
