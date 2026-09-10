# Colibri review — src/bundles/constraints.ts (feature)

- **Source:** `src/bundles/constraints.ts` · **sha256:** 01434323
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** 8 importers (schema.ts, DeckControls, ScrubInput, bundlesStore, queueStore, GenerateSurface, fill.ts); FEATURES.md rows `stepper-detent`, `steppers-show-defaults`; last touch 410494c (2026-08-25).

## What this module does

The bundle parameter-constraint vocabulary: the detent grammar (`kn+c` parsed by regex, snapped by `snapToDetent`), the CFG cap (`cfgMax`/`cfgPinned` with the override latch), `violations()` (frames detent, CFG ceiling, positive-number sweep), and `snapMessage` (the user-facing correction text the deck shows for 4s). 62 lines, pure functions, exercised directly by tests.

## Suggested add-ons

**Generalized per-field constraints: dimension multiples and step bounds** — Value High · Effort M
- What: extend the constraint vocabulary so a bundle can declare `width_step`/`height_step` (multiples, e.g. 32 or 64 for the LTX/Qwen VAEs) and `steps_min`/`steps_max` bounds; `violations()` checks them and `setParam` snaps them with `snapMessage` text, exactly like frames.
- Why (verified): `violations()` (constraints.ts:43-56) checks only the frames detent, the CFG cap, and positivity — and GenerateSurface.tsx:119-128 lets the user type ANY width/height from 64 to 4096 with no multiple enforcement anywhere between the deck and the engine. A 777-wide frame on a VAE that quantizes to multiples silently wastes a whole render. The turbo models also have real step-count ceilings that today nothing expresses.
- How: `BundleConstraints` gains the fields (validated at load beside `constraints.frames`, schema.ts:96-98); `violations()` grows the checks; `bundlesStore.setParam` snaps post-patch like frames (bundlesStore.ts:220-227); `snapMessage`'s field union widens. Callers verified: every consumer reads `violations`/`snapToDetent` generically — no call-site breakage.

**A `detentInfo` helper for UI hints** — Value Low · Effort S
- What: one function returning `{k, c, min, max}` for a field so Stepper/slider components never re-derive `detent?.k ?? 8` fallbacks (GenerateSurface repeats that ternary four times).
- Why: the fallback constants live in the consumer; the grammar's owner should publish them.

## Nice-to-haves

- `seed` range validation — positivity is skipped for seed today; ComfyUI seeds have practical bounds and the UI caps at 2^47 while `randomSeed()` generates 48-bit values. Cosmetic until an engine rejects one.

## Notes

- The module is deliberately tiny and pure; both add-ons extend the existing pattern rather than replacing it.
