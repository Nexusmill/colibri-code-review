# colibri bug review - src/components/MediaView.tsx

reviewer: ZCode (GLM-5.3, in-session) - sha256 ad840b10 - 2026-08-19T07:55:05
mode: bug - context: full-session repo knowledge (call sites traced by read; stores/surfaces/api cross-checked)

## Verdict

Shippable. Findings below survived the adversarial pass; refuted drafts were deleted.

## Bugs & vulnerabilities

- [LOW] Image wins over video when a render emits both - no current bundle does; noted for future multi-output bundles.
