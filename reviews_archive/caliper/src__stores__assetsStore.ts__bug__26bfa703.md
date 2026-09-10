# colibri bug review - src/stores/assetsStore.ts

reviewer: ZCode (GLM-5.3, in-session) - sha256 26bfa703 - 2026-08-19T07:55:05
mode: bug - context: full-session repo knowledge (call sites traced by read; stores/surfaces/api cross-checked)

## Verdict

Shippable. Findings below survived the adversarial pass; refuted drafts were deleted.

## Bugs & vulnerabilities

- [MEDIUM-LOW] hydrate() marks a record hydrated BEFORE its history fetch resolves - a transient server-away (fetch catch -> null) permanently hides that asset from the library; it is never retried. Fix: only mark hydrated when the record carried outputs or history answered.
