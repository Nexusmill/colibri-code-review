# Colibri review — src/bundles/schema.ts (feature)

- **Source:** `src/bundles/schema.ts` · **sha256:** d0cc311e (full sha in manifest)
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** 18 importers (bundlesStore, queueStore, DeckControls, AdvancedDrawer, ReproduceSheet, BundlesSurface, fill.ts, vite.caliper, vite.agent); FEATURES.md rows `bundles-*`; prior bug-mode reviews at this sha family; last touch e3a2c03 (2026-09-05).

## What this module does

The bundle type system and its single gate. `validateBundles` runs at load AND save (client and server both call it), enforcing required+unique ids, unique names (params/prompts/selection all key by name), per-field shape, and detent-string usability. `withIds` migrates legacy id-less files at load and persists the migration so renames can't re-derive ids. `defaultBundles` carries the four factory bundles (LTX-2.3-Distilled video, Anima-Aesthetic, Krea-2-Turbo, Anima-Turbo images).

## Suggested add-ons

**Constraint ceilings in the schema (frames_max and friends)** — Value High · Effort S
- What: move the `FRAMES_MAX = 521` ceiling out of GenerateSurface (its own comment at src/surfaces/GenerateSurface.tsx:23 says "Belongs in the bundle schema; here until it gets there") into `BundleConstraints` as optional `frames_max`, and let the Stepper/slider max read it.
- Why: today the ceiling is UI-local — the Bundles editor and the AdvancedDrawer never see it, and a bundle whose engine allows more (or less) than 521 frames cannot express that.
- How: add `frames_max?: number` to `BundleConstraints` (schema.ts:17), validate `> 0` beside `cfg_max` (schema.ts:99), read it in GenerateSurface:115-116 with 521 as the fallback default.

**Bundle definition export/import** — Value Med · Effort S
- What: export one bundle row as a JSON file; import merges via `withIds` id-uniqueness and the existing `validateBundles` gate before save.
- Why: bundles.json is machine-local (tuned negatives, defaults, constraints); moving a tuned bundle between machines today means hand-editing JSON. `validateBundles` is already exactly the right validator for an imported blob.
- How: a row action in BundlesSurface → `JSON.stringify(bundle)`; import path: parse → `withIds([incoming])` → `validateBundles` → append → `save()`. Verified absent: no export/import exists in BundlesSurface (search: only the `export function` declaration matches).

**Lora strength in the bundle** — Value Med · Effort S-M
- What: let a bundle carry per-lora strength (`loras: string[]` stays, plus optional `loraStrength: Record<string, number>` or a parallel object list migrated by a `withIds`-style backfill).
- Why: fill.ts:106 hardcodes `strength_model: 1` for every lora — Anima-Turbo's turbo lora is permanently pinned at full strength with no way to dial it down from the instrument.
- How: schema field + validation (0 < strength ≤ 2), `fill.ts` LoraLoaderModelOnly inputs read it, AdvancedDrawer exposes it. Callers verified: only fill.ts builds LoraLoader nodes.

## Nice-to-haves

- `hidden?: boolean` on Bundle — keep an experimental bundle out of the deck dropdown without deleting it (factory rows can't be deleted today).
- A `version` stamp on `BundlesFile` — no file-level migration hook exists; `withIds` is the only migration and future constraint-vocabulary growth (see constraints.ts review) will want one.

## Notes

- Verified non-gaps: file-presence display is already covered by the install catalog's Files column (`install-catalog` manifest row); duplicate-name refusal is a shipped feature (`bundles-validation`).
