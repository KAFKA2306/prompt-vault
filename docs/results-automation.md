# KAFKA RESULTS — Automation KPI

`results/automation/<repo>.json` measures observable GitHub Actions activity over a rolling 30-day window.

## Evidence boundary

- `scheduled_runs` counts runs for which GitHub reports `event=schedule`.
- `manual_trigger_runs` counts `workflow_dispatch` / `repository_dispatch` runs.
- `manual_start_actions_avoided.observed` equals scheduled runs and means only that the recorded run started without a human pressing the run button.
- It does **not** claim downstream work-hours saved or that a human would certainly have executed an equivalent job.
- A failed automated run is not automatically a manual intervention. Recovery is `not_computable_from_workflow_runs_alone` unless another source records it.
- Artifact generation without human editing is `not_instrumented` until artifact-level provenance is connected.
- `hours_saved` remains `unknown` without measured before/after timing evidence.

Every counted run retains run URL, workflow ID, commit SHA, event, conclusion, attempt, and timestamp as provenance. Zero and unknown are kept distinct.
