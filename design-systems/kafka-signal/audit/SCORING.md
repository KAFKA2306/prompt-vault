# Scoring decision model

`nominal_grade` is derived only from the eight 0–5 dimension scores. `grade` is the actionable grade after evidence gates.

For S/A candidates, missing or failing browser evidence blocks promotion. The scorer preserves the nominal grade for traceability, caps the actionable grade to B, clears `canonical_target`, and sets `canonical_candidate=false`.

This makes the boundary between #24 discovery, scoring, #25 harvesting, and #26 browser verification explicit and fail-closed.
