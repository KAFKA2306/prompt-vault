# ADR 0024: wav artifact を画像 artifact と同じ登録経路で扱う

## ステータス

承認済み

## コンテキスト

Prompt Vault では、生成物を `db/prompts.json` の `artifacts` で管理している。
従来は PNG を前提にした登録・検証・配布になっていたため、wav 音声を同じ仕組みで扱うには追加対応が必要だった。

音声生成フローを画像生成フローと並列に扱うには、次の点を揃える必要がある。

- 生成結果を `artifacts/NNN_slug.wav` として登録できること
- `db/prompts.json` の `artifacts` に wav を接続できること
- `build.py` が wav を dist に配布できること
- `app.py` が wav を配信できること
- 監査と検証が root `artifacts/` の PNG だけを前提にしないこと

## 決定

- `scripts/artifacts/register_generated_artifact.py` は PNG と wav を登録対象にする。
- `src/artifact_ops.py` の採番は、`artifacts/` 内のファイル全体を見て決める。
- `build.py` は PNG を WebP 化し、wav はそのまま dist にコピーする。
- `app.py` は wav を `audio/wav` で配信する。
- `scripts/validate_db.py` と `scripts/audit_artifacts.py` は、`artifacts/` の実ファイル全体を監査対象にする。
- `docs/SCHEMA.md` は、`artifacts.path` が画像だけでなく音声も指せることを明示する。

## 理由

- 画像と音声を別の流れに分けると、登録・配布・監査の重複が増える。
- 1 つの登録経路に寄せると、採番規則と DB 接続を共通化できる。
- wav を artifact として扱うと、画像生成と音声合成を並列に作っても管理方法が変わらない。
- UI が音声を直接再生できれば、生成結果の確認がその場でできる。

## 影響

- 生成音声は `artifacts/NNN_slug.wav` に保存できる。
- 既存の PNG ワークフローはそのまま使える。
- Gallery は画像と音声を同じ一覧に並べられる。
- 監査は「root `artifacts/` に未接続ファイルを残さない」方針を維持する。

## 運用

1. PNG か wav を登録するときは `scripts/artifacts/register_generated_artifact.py` を使う。
2. 変更後は `python3 build.py` と `python3 scripts/validate_db.py` を実行する。
3. 追加した wav は `http://127.0.0.1:8787/` で再生確認する。
4. root `artifacts/` に未接続ファイルを残さない。
