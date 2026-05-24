---
name: safe-git-delivery
description: 変更の検証、プレフライトハーネスの確認、および Conventional Commits に準拠した安全な Git コミット・クリーンアップを統合したワークフロー。
---

# safe-git-delivery ワークフロー仕様

このスキルは、開発中の変更のコミット、検証、または破壊的コマンド（クリーンアップや変更の破棄）を実行する際に、二重実行やハーネス違反を防ぎ、安全にリポジトリを最新状態に保つためのワークフローを定義します。

## 1. 走行ルートとトリガー

以下の状況でこのスキルを実行します：

- 成果物の生成や修正が終わり、Git へのコミットを行う前。
- ワーキングツリーの変更を破棄・リセット・クリーンアップしたいとき。
- テストやバリデーションを実行し、変更状態の整合性を確認したいとき。

---

## 2. 実行手順 (Phases)

### Phase 1: 変更の精査と検証 (Diff & Test)

1. `git status` および `git diff` を実行して、意図しない変更が含まれていないか確認します。
2. `Taskfile.yml` に従って、検証テストを実行します。

   ```bash
   task test
   ```

   ※ このコマンドにより、`lint`, `format`, `deliver`（literals-audit, validate, artifacts-audit, build）が一括で実行されます。
3. エラーが出た場合は、直ちに修正フェーズ（修復ループ）に移行し、再度検証を行います。

### Phase 2: 安全なクリーンアップ (Preflight Clean) - ※必要な場合のみ

ワーキングツリーをリセット・クリーンアップする（`git clean` や `git restore` 等）場合、**直接の実行は永久に禁止**されています。必ず以下の手順を踏みます。

1. プレフライトハーネスを実行します。

   ```bash
   ./scripts/safe_git_clean.sh
   ```

2. 出力を確認し、判定に従います：
   - **PASS**: クリーンアップ対象の未追跡ファイルはありません。
   - **BLOCKED / FAIL**: クリーンアップによって削除されるファイルが存在します。**直ちに処理を停止**し、生成された証拠ディレクトリ（`runs/destructive_guard/`）と未追跡ファイルの一覧をユーザーに報告して指示を仰ぎます。LLM の自己判断でのクリーンアップ実行は禁止します。

### Phase 3: 安全なコミット (Safe Commit)

1. 変更が完全に検証され、ハーネスをパスしていることを確認します。
2. Conventional Commits 形式に従い、コミットメッセージを作成します（`git-commit-formatter` スキルを併用）。
3. コミットを実行します。

   ```bash
   git add <target_files>
   git commit -m "<type>(<scope>): <subject>"
   ```

---

## 3. 完了条件 (Fidelity Check)

- 全ての検証タスク (`task test`) が正常終了（Exit Code 0）していること。
- 直接的な `git clean` の実行履歴がなく、プレフライトハーネスを通していること。
- コミットメッセージが Conventional Commits 規格に準拠していること。
