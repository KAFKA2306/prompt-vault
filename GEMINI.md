# Project Guidelines: Prompt Vault

## TTS & Whisper Workflow
- **Whisper Cache**: Whisper のモデルはダウンロードを避けるため、必ずキャッシュディレクトリを指定して実行する。
  - コマンド例: `whisper <audio> --model small --language Japanese --model_dir ~/.cache/whisper`
- **Working Directory**: TTS 検証用の作業は `.tmp/tts-validate/` で行う。
- **Artifacts**: 音声アセットは `artifacts/` に配置し、`db/prompts.json` で管理する。
