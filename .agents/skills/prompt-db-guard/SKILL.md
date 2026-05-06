---
name: prompt-db-guard
description: prompts.json の整合性と品質を監査し、破壊的変更や責務崩壊を防ぐガードレール。
---

# prompt-db-guard

## 目的

`prompts.json` の構造的整合性と品質を維持し、不用意な修正によるシステムの崩壊を防ぐこと。

## 役割

- **監査のみ**: データの「悪い状態」を検出し、レポートする。
- **自動修正禁止**: ファイルの直接編集、ブロックの自動付与、IDの自動生成、削除は一切行わない。

## 禁止事項

1. **ファイルの直接編集**: 監査結果に基づいて人間が判断する。
2. **自動 block 付与**: title だけから `master_style` 等を推論して付けるのは禁止。
3. **template 自動統合**: 重複していても勝手に消さない。
4. **ID 自動生成**: 新規ブロック ID を勝手に作らない。

## 監査項目

1. **unknown block_id**: テンプレートから参照されているが存在しないブロック。
2. **duplicate id**: ブロック ID の重複。
3. **blocks: []**: 構成要素が空のテンプレート。
4. **見た目混入**: テンプレートの `summary` 等に「光」「衣装」などの視覚表現が含まれている（汚染）。
5. **複数 role 混入**: 1つのブロックに `pose`, `lighting`, `background` 等が 3 つ以上含まれている。
6. **ゴミ箱化**: `scene`, `layout`, `style` ブロックが曖昧な多目的要素を含んでいる。
7. **肥大化**: 200文字を超えるブロック、または 10件を超えるテンプレートブロック。

## 使用方法

`scripts/guard.py` を実行して JSON 出力を得る。

```bash
python3 scripts/guard.py
```

## 出力形式

必ず以下の JSON 形式で報告する。

```json
{
  "severity": "critical | warning | info",
  "type": "...",
  "id": "...",
  "title": "...",
  "reason": "...",
  "suggested_action": "...",
  "requires_human_review": true
}
```

## 原則

- **Template = 用途**（何を作るか、おはツイ、作業開始など）
- **Block = 素材**（材料、光、ポーズ、衣装など）
- **最優先事項**: 疑わしいものは直さず、警告を出して停止する。
