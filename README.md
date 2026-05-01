# Prompt Vault

画像生成プロンプトを1人で管理するための最小サイト。

## 起動

```bash
python app.py
```

## 静的書き出し

```bash
python build.py
```

`dist/index.html` が生成される。

## できること

- 一覧
- 検索
- カテゴリ絞り込み
- 固定表示
- 複製
- 保存
- 削除
- まとめコピー

## データ

- `db/prompts.json` がローカルDB
- 追記・更新はこのファイルに保存される

## 配信先

- GitHub Pages
- Cloudflare Pages
