# KAFKA SIGNAL UI audit contract

This directory is the machine-readable boundary between discovery (#24), scoring, harvesting (#25), and browser verification (#26).

## Pipeline

```text
repo inventory / UI element discovery
  -> evidence-backed proposed scores
  -> scripts/score.py
  -> repo-ui-scorecard.json
  -> canonical candidates only
  -> harvester
  -> browser gate / evidence refresh
```

## Scoring rules

Each UI element has eight dimensions, each scored 0–5:

1. `visual_quality`
2. `task_completion`
3. `responsiveness`
4. `accessibility`
5. `interaction_quality`
6. `data_semantics`
7. `reusability`
8. `evidence_maintainability`

Nominal grades follow the parent issue contract: S=34–40, A=29–33, B=23–28, C=16–22, D=0–15.

The scorer is intentionally conservative. S/A are promotion grades and require browser evidence. If an S/A candidate lacks verified 360/768/1440 viewports, has console errors, unexpected overflow, failed keyboard/focus verification, or insufficient screenshots, it is emitted as `provisional`, is capped to actionable grade B, and `canonical_candidate` is forced to `false`. The original threshold result remains in `nominal_grade` for auditability.

The scorer does not invent UX judgement. Upstream analysis must provide explicit scores plus evidence. Its job is to validate dimensions, calculate totals, apply deterministic policy, and prevent unverified candidates from reaching the harvester.

## Usage

```bash
python design-systems/kafka-signal/scripts/score.py \
  --input path/to/ui-score-input.json \
  --output design-systems/kafka-signal/audit/repo-ui-scorecard.json
```

See `scorecard.schema.json`, `scoring-policy.json`, and `fixtures/` for the contract.
