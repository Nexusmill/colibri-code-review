# colibri bug review - src/stores/queueStore.ts

reviewer: ZCode (GLM-5.3, in-session) - sha256 0aec9a4c - 2026-08-19T07:55:05
mode: bug - context: full-session repo knowledge (call sites traced by read; stores/surfaces/api cross-checked)

## Verdict

Shippable. Findings below survived the adversarial pass; refuted drafts were deleted.

## Bugs & vulnerabilities

- [LOW] Rejected jobs get synthetic id rejected-${Date.now()} (line 114) - two rejections in the same millisecond produce duplicate React keys. Fix: append a module counter.
- TOCTOU guard (queueInFlight) traced correct; provenance patch at done traced correct (executed events accumulate before the terminal executing(null)).
