# KAFKA RESULTS — Reliability

Issue #37 の正準計測契約。GitHub Actions REST API の workflow / workflow-runs を一次データとして、KAFKA2306配下の非archive repositoryごとに過去30日を再生成する。

## 出力

`results/reliability/<repo>.json`。CIでは全repo分を生成・schema監査し、30日artifactとして保存する。生成snapshot自体は日次実行の観測値なのでmainへ自動commitしない。

## 意味論

- `success`, `failure`, `cancelled`, `timed_out`, `skipped` は別集計。cancelledをfailureへ混ぜない。
- `run_attempt == 1` をfirst attempt、それより大きい値をretryとして分離する。
- workflow単位とrepository集計を両方保持する。
- 各runはActions run URL、head SHA、event、status/conclusion、run attempt、created_atをprovenanceとして保持する。
- deploy成功をlive verification成功とはみなさない。workflow名/pathがlive/smokeを明示しない場合、`post_deploy_verification.status=not_instrumented` のままにする。
- workflow-runs APIだけで判定できない missed schedule、artifact verification、residue cleanup、regression rejection は0にせず `not_computable` / `not_instrumented` とする。
- GitHubが返す未知/追加conclusionは `other_raw_statuses` に保持し、既知カテゴリへ推測変換しない。

## 再生成

```bash
GITHUB_TOKEN=... python scripts/collect_reliability.py --owner KAFKA2306 --out results/reliability
```

CI `KAFKA RESULTS reliability` は日次、手動、関連変更のPR/main pushで実行する。collectorのunit test、全生成JSONのcontract audit、artifact保存、runtime生成物削除後のclean-checkoutをblocking stepとして持つ。

## 一次仕様

GitHub REST API `List workflow runs for a repository` を使用する。status/conclusion、created filter、head SHA、run URL等はGitHubが返す一次フィールドをそのまま使用し、推測値へ置換しない。
