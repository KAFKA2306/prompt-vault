# Output contract

The scorer emits `repo-ui-scorecard.json`-compatible JSON with `total`, `nominal_grade`, actionable `grade`, `decision_status`, `canonical_candidate`, and evidence/provenance fields. Downstream harvesting must never infer promotion from `nominal_grade`; it must require `canonical_candidate=true`.
