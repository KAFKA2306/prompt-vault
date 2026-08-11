# KAFKA RESULTS data quality

`results/data-quality/<repo>.json` is a cross-repository evidence envelope. It does not invent a common data-quality metric when a repository has not published machine-readable evidence.

## Evidence boundary

- `unknown`, `not_instrumented`, and zero are distinct states.
- A repository is measured only through an explicit adapter to repository-owned machine-readable audit output.
- The central collector does not reimplement a repository's domain audit logic.
- Coverage metrics retain numerator and denominator; a ratio without its population is not canonical evidence.
- Materialized copies are not counted as additional verified records.
- `source_commit`, evidence paths, blob SHAs, and evidence URLs are retained for measured adapters.

## Initial adapter

`KAFKA2306/semiconductor-earnings-model` reuses the existing earnings-ledger audit artifacts:

- `audit_latest.json` for the accepted canonical population,
- `evidence_latest.json` for that audit's explicit verification window,
- `lineage_latest.json` for artifact SHA-256 coverage,
- `semantic_duplicate_audit_latest.json` for duplicate count,
- `rejection_reason_audit_latest.json` for rejected-record and rejection-reason coverage.

The adapter deliberately leaves record-level provenance coverage, common freshness/stale counts, null-reason coverage, broken evidence URLs, and 30-day verified-addition delta unknown because the registered audits do not currently expose those quantities as compatible aggregates.

## Completion boundary for Issue #36

This first adapter establishes the schema and proves reuse of an existing repository-owned audit. Issue #36 remains open until additional data-bearing repositories define canonical populations and until historical snapshots make `verified_added_30d` reproducible rather than inferred.
