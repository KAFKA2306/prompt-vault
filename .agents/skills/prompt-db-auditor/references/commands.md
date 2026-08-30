# Commands

Use these commands in order when the task is about ideal-state diff auditing.

- `python3 scripts/audit_db.py`
  - Structural audit of `db/prompts.json`
  - Reports errors and warnings
  - `--strict` fails on warnings as well

- `python3 scripts/validate_db.py`
  - Checks duplicate artifact paths across non-`generated` templates
  - Warns on orphaned files in `artifacts/`

- `python3 scripts/audit_artifacts.py`
  - Checks root `artifacts/` files against DB links
  - Fails on unlinked root files, missing linked files, `_orphaned` files that are still linked, and duplicate links

- `python3 build.py`
  - Regenerates `dist/`
  - Fails if a template references an unknown block or if a linked artifact file is missing

- `python3 scripts/artifacts/register_generated_artifact.py`
  - Use for registering generated `.png` or `.wav` files
  - Do not hand-edit `artifacts/` or `db/prompts.json` for new generated assets

- `python3 scripts/artifacts/reconnect_unconnected_pngs.py --dry-run`
  - Inspect existing unconnected PNGs before reconnecting them

## Diff Lens

Use the audit outputs to compare the current DB against the target shape.

- Canonical target: few core blocks, few core templates, only reusable recipes
- Unnecessary branches: merge candidates, archive candidates, delete candidates, canonical candidates
- Complexity sources: generated mixing, huge packs, synonym blocks, artifact memory, role boundary violations
- Recommended consolidation: merge near-duplicates, move archived content out, remove non-canonical branches, relocate generated history
