# Colibri review — src/bundles/schema.ts (feature)

- **Source:** `src/bundles/schema.ts` · **sha256:** 33e6a4f4
- **Reviewer:** ZCode (GLM-5.3, in-session) · **Date:** 2026-09-14 · **Mode:** feature (DELTA vs d0cc311e @ 2026-09-05)
- **Context pack:** #1 file by import PageRank (validateBundles, 16 in-degrees); importers bundlesStore/queueStore/DeckControls/AdvancedDrawer/ReproduceSheet/BundlesSurface/fill.ts/vite.caliper/vite.agent; delta = e7bc621 (Theme C, +169); FEATURES rows `bundles-*`, `stepper-detent`; full current read 1-160 + outline.

## What this module does

The bundle type system and its single load-and-save gate, now carrying the full constraint vocabulary: VAE grids (`width_multiple`/`height_multiple` with the never-invalidating `withFactoryConstraints` adoption), `frames_max` (migrated out of the UI), step bounds, `size_presets` (grid-validated at load), and `lora_strength` (absent = 1). `withIds` still migrates legacy id-less files; `defaultBundles` is the factory truth the adoption reads.

## Fixed since last review (all three 2026-09-05 add-ons BUILT by e7bc621)

- Constraint ceilings in the schema → `frames_max` + steps bounds + multiples live in `BundleConstraints` (schema.ts:17-32), validated at load.
- Lora strength in the bundle → `lora_strength?: number` (schema.ts:46-47) with the fill.ts comment trail.
- The `version` stamp nice-to-have → addressed in spirit by `withFactoryConstraints`' adoption-only-when-valid migration (no stamp, but the migration can no longer invalidate; see add-on 2 for the remaining half).

## Suggested add-ons

**Bundle export/import through the existing gate** — Value Med · Effort S (CARRIED, still unbuilt)
- What: export one bundle row as JSON; import parses → `withIds([incoming])` → `validateBundles` → append → save.
- Why: bundles.json stays machine-local; the tuned constraints vocabulary (grids, presets, lora strength) is now the product of real tuning — hand-copying JSON between machines is the only path.
- How: row action in BundlesSurface; the validator is already exactly the right gate. Verified absent (no export path in BundlesSurface).

**A migrations stamp on BundlesFile** — Value Low-Med · Effort S
- What: `migrations?: string[]` recording which load-time migrations ran ("ids", "factory-constraints:2026-09-05"); withIds/withFactoryConstraints append once.
- Why: two never-invalidating migrations exist and persist blindly (return added/merged; callers re-run every load); a third is likely (vocabulary keeps growing) and a stamp makes the file self-describing + lets future migrations skip settled work.
- How: field + validation (array of strings); the two migration functions append their key when they change a row.

**Width/height minimums in the vocabulary** — Value Low · Effort S-M
- What: `width_min`/`height_min` (VAEs and engines have real floors); `violations()` checks, `coerceParams` floors like frames_max.
- Why: today the only floor is `snapToMultiple`'s "never below one multiple" (constraints.ts:71-73) — a 32px width is legal and renders a stamp.
- How: mirror frames_max through CONSTRAINT_KEYS, the accessor, violations, coerceParams.

## Nice-to-haves

- Per-lora strength map (chain-wide number today) — only if a real bundle ever carries two loras; none does.
