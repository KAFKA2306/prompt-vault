---
name: tts-validate
description: 日本語の TTS 台本を、生成前の危険予測と Whisper Mini のフィードバックで作成・検証・修正する。voice caption、台本下書き、壊れやすい行の予測、転写比較、TTS -> Whisper Mini -> diff ループ、転写後の修正、台本確定前の忠実度確認をしたいときに使う。
---

# TTS Validate

この skill は、最小構成の TTS ワークフローを回すために使う。
台本を作る。壊れやすさを予測する。音声を生成する。転写する。比較する。直す。
DB 監査やアセット登録とは分ける。

## 具体値のデフォルト

特に指定がない場合は、次を使う。

- プロジェクトルート: `/home/kafka/projects/prompt-vault`
- 作業ディレクトリ: `/home/kafka/projects/prompt-vault/.tmp/tts-validate`
- 元台本ファイル: `/home/kafka/projects/prompt-vault/.tmp/tts-validate/script.txt`
- 生成音声ファイル: `/home/kafka/projects/prompt-vault/.tmp/tts-validate/output.wav`
- Whisper 転写ファイル: `/home/kafka/projects/prompt-vault/.tmp/tts-validate/transcript.txt`
- 差分レポート: `/home/kafka/projects/prompt-vault/.tmp/tts-validate/diff.md`
- 比較モード: `meaning-first`
- 深刻度の順序: `critical`, `high`, `medium`, `low`
- 書き換え方針: ユーザーが強い書き換えを求めない限り、意図は維持する
- かな優先: 読み間違いしやすい漢字はかなに寄せる

## 推奨の実行設定

ユーザーが設定を指定しない場合は、次を優先する。

- 長文より短文
- 1 回のテストにつき 1 人の話者
- 2 案を比べるときは seed 固定
- デバッグ時は 1 回に 1 変更
- ユーザーが混在言語を求めない限り日本語のみ
- 1 回目の転写差分を見てから 2 回目に進む

## 実行テンプレート

エンドツーエンドで回すときは、次の流れで扱う。

1. 台本を `/home/kafka/projects/prompt-vault/.tmp/tts-validate/script.txt` に書く
2. 音声を `/home/kafka/projects/prompt-vault/.tmp/tts-validate/output.wav` に生成する
3. Whisper 転写を `/home/kafka/projects/prompt-vault/.tmp/tts-validate/transcript.txt` に出す
4. 比較レポートを `/home/kafka/projects/prompt-vault/.tmp/tts-validate/diff.md` に書く
5. 必要なら台本を書き直して繰り返す

作業ディレクトリが変わっても、ユーザーが別指定しない限りファイル名は同じにする。

## 書く内容

- ベースとなる声キャプション
- 短い読み上げ用台本
- 元文が壊れやすいときの、より通りやすい書き換え

## やること

- ユーザーが未作成なら、まず本文を下書きする。
- 生成前に壊れやすい行を予測する。
- 台本から音声を生成する。
- Whisper Mini で音声を転写する。
- 転写結果を元文と比較する。
- どこが壊れたかを分類する。
- 壊れた部分だけを書き直す。
- 十分安定するまで繰り返す。

## 生成前に見る点

- 同音異義語
- 漢字が多い語
- 固有名詞
- 長い節
- 弱い助詞
- 潰れやすい短い感嘆
- 名前、数字、記号の連続

## 生成後に比べる点

- 語の一致
- 意味
- 話し手の意図
- 間と文切れ
- 固有名詞と珍しい語

## 深刻度

- `critical`: 意味反転、否定の欠落
- `high`: 固有名詞の欠落、重要内容の欠落
- `medium`: 節の欠落、意図の弱化
- `low`: 小さな表記ゆれ

## 書き換え方針

- 長文は短く分ける
- 抽象語は具体語に置き換える
- 意味を残したい箇所だけ冗長性を足す
- 読み間違いしやすい漢字はかなに寄せる
- ユーザーが強い書き換えを求めない限り、意図は変えない

## 出力

次のいずれかを返す。

- 1 本の声キャプション
- 声キャプションと台本例
- 危険度表
- 転写差分
- 損傷レポート
- 修正版台本
- 短い反復チェックリスト

## 対象外

この skill では扱わない。

- `db/prompts.json` の整合性チェック
- artifact registration
- 画像ワークフロー
- 一般的なプロジェクト運用
