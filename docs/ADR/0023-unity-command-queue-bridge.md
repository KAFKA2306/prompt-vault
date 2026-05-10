# ADR 0023: Unity 操作は command queue と result file で行う

## ステータス

承認済み

## 決定

Unity への操作指示は、手順書だけに頼らず、ファイルベースの command queue を経由して行う。

構成は次の3点に固定する。

- `command` ファイル
- Unity Editor 側の実行スクリプト
- `result` ファイル

追加で、必要なときだけ `screenshot` を返す。

## 最小仕様

- `command` は 1 件ずつ書く。
- Unity Editor 側は `command` を読み、実行する。
- 実行結果は `result` に書く。
- `screenshot` は確認用の補助出力として扱う。

## 書かないこと

- GUI を人間に逐一押させる前提の説明
- 未確認の Unity API 挙動
- 実装していない自動化機能
- 推論による成功期待

## 運用

- 仕様を書くときは、`command` と `result` の入出力だけを書く。
- Unity 側の実装名は、実際のファイル名が決まってから書く。
- 未確定の細部は `未確認` と書く。

## 影響

- 手順書が GUI 依存から外れる。
- 実行結果をファイルで追える。
- 失敗時の状態を残しやすくなる。
