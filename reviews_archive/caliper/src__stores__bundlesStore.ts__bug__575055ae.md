# colibri bug review - src/stores/bundlesStore.ts (delta)

reviewer: ZCode (GLM-5.3, in-session) - sha256 575055ae - 2026-08-26
mode: bug (delta on 436cd891, 2026-08-19) - context: partialize/migrate/onRehydrate read against persisted v1->v2 storage; load/save traced against vite.caliper bundles routes and round-1's schema/constraints changes; git 0068895/e8dd8ef

## Verdict

Shippable - the delta is clean.

## Fixed/open since last review

- [OLD PLAUSIBLE, still accepted] select() with the vram node unreachable (getCaliperVram catch -> null -> no models) skips the tight-VRAM auto-unload - unchanged degradation, accepted.

## New findings

None confirmed. The paramEdits migration (only touched fields persist; factory-equal values dropped), the failed-load never-sets-loaded guard against PUTting defaults over the real file, the withIds re-validation+persist path, the selectGen race guard, and setParam's post-snap touched recording all trace correct - including against this session's interpolated snap messages.

## Missing safeguards

- Whole-store default subscription re-renders all consumers on any write (style-wide, perf note only).
