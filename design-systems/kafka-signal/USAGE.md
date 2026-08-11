# Consumer usage

Pin `kafka-signal-v1.0.0` and its commit. Vendor required files under `vendor/kafka-signal/`, then record source, destination, release, commit, and SHA-256 in `kafka-signal.lock.json`.

Consumers may override layout density and domain composition. They may not redefine status semantics, remove provenance, or use character assets as authoritative evidence.

## Component retrieval

Use the canonical component manifest through the deterministic retrieval command:

```bash
python design-systems/kafka-signal/scripts/retrieve_components.py "証拠 出典 更新日時"
python design-systems/kafka-signal/scripts/retrieve_components.py "history changed"
```

The JSON result contains component IDs, observed capability terms, ranking reasons, canonical manifest repository/path/commit, and the measurement boundary. Japanese/English aliases expand query vocabulary only; they do not alter component metadata or manufacture quality evidence.

`--grade`, `--framework`, `--responsive`, and `--accessibility` are fail-closed filters. The current `components.manifest.json` does not yet carry those measured fields, so requesting one returns no matching component instead of assuming a grade, framework, responsive state, or accessibility status. Original source-repository provenance is likewise reported as `not_instrumented` until upstream component/scorecard metadata supplies it.
