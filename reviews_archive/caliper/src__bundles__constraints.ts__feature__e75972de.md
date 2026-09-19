# Colibri review — src/bundles/constraints.ts (feature)

- **Source:** `src/bundles/constraints.ts` · **sha256:** e75972de
- **Reviewer:** ZCode (GLM-5.3, in-session) · **Date:** 2026-09-14 · **Mode:** feature (DELTA vs 01434323 @ 2026-09-05)
- **Context pack:** 8 importers (schema, DeckControls, ScrubInput, bundlesStore, queueStore, GenerateSurface, fill.ts); delta = e7bc621 (+73); FEATURES `stepper-detent`, `steppers-show-defaults`; full current read.

## What this module does

The bundle parameter-constraint engine, now the full vocabulary: detent grammar + `widthMultiple`/`heightMultiple`/`framesMax`/`stepsBounds` accessors (absent = old-UI fallback, with the detent-landed frames cap and the "no law" open steps max), `snapToMultiple` (never below one grid unit), `coerceParams` (the spoken snap applied per-edit and to persisted touched params at load), `violations` (frames detent + ceiling, CFG cap, both grids, steps bounds, positivity sweep), and the widened `snapMessage` (frames/cfg/width/height/steps with VAE-grid wording).

## Fixed since last review

- Generalized per-field constraints (the 2026-09-05 High) → BUILT by e7bc621 end to end (schema keys, accessors, violations, snap message).
- `detentInfo` helper → absorbed: the accessors publish the fallbacks (widthMultiple etc.), consumers no longer re-derive.

## Suggested add-ons

**Seed bounds in the vocabulary** — Value Low · Effort S (CARRIED, sharpened)
- What: `seed_max` (and positivity for seed, which `violations` explicitly skips at line ~118 `k !== "seed"`).
- Why (verified): the prior review's note stands — the UI caps seeds at 2^47 while `randomSeed()` generates 48-bit values; nothing between deck and engine reconciles the two.
- How: constraint key + accessor + one violations line; snap message unwritten (seed changes silently by design — LOCK SEED speaks instead).

**fps as a bounded field** — Value Low · Effort S
- What: `fps_min`/`fps_max` (or a fixed enum) — ParamState carries fps and nothing constrains it; LTX video+audio cares about fps alignment with the audio track.
- Why: the vocabulary now bounds every OTHER numeric; fps is the last free number a hand-edit can set to something the engine rejects (0, 1, 1000).
- How: same pattern as steps bounds; a fixed default (24/30 enum) needs no UI work.

## Nice-to-haves

- None — the module is deliberately tiny and the spree completed its agenda; both add-ons are the same pattern extended.
