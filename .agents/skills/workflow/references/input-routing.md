# Prompt Vault Input Routing

このファイルは、入力が画像だけ、path だけ、画像生成プロンプトだけのときに、最初に何をするかをまとめる。

## 1. 画像だけ

- その画像を登録対象として扱う。
- `scripts/register_generated_artifact.py` に渡せる `--source` を用意する。
- 必要なら `--title` と `--generated-prompt` を付ける。

## 2. path だけ

- その path を登録対象として扱う。
- `scripts/register_generated_artifact.py` に渡せる実体ファイルを確認する。
- 必要なら `--title` を付ける。

## 3. 画像生成プロンプトだけ

- 生成結果を登録対象として扱う。
- 先に生成した画像を `--source` に入れる。
- `--generated-prompt` で元プロンプトを残す。
