# AUDIT_SYSTEM — superseded

このファイルは既存リンク維持のため残しています。

現在の監査・validation・production verificationの正準説明は [VALIDATION.md](VALIDATION.md) です。日常の実行順は [OPERATIONS.md](OPERATIONS.md) を参照してください。

## Current implementation

現在のrepositoryで実際に使う入口は、主に次です。

```bash
task validate
task artifacts-audit
task build
task deliver
```

それぞれが何を検証するかは `Taskfile.yml` とvalidator実装がauthorityです。

## Why this document was reduced

旧版は、実際のrepositoryに存在するvalidatorと、将来構想のruntime/harness/provenance機構を一つの「全体仕様」として混在させていました。

Documentation refactor後は次を分離します。

- current validation: [VALIDATION.md](VALIDATION.md)
- current architecture: [ARCHITECTURE.md](ARCHITECTURE.md)
- current operations: [OPERATIONS.md](OPERATIONS.md)
- historical decisions: `ADR/`

実装されていない仕組みをcurrent systemとして復活させないでください。
