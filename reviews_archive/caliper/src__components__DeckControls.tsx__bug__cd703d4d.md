# colibri bug review - src/components/DeckControls.tsx

reviewer: ZCode (GLM-5.3, in-session) - sha256 cd703d4d - 2026-08-19T07:55:05
mode: bug - context: full-session repo knowledge (call sites traced by read; stores/surfaces/api cross-checked)

## Verdict

Shippable. Findings below survived the adversarial pass; refuted drafts were deleted.

## Bugs & vulnerabilities

- No new findings. li key={b.name} inherits the duplicate-name ambiguity (see schema.ts finding) - fixed there.
