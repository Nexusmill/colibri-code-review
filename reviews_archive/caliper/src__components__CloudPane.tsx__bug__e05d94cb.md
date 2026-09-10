# colibri bug review - src/components/CloudPane.tsx

reviewer: ZCode (GLM-5.3, in-session) - sha256 e05d94cb - 2026-08-27
mode: bug - context: GenerateSurface seats it keyed by service:slug (remount, no stale-catalog race); ModelPicker's round-2 enum fix is the sibling contract

## Verdict

Shippable after the one fix below.

## Fixed since this review (same session)

- [MEDIUM] The default-seeding loop lacked the enum[0] fallback (round 2's ModelPicker defect class): a required enum with no schema default RENDERED its first option while values[k] stayed undefined - the field sat in the missing list with the form looking complete (the idle line names it, but the select looks filled). FIX: enum[0] seeded when no default exists; the shown value is the sent value.

## Verified-correct

- loadModel catalog-then-direct-schema; run dispatch per service; makeDefault + refresh; artifact open; the pinned/advanced field split (required + image-format leads).
