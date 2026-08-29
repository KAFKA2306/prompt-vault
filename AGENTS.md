# AGENTS.md

## Short-context start

最初に読むのはこのファイルと、現在のtaskを所有する実装・正準データ・validatorだけです。README、全Issue、全docs、過去artifactを先読みしません。必要なauthorityだけを追加で読み、同じ目的のIssue/PRがあれば継続します。

途中で止まる場合は、既存Issue/PRへ「現在state・確認済みevidence・blocker・次の1 action」を短く残します。chat historyを継続の正本にしません。

## 正本

変更判断は現在の実装と機械可読データを優先する。

- Prompt DBの型・読書き: `src/prompt_db.py`
- アセット採番・命名: `src/artifacts.py`
- 固定サイズ2D SVG検証: `src/designs.py`
- Skill一覧の読取り: `src/skills.py`
- 正準データ: `db/prompts.json`
- 正準アセット: `artifacts/`
- 固定サイズ2Dの編集可能な正準デザイン: `designs/*.svg`
- 静的生成: `build.py`
- 共通コマンド: `Taskfile.yml`
- UI: `static/`
- `dist/` は生成物。直接編集しない。

Markdown、Issue、過去の ADR が現在の実装と矛盾する場合は、現在の実装を確認し、古い説明を更新または削除する。未確認の仕様を docs や skills に書かない。

## 変更方針

- `src/` は用途が名前から分かる小さなモジュールを保つ。汎用的な `models.py` / `utils.py` / `helpers.py` を作らない。
- 現行規模で `domain/infra/services/` のような多層化を追加しない。責務が実際に分裂してから分割する。
- 既存の標準処理で解決できるなら新しい script、workflow、独自形式を増やさない。
- DELETE > MERGE > REPLACE > ADD。未使用・重複を実参照で確認してから削除する。
- synthetic、fixture、placeholder を本番結果や実アセットの代用にしない。
- 取得失敗、検証失敗、参照切れを silent fallback や broad exception で成功扱いにしない。
- コメントはコードから分からない理由、外部制約、互換性理由だけに使う。処理内容の言い換えは書かない。
- host 固有パス、個人環境、one-off 手順を repository の恒久ルールにしない。

## データとアセット

- `db/prompts.json` の変更は `src/prompt_db.py` と既存 validator に適合させる。
- アセットを追加・変更した場合は DB との接続を検証する。
- `designs/*.svg` では文字列、font、座標、図形を構造として保持し、`dist/` 側のコピーを正本にしない。
- 未接続ファイルを「念のため」保存し続けない。参照がないことを確認できたものは削除する。
- 一回限りの具体的な日付、セリフ、用途を再利用 block に混ぜない。再利用可能な構造と生成ごとの差分を分離する。

## 検証

変更後は対象範囲に応じて既存 Task を使う。

```bash
task validate
task artifacts-audit
task build
```

全体確認が必要な変更では `task deliver` を使う。新しい個別検証 script を追加する前に既存 validator へ統合できないか確認する。

Pull Request では変更した head SHA の CI を確認する。merge 後は `main` を読み返し、公開物に影響する変更は GitHub Pages / Cloudflare Pages の実 URL を確認する。ローカル build や CI 成功だけを production 成功の証拠にしない。

## 完了条件

次を満たしたときだけ完了とする。

1. 正準データ・実装・生成物の整合性が既存 validator で確認できる。
2. 変更した PR head SHA の CI が成功している。
3. merge 後の `main` に変更が存在する。
4. 公開物に影響する場合は production URL で結果を確認できる。
5. 古い説明、重複処理、不要な一時物を残していない。

確認できない項目は成功扱いにせず `UNVERIFIED` とする。
