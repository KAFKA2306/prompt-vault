# Fail Conditions

Treat the following as FAIL during ideal-state diff audit, even if a script only warns in some cases.

## Structure

- Unknown block reference from a template
- Duplicate block ID
- Missing `role` on a block
- Template with empty `blocks` when it is not `generated`
- Template with too many blocks for the current review
- Pack block that is clearly too large or too broad
- A block contains more than one responsibility
- A template has more than one purpose
- Identity and scene are mixed in the same block
- Background and emotion are mixed in the same block
- Generated and canonical content are mixed in the same template layer
- Template acts as both reusable composition and generated snapshot
- `generated_prompt` is treated as source of truth
- `generated` is left ambiguous as status, category, source, or provenance
- Pack functions as a semantic black box instead of a bounded bundle

## Identity Protection

- Identity core is changed without explicit review
- Hair, eyes, emotional signature, or air feel are edited as if they were scene details
- Identity block mixes scene, outfit, background, or layout content
- Character core is scattered across multiple blocks without a clear lock block
- Identity and negative prompts conflict
- Unverified generation is treated as PASS
- Identity lock depends only on LLM obedience instead of schema-level constraints

## Artifact Integrity

- Duplicate non-`generated` artifact path
- Linked artifact file is missing
- Root `artifacts/` file is unlinked
- A file under `artifacts/_orphaned/` is still linked from DB
- Duplicate DB links point to the same artifact path
- Orphan / duplicate / deprecated state is left unresolved
- Prompt lifecycle and artifact lifecycle are treated as the same thing

## Review Discipline

- A change is accepted only because it "looks fine"
- A diff is approved without checking before/after
- Deprecated content is reused as if it were current
- Missing evidence is replaced by guesswork
- LLM output is trusted without schema, reference, artifact, and diff checks
- The audit stops at the first aesthetic impression instead of structural analysis
- PASS is given to something that only looks close to ideal
