# Consumer usage

Pin `kafka-signal-v1.0.0` and its commit. Vendor required files under `vendor/kafka-signal/`, then record source, destination, release, commit, and SHA-256 in `kafka-signal.lock.json`.

Consumers may override layout density and domain composition. They may not redefine status semantics, remove provenance, or use character assets as authoritative evidence.

## Pages asset registry

Shared Pages assets are selected by canonical asset ID rather than copied ad hoc between repositories.

Canonical inputs:

- `assets/registry.json` — lists approved asset collections.
- Each collection manifest — records asset ID, canonical file, SHA-256, provenance/usage metadata.
- `consumers/schema.json` — defines the consumer manifest contract.

A consumer manifest declares only the assets it needs and repository-relative destinations. The `consumers/fixtures/` directory is test data; it is not live desired state for those repositories.

Example:

```json
{
  "schema_version": "1.0.0",
  "repository": "KAFKA2306/example",
  "assets": [
    {
      "collection": "site-basics",
      "id": "travel-basic",
      "destination": "public/assets/travel-basic-illustration.webp"
    }
  ]
}
```

Preview the update without writing files:

```bash
python design-systems/kafka-signal/scripts/vendor_assets.py \
  --source design-systems/kafka-signal \
  --destination /path/to/consumer \
  --consumer-manifest /path/to/consumer-manifest.json \
  --commit <PINNED_PROMPT_VAULT_COMMIT> \
  --dry-run
```

Apply the same pinned update by removing `--dry-run`. The command verifies each canonical source SHA-256 before copying and writes `.kafka-signal/pages-assets.lock.json` in the consumer repository. If a previously locked destination was modified locally, or an unmanaged destination would be overwritten with different content, the command fails instead of replacing it silently.

The consumer repository still owns its application data, page structure, build and deployment. Prompt Vault owns only the canonical shared asset package and its distribution metadata.

## Component retrieval

Use the canonical component manifest through the deterministic retrieval command:

```bash
python design-systems/kafka-signal/scripts/retrieve_components.py "証拠 出典 更新日時"
python design-systems/kafka-signal/scripts/retrieve_components.py "history changed"
```

The JSON result contains component IDs, observed capability terms, ranking reasons, canonical manifest repository/path/commit, and the measurement boundary. Japanese/English aliases expand query vocabulary only; they do not alter component metadata or manufacture quality evidence.

`--grade`, `--framework`, `--responsive`, and `--accessibility` are fail-closed filters. The current `components.manifest.json` does not yet carry those measured fields, so requesting one returns no matching component instead of assuming a grade, framework, responsive state, or accessibility status. Original source-repository provenance is likewise reported as `not_instrumented` until upstream component/scorecard metadata supplies it.
