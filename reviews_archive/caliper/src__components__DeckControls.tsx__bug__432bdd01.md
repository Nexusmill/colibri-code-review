# colibri bug review - src/components/DeckControls.tsx (delta)

reviewer: ZCode (GLM-5.3, in-session) - sha256 432bdd01 - 2026-08-26
mode: bug (delta on cd703d4d, 2026-08-19) - context: wells seated against the chassis map; queue/cloud/optimizer status semantics traced against queueStore, routesStore, llm/client; git 3f395f0

## Verdict

Shippable - the delta is clean.

## Fixed since last review

- [OLD, cross-file] li key={b.name} duplicate-name ambiguity: fixed in schema.ts (round one of this hunt) - name dups are now rejected at load.

## New findings

None confirmed. The cloud-run status precedence (cloud line leads, local render follows, untracked server work never reads idle), the OPTIMIZE label/title state machine across provision/download/error, the deck dropdown keyboard cursor, and SourceSelect's catalog effect (already carries the live-guard this hunt added to ModelPicker) all traced.

## Missing safeguards

- Whole-store subscription on useBundlesStore() - perf note, style-wide.
