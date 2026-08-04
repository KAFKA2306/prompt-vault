# KAFKA SIGNAL Site Basics

KAFKA2306の公開Pages向けに生成した、軽量なベーシック挿絵コレクションです。各画像はKAFKA SIGNALの色・線・キャラクター契約を共有しながら、サイト固有の情報領域を示します。

## 許可用途

- ページ導入
- オンボーディング
- 空状態
- 編集的な表紙・セクション区切り

## 禁止用途

- 一次情報、証拠、公式画像の代替
- 財務数値、投資判断、公式ルール、安全・法的警告の話者
- 商品・作品・イベント・旅行先の公式な推薦または承認表示
- 第三者IPのキャラクターや公式素材であるかのような利用

Kafkaキャラクターはidentity accentであり、専門家、運営者、公式情報源ではありません。

## 配布仕様

- 透過WebP
- UI用の軽量プレビュー／ベーシック資産
- 元の生成セッション出力: 1536 × 1024
- リポジトリ格納版: 64〜256px幅
- 生成ID、再生成プロンプト、SHA-256、用途制約は`manifest.json`と`PROMPTS.md`に記録

高解像度の生成セッション原本はこのリポジトリには含みません。利用側は、このコレクションを含むcommitと各ファイルのSHA-256を固定してください。

## 実装規則

1. `width`と`height`を指定し、CLSを防ぐ。
2. below-the-foldではlazy loadする。
3. 装飾用途では`alt=""`、画像自体を説明対象にする場合だけ短い文脈的altを付ける。
4. 自然解像度を超えて拡大しない。
5. 画像が欠落しても、本文・CTA・状態・証拠を完全に理解・操作できるようにする。
6. 公式写真、商品画像、ポスター、イベント告知とは視覚的・意味的に分離する。

## ファイル

| Site | File |
|---|---|
| CrewTrade | `crewtrade-basic-illustration.webp` |
| bonus | `bonus-basic-illustration.webp` |
| boothitemmanager | `boothitemmanager-basic-illustration.webp` |
| semiconductor-earnings-model | `semiconductor-earnings-model-basic-illustration.webp` |
| bodogenomikata2 | `bodogenomikata2-basic-illustration.webp` |
| investor | `investor-basic-illustration.webp` |
| travel | `travel-basic-illustration.webp` |
| anime | `anime-basic-illustration.webp` |
| vrc_cast_event_calender | `vrc-cast-event-calendar-basic-illustration.webp` |
| pal-atlas | `pal-atlas-basic-illustration.webp` |
