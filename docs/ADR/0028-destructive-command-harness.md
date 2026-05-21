# ADR 0028: Preflight Destructive Command Harness

## Status
Accepted

## Context
エージェントによる `git clean -fd` や `git restore` の誤用により、未コミットの画像アセットやデータベースの変更が消失するインシデントが発生した。LLMの注意深さに依存するのではなく、システム的に破壊的操作を制限する仕組みが必要である。

## Decision
以下の「破壊的コマンド・ハーネス」を導入し、エージェントの行動を制限する。

1.  **直接実行の禁止**: `git clean`, `git restore`, `git reset`, `rm`, `mv` 等の破壊的操作を直接実行することを禁止する。
2.  **安全スクリプトの強制**: 全ての破壊的操作の前に `scripts/guard_destructive.sh` を実行しなければならない。
3.  **`git clean` の代替**: `git clean` を実行する場合は、必ず `scripts/safe_git_clean.sh` を使用する。
4.  **エビデンスの記録**: 全ての判定結果は `runs/destructive_guard/YYYYMMDD-HHMMSS/` に保存される。
5.  **ハードゲート**:
    - 未追跡の画像ファイル（PNG/WebP/JPG）が存在する場合、実行を拒否する。
    - `db/prompts.json` が変更されている場合、実行を拒否する。
6.  **LLM自己申告の禁止**: 「安全である」という推論による判断を禁止し、スクリプトの `PASS` 出力のみを根拠とする。

## Consequences
- エージェントによる偶発的なデータ喪失リスクが大幅に低減される。
- 新規アセットの即時登録（`register_generated_artifact.py`）が事実上強制される。
- 破壊的操作の前に、未追跡ファイルのコミットまたは退避が必須となる。
