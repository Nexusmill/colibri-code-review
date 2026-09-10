# Spec-conformance review — BundlesSurface.tsx

- Source: E:\AI\Caliper\src\surfaces\BundlesSurface.tsx (334 lines)
- Reviewer: ZCode fresh-context subagent
- SHA-256: fbcd3d339c8ffd4e793610b89efefeba6d0c7f01661529981008cc47a3e66305
- Date: 2026-08-31
- Mode: spec conformance (registry: E:\AI\Caliper\spec\bundles.json)
- Context: This surface owns the bundles table with its Files column (per-bundle
  file state + install affordances), the editor modal with the Save control,
  the curated add-from-catalog flow, and the surface-visible halves of
  validation refusal (fileIssues banner, editor save message).

## Verdict

PASS WITH ONE DIVERGENCE. Of the seven registry clauses, two are judgeable in
this file: BND-EDITOR-SURFACE is satisfied (table with Files column showing
per-bundle install state, Save control in the editor), and
BND-VALIDATE-LOAD-AND-SAVE is satisfied on the editor-save path (duplicate-name
save surfaces the message at line 128, editor stays open, nothing written) but
violated on the curated-add path, where a refused save is swallowed with no
visible result. Five clauses are owned by other files (see UNJUDGEABLE HERE).

## Divergences

### 1. Curated-add discards a refused save with no visible message (remove shares the shape)

- Expectation (BND-VALIDATE-LOAD-AND-SAVE, error_paths, quoted verbatim):
  "a save whose edits break the schema (e.g. a duplicate bundle name) surfaces
  the validation message on save and writes nothing."
- Trigger: Clicking Install in the Add-model selector for a render bundle whose
  addition is refused by store.save. Two traced triggers:
  (a) Schema-break: a bundle in the table already carries the template's NAME
  under a different id, so `bundles.some((b) => b.id === id)` (line 48) passes
  and `save([...bundles, structuredClone(template)])` fails validateBundles
  with `Duplicate bundle name "..."` (src/bundles/schema.ts:101-112). UI-only
  sequence to reach it: rename the catalog template (id is immutable), create a
  custom bundle under the template's old name (withIds derives a `-2` id,
  src/bundles/schema.ts:52-64), remove the renamed original, then add the
  template from the catalog. Contrived but real.
  (b) Store never loaded (middleware down at startup): store.save returns
  "The bundle file never loaded from the server; refusing to overwrite it."
  (src/stores/bundlesStore.ts:141-143) on every catalog Install — a much more
  reachable trigger.
- Behavior: `addFromCatalog` (lines 46-54) hits `if (problems.length > 0)
  return` and discards the ValidationIssue[]. No setIssues (the `issues` state
  only renders inside the editor modal, line 128, which this flow never opens),
  no fileIssues set (store.save returns validation issues without touching
  state, src/stores/bundlesStore.ts:146), and the selector modal closes via
  `setOpen(false)` right after `onAdd` (line 218). Net effect: a click that
  produces zero visible result. The "writes nothing" half of the clause IS
  honored (return happens before startInstall; the store validates before the
  PUT). `remove` (lines 72-74) has the same shape — it discards save problems
  such as "Could not reach the bundle API" (network down mid-session leaves the
  row in the table with no message), though removal edits cannot themselves
  break the schema, so that instance sits at the clause's edge.
- Fix: In `addFromCatalog`, surface refused problems the way the editor does —
  e.g. promote a per-surface message region (or reuse fileIssues-style banner)
  rendering `problems.map(p => ...)` when `problems.length > 0`, and keep the
  selector open (or reopen it) instead of closing on a refused add. Give
  `remove` the same treatment for its discarded issues.
- CONFIRMED — code path re-opened and traced end to end (surface lines 46-54
  and 214-220; store save refusal paths at bundlesStore.ts:141-143 and :146;
  schema duplicate-name issue at schema.ts:111; the editor's `issues` state
  confirmed unreachable outside the editing modal). Trigger (a) verified
  reachable through the UI alone but contrived; trigger (b) is the common-case
  reachable path.

## UNJUDGEABLE HERE

- BND-VALIDATE-LOAD-AND-SAVE, "expected" half (schema validation at load AND
  save; ids required + unique; detents parseable; invalid file never silently
  repaired or half-loaded): owned by src/bundles/schema.ts (validateBundles,
  withIds) and src/stores/bundlesStore.ts (load/save orchestration, the
  loaded-flag refusal, the withIds id-migration PUT). Only the surface-visible
  halves were judged here: the fileIssues banner (lines 79-81, present) and the
  editor save message (line 128, present).
- BND-SWITCH-ACTIVE (picker flyout switches active bundle; face shows the
  name): owned by src/components/DeckControls.tsx — SourceSelect at lines
  223/233 calls `useBundlesStore.getState().select(name)`. The ModelSelector
  in this file is an add-model catalog picker, not the active-bundle picker.
- BND-FILE-DEFAULTS-SHOWN (steppers show file defaults on bundle load): owned
  by src/stores/bundlesStore.ts (initParams / load overlay of paramEdits) and
  src/surfaces/GenerateSurface.tsx (stepper rendering).
- BND-FRAME-DETENT-SNAP (snap + correction message; unparseable detents
  refused at schema, not a render crash): owned by
  src/surfaces/GenerateSurface.tsx (frames Stepper/OrnateSlider),
  src/components/Stepper.tsx, src/stores/bundlesStore.ts (setParam snap +
  lastSnap message), and src/bundles/schema.ts (parseDetent refusal, boundary
  clause). This file renders no frames values.
- BND-TOUCHED-ONLY-PERSISTENCE (touched-only persistence; storage key
  caliper.bundles-ui and nowhere else; v1 migration): owned by
  src/stores/bundlesStore.ts (persist name "caliper.bundles-ui", partialize,
  migratePersisted). BundlesSurface.tsx contains no localStorage access —
  verified, no direct storage writes leak from this file.
- BND-PROMPT-PER-BUNDLE (prompts survive switch/reload, swap with bundle):
  owned by src/surfaces/GenerateSurface.tsx (setPrompt textarea) and
  src/stores/bundlesStore.ts (prompts map + load/save preservation).
