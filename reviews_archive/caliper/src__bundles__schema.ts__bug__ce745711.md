# colibri bug review - src/bundles/schema.ts

reviewer: ZCode (GLM-5.3, in-session) - sha256 ce745711 - 2026-08-19T07:55:05
mode: bug - context: full-session repo knowledge (call sites traced by read; stores/surfaces/api cross-checked)

## Verdict

Shippable. Findings below survived the adversarial pass; refuted drafts were deleted.

## Bugs & vulnerabilities

- [MEDIUM] Duplicate display NAMES pass validation (only ids are uniqueness-checked) while params/prompts/selected/editingKey/remove/picker-keys are all NAME-keyed - two same-named bundles silently share parameters and ambiguate every by-name operation. Fix: reject duplicate names like duplicate ids.
