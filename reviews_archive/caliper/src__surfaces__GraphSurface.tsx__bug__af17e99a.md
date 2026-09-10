# colibri bug review - src/surfaces/GraphSurface.tsx

reviewer: ZCode (GLM-5.3, in-session) - sha256 af17e99a - 2026-08-19T07:55:05
mode: bug - context: full-session repo knowledge (call sites traced by read; stores/surfaces/api cross-checked)

## Verdict

Shippable. Findings below survived the adversarial pass; refuted drafts were deleted.

## Bugs & vulnerabilities

- [PLAUSIBLE] Mount-time seedAll can run before load() resolves and seed graphs from factory defaults (unverified race; graphs are mirrors and force-reseed exists).
- First-visit-only seeding and boot-mirror logic traced correct.
