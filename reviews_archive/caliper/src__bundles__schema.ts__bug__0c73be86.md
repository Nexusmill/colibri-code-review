# colibri bug review - src/bundles/schema.ts (delta)

reviewer: ZCode (GLM-5.3, in-session) - sha256 0c73be86 - 2026-08-25
mode: bug (delta on ce745711, 2026-08-19) - context: 17 importers enumerated via jcodemunch (bundlesStore, fill.ts, vite.caliper save-side validation, DeckControls, surfaces), git 47ccaa6/110acee (the colibri-fix + hardening era)

## Verdict

Shippable - no new defects; the file remains the repo's most-depended-on contract and it holds.

## Fixed since last review

- [OLD MEDIUM] Duplicate display names passed validation: FIXED - lines 108-113 now reject duplicate names alongside ids, with the name-keyed-state rationale in a comment.

## New findings

None confirmed. The detent-validation addition (parseDetent as single source of truth, k>0 enforced) traces correct against constraints.ts and the schema.test.ts suite.

## Missing safeguards

- defaults numerics are only typeof-checked at file level (NaN/0/negative pass validateBundles); runtime violations() backstops NaN and <=0 for live params, so a bad hand-edited bundles.json surfaces at generate time, not load time.
