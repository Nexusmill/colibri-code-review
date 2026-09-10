# colibri bug review - src/surfaces/OutputsSurface.tsx

reviewer: ZCode (GLM-5.3, in-session) - sha256 badb9f63 - 2026-08-19T07:55:05
mode: bug - context: full-session repo knowledge (call sites traced by read; stores/surfaces/api cross-checked)

## Verdict

Shippable. Findings below survived the adversarial pass; refuted drafts were deleted.

## Bugs & vulnerabilities

- No new findings (hydration now in assetsStore; the once-per-id semantics moved with it).
