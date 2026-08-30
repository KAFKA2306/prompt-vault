# UI Design

この文書は Prompt Vault UI の**設計意図**を説明します。実際の色、spacing、component behaviorの正本は `static/` です。CSS値をこの文書と二重管理しません。

## Principles

### Quiet UI

Promptやartifact自体を主役にし、navigationや装飾を必要以上に強くしません。

- thin borders
- restrained shadows
- readable spacing
- content-first hierarchy
- hover animationを情報より目立たせない

### Hierarchy first

見出し、本文、metadata、actionの優先順位をspacing・size・toneで表現します。過剰なglow、neon、motionで階層を作りません。

### Readability

- 日本語と英語の長いpromptを読みやすくする
- copy actionを見つけやすくする
- code / prompt textのline-heightを確保する
- 12px未満の文字を通常UIとして常用しない
- keyboard focusが分かること

## Interaction

- Galleryから詳細へ進んでも戻れるnavigationを保つ
- Copy Full Promptのような主要actionを優先する
- hoverで大きく位置が動くcomponentを避ける
- modalやdetail viewは背景contextを完全に失わせない

## Layout

基本はcontentを追いやすいcentered layoutとし、gallery → detailの流れを単純にします。

Responsive behaviorや実際のbreakpointは `static/style.css` / `static/app.js` をauthorityとします。

## Typography

Font family、weight、sizeの実値はUI sourceをauthorityとします。固定サイズ2D designのfont contractはUIとは別で、`designs/*.svg` と `src/designs.py` が管理します。

## Do

- contentをUIより目立たせる
- copy / search / navigationを明快にする
- whitespaceを情報構造として使う
- subtleなinteraction feedbackを使う

## Do not

- dramatic shadowやneon glowを基本表現にする
- hoverだけでlayoutを大きく動かす
- design tokenの数値をMarkdownとCSSに重複して正本化する
- generated image内のvisual styleとapplication UI styleを混同する

## Authority

UIの実装を変更した場合、まず `static/` を変更します。この文書はstableな設計原則だけを持ち、current CSSのコピーにはしません。
