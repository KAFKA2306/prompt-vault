# KAFKA SIGNAL state scenes

## Design decision

State scenes are a dedicated collection rather than additions to `site-basics`.

`site-basics` contains site/editorial illustrations tied to particular Pages experiences. State scenes encode a reusable UI state vocabulary shared by dashboards, repository landing pages, CI/deploy views, and other consumers. Keeping them separate prevents site-specific illustration inventory from becoming the canonical source for operational state semantics.

## Consumer contract

- The SVG is supplemental artwork. A visible heading and description remain mandatory in the consuming UI.
- State is selected only from canonical consumer data; never infer state from artwork, color, filename, or pictogram.
- If an asset cannot load, the heading, description, state, and action remain available.
- Consumers pin an immutable Prompt Vault commit/release and vendor the selected asset locally. Runtime hotlinks to mutable `main` are forbidden.
- The default mini-scene viewBox is `0 0 192 128`; consumers scale responsively without cropping semantic UI text.

The `fixture.svg` file is a catalogue/consumer fixture showing representative empty, success, and failure states with visible labels. It is not a runtime source of truth.
