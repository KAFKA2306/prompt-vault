# KAFKA SIGNAL

KAFKA SIGNAL is the canonical identity package for KAFKA2306 public products. It standardizes identity, semantics, accessibility, provenance, and distribution. It does not standardize product information architecture.

## Design intent

Use a warm paper canvas, dark navy editorial text, restrained blue/lavender/rose/mint/apricot accents, thin borders, compact radii, and low-noise composition. Use typography, spacing, evidence order, and tables before adding more cards.

## Non-negotiable semantics

| State | Meaning | Required visible label |
|---|---|---|
| verified | confirmed against a named source | 確認済み / VERIFIED |
| estimated | modelled or inferred | 推定 / ESTIMATED |
| attention | requires revalidation or review | 要確認 / ATTENTION |
| rejected | explicitly rejected or failed | 棄却 / REJECTED |
| unavailable | not supplied or not computable | 利用不可 / UNAVAILABLE |

Color and icons only supplement these labels. Consumer repositories must not silently redefine their meanings.

## Information hierarchy

1. State the current decision or analytical question.
2. Show data-as-of, scope, source, and unresolved evidence.
3. Present one primary action.
4. Keep comparison, history, and raw evidence nearby but subordinate.
5. Preserve product-specific data structures and density.

## Character boundary

Kafka is an identity accent for introductions, onboarding, empty states, release notes, and occasional editorial covers. Kafka must not speak for official rules, investment conclusions, safety warnings, legal claims, numerical outputs, or destructive controls. Do not use Apache Kafka imagery.

Canonical description: long light-blue hair with a lavender gradient, blue-purple eyes, silver triangular cat hairpin, right-side braid with black ribbon, and a quiet expression. Generated or commissioned art requires provenance and approval status. Text-only and no-character fallbacks are mandatory.

## Accessibility baseline

WCAG 2.2 AA; keyboard-complete operation; visible focus; 320px reflow; 200% zoom; reduced motion; text labels for states; normal text at least 16px; persistent metadata at least 14px; controls at least 44px, or 48px for primary mobile play/participation actions.

## Performance budgets

At p75: LCP <= 2.5 s, INP <= 200 ms, CLS <= 0.1. Consumers must document the measurement environment and must not claim these budgets passed without field or controlled-lab evidence.

## Distribution

Pin an immutable release and commit. Vendor canonical files into each consumer and record SHA-256 values in `kafka-signal.lock.json`. Runtime dependencies on mutable CDN URLs are prohibited.
