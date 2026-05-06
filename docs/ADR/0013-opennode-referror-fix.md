# ADR 0013: openNode 未定義バグの根本原因と対処

## 状況

`static/app.js` の 86 行目に以下の記述があった。

```js
window.openNode = openNode;
```

`openNode` 関数はどこにも定義されていなかったため、ページロード時に `ReferenceError: openNode is not defined` が発生し、それ以降の `renderRail()` / `renderGen()` が実行されなかった。

## 症状

- `db.templates.length` は 135（データは正常）
- `template-count` 要素は `0 templates`
- テンプレートカードが一切表示されない
- JS コンソールに `[SEVERE] Uncaught ReferenceError: openNode is not defined` が出力される

## 検出方法

Selenium（ヘッドレス Chrome）で以下を確認：

```python
db_size = driver.execute_script("return db.templates?.length")  # → 135
logs = driver.get_log("browser")  # → ReferenceError
count_text = driver.find_element(By.ID, "template-count").text  # → "0 templates"
```

## 対処

`openNode` を `openModal` のエイリアスとして定義する。

```js
// 修正前
window.openNode = openNode;

// 修正後
window.openNode = (id) => openModal(id);
```

## 教訓

- `window.xxx = xxx` のような再エクスポートは、参照先が定義済みであることを必ず確認する。
- ビルドが通っても JS 実行時エラーはバリデーションで検出できない。
- Selenium による本番 URL チェックをデプロイ後の標準検証手順に組み込むこと。
