# colibri bug review - src/stores/screenStore.ts

reviewer: ZCode (GLM-5.3, in-session) - sha256 12c274e7 - 2026-08-19T07:55:05
mode: bug - context: full-session repo knowledge (call sites traced by read; stores/surfaces/api cross-checked)

## Verdict

Shippable. Findings below survived the adversarial pass; refuted drafts were deleted.

## Bugs & vulnerabilities

- Bounds invariant traced end to end (move clamps by own footprint; resize caps at remaining space; maximize fills exactly above the taskbar and restores exact bounds). No findings.
