# ADR 0004: SEO / LLMSEO の再現可能な最小構成

ステータス: 承認済み

## コンテキスト

このサイトは、画像生成プロンプトの保管庫であり、ブログやECのような強い更新型コンテンツではない。
そのため、検索エンジン向けのSEOと、AIエージェント向けの可読性を、同じ静的ファイル群で安定して維持できる形にしておく必要がある。

## 決定事項

- `static/index.html` に基本メタ情報を置く。
  - `title`
  - `description`
  - `canonical`
  - `lang`
  - Open Graph
  - Twitter card
- `schema.org` の JSON-LD を置く。
  - `WebSite`
  - `CollectionPage`
  - `Organization`
  - `BreadcrumbList`
  - `SearchAction`
- `static/robots.txt` を置く。
  - `Sitemap` を明示する
  - AI 向けの content signal コメントを含める
- `static/sitemap.xml` を置く。
  - トップページを 1 URL として宣言する
- `static/llms.txt` を置く。
  - 先頭に 1 文の description blockquote を置く
  - 人間向けの主導線ではなく、機械可読な補助ファイルとして扱う
- トップのヒーローから `llms.txt` を目立たせない。
  - 人間向け導線は gallery / template / GitHub を優先する
- 静的な見本画像と内部リンクを置く。
  - AI クローラが HTML だけで文脈を拾えるようにする
- 重要な変更後は `python3 build.py` を必ず実行する。
- 重要な変更後は `scripts/verify_pages.sh` で公開側の表示を確認する。

## 非決定事項

- `/.well-known/ucp` は必須にしない。
  - このサイトは販売サイトではなく、現時点で commerce protocol は必要ない
- 強いセキュリティヘッダは、実際に配信基盤が対応できる場合に限って追加する。
  - GitHub Pages 単独ではヘッダ制御に限界があるため、配信先に合わせて扱う
- `AggregateRating` は追加しない。
  - このサイトはレビュー集約の場ではない

## 理由

- 静的ファイル中心にすると、再現性が高い。
- 検索エンジンと AI エージェントの両方に対して、同じ出力物で整合を取りやすい。
- `llms.txt` や schema は、運用の途中で増減しても差分管理しやすい。
- トップの人間向け導線を増やしすぎると、ユーティリティとしての見通しが落ちる。

## 運用手順

1. `static/index.html` を更新する。
2. 必要に応じて `static/llms.txt`、`static/robots.txt`、`static/sitemap.xml` を更新する。
3. 必要に応じて `static/.well-known/ucp` や `static/_headers` を追加・削除する。
4. `python3 build.py` を実行する。
5. `python3 app.py` でローカル表示を確認する。
6. `scripts/verify_pages.sh` を実行する。
7. 変更を出す場合は `git add` → `git commit` → `git push` の順で進める。

## 影響

- SEO / LLMSEO の変更は、まず静的ファイルで表現する。
- 変更は `dist/` にも反映し、配信物との差分を残さない。
- 新しい AI 向けファイルを追加するときは、トップ導線に出す前に役割を明確にする。
- このサイトでは、見つけやすさと読みやすさを優先し、不要な protocol を増やさない。
