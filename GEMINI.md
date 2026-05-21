# Project Guidelines: Prompt Vault

## TTS & Whisper Workflow
- **Whisper Cache**: Whisper のモデルはダウンロードを避けるため、必ずキャッシュディレクトリを指定して実行する。
  - コマンド例: `whisper <audio> --model small --language Japanese --model_dir ~/.cache/whisper`
- **Working Directory**: TTS 検証用の作業は `.tmp/tts-validate/` で行う。
- **Artifacts**: 音声アセットは `artifacts/` に配置し、`db/prompts.json` で管理する。

## Destructive Command Preflight Harness (Agent Contract)

- **直接実行の禁止**: `git clean -fd` や `git restore` などの破壊的コマンドを直接実行することを永久に禁止する。
- **プレフライトハーネスの義務化**: ワーキングツリーの変更を取り消す、またはクリーンアップする際は、必ず `scripts/safe_git_clean.sh` もしくは `scripts/guard_destructive.sh` を事前に実行しなければならない。
- **機械的判定の厳守**: `safe_git_clean.sh` が **BLOCKED** または **FAIL** を出力した場合、LLMの自己判断による安全アピールを禁止し、直ちに処理を停止して証拠ディレクトリと未追跡ファイルの一覧のみをユーザーに報告しなければならない。
- **実存根拠のない要約禁止**: 物理的にディスク上に存在しないアセットファイルを「復旧可能」と報告してはならない。


