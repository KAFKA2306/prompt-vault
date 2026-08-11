# KAFKA RESULTS — Adoption / Usage

Issue: https://github.com/KAFKA2306/prompt-vault/issues/39

`results/adoption/<repo>.json` records only usage evidence that can be supported by the selected source. The initial collector uses GitHub repository metadata to build a public-surface inventory and to record GitHub stars/forks as **proxy metrics only**.

## Contract

- A repository homepage or `has_pages=true` is evidence of a declared/deployed public surface, not proof that anybody used it.
- GitHub stars and forks are proxy/community signals. They are never labeled users, sessions, requests, conversions, or task completions.
- Page views, unique visitors, API requests, MCP calls, returning users, and task-completion events remain `null` with `not_instrumented` until a repository-owned measurement source exists.
- Unknown/unobserved usage is not converted to zero.
- A Pages URL is not guessed from repository naming when repository metadata does not return the actual URL.
- Private analytics and user-identifying data are outside this collector.
- Bot/crawler filtering is not claimed unless the future measurement source can demonstrate it.

## Current source

The collector reads the GitHub REST repository-list endpoint with API version `2026-03-10`, paginating beyond 100 repositories. For each non-archived public repository it stores repository/source identifiers and metadata timestamps as provenance.

The repository-list payload can support inventory and cumulative GitHub proxy values, but it cannot support 7-day/30-day real-usage claims. Therefore those windows are emitted as `not_instrumented`, rather than fabricated from cumulative stars/forks.

## Extension rule

Future repository-specific adapters may populate real usage only when they expose a stable evidence source with a period, definition, `data_as_of`, and provenance. Examples include a repository-owned privacy-safe telemetry artifact, API gateway request summary, or MCP call audit. The central collector must not infer these values from GitHub activity.
