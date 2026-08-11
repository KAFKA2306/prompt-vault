# KAFKA RESULTS — Code Quality / Bug Prevention Ratchet

`results/code-quality/<repo>.json` records observable code-quality gate outcomes over a 30-day current window and the preceding 30-day baseline.

## Evidence boundary

- `quality_gates` counts GitHub Actions workflows whose name/path indicates quality, lint, type, test, smoke, validate, or check.
- Only first-attempt runs contribute to acceptance/rejection counts. Retries remain in provenance but do not erase the initial rejection.
- A failed quality gate is **not** called a product bug. Reproducible bugs require repository-owned reproduction evidence.
- `lint_errors`, `type_errors`, `failing_tests`, flaky-test, dead-code, duplicate, and complexity counts remain `not_instrumented` unless native tools emit machine-readable output.
- `unknown` is never converted to zero.
- Baseline/current/delta are computed mechanically; regenerating the current report does not rewrite the previous 30-day time window.

Every observed run retains the workflow name, run URL, commit SHA, event, conclusion, attempt, and timestamp.

This collector intentionally does not infer bug counts from commit messages, PR text, or LLM judgment.
