# Colibri spec-conformance review

- source: E:\AI\Caliper\src\stores\bundlesStore.ts (269 lines)
- reviewer: ZCode fresh-context subagent
- sha256: 575055aee4d70777d4d34725fd034a37dc3dae6249c253d24a2d7ab7de8c1821 (sha8: 575055ae)
- date: 2026-08-31
- mode: spec (registry: E:\AI\Caliper\spec\bundles.json)
- context summary: zustand store for the bundles feature — server-file load/save with schema validation, per-bundle params/prompts with touched-only persistence (v2 storage, v1 full-map migration under key `caliper.bundles-ui`), detent snap on setParam, VRAM checks on bundle switch. Call sites verified via jcodemunch (repo local/Caliper): App.tsx (load on mount), DeckControls.tsx (picker flyout, params/prompts/fileIssues/vram UI), GenerateSurface.tsx (lastSnap toast), BundlesSurface.tsx (editor), queueStore.ts, CommandPalette.tsx, ReproduceSheet.tsx, stores.test.ts (snap/cfg-latch/migration/persistence-key/save-refusal tests). schema.ts (validateBundles, withIds, defaultBundles) and constraints.ts (parseDetent, snapToDetent, snapMessage) read for ground truth.

## Verdict

PASS WITH ONE DIVERGENCE. All seven registry clauses are satisfied at the store layer except BND-VALIDATE-LOAD-AND-SAVE's "never silently repaired" term, which the missing-id migration path on load() contradicts by silently repairing the server file and PUTting it back. The quiet clauses (migration boundary, storage key, per-bundle prompts) were traced end-to-end and hold.

## Divergences

### 1. A schema-invalid bundle file (missing ids) is silently repaired and rewritten on load, not refused with a visible message

- Clause (BND-VALIDATE-LOAD-AND-SAVE, verbatim): `"bundles.json passes schema validation at load and again at every save: ids required and unique, frame detents parseable; an invalid file is refused with a visible message, never silently repaired or half-loaded."`
- Expectation: a bundles.json that fails validation — and per the schema, a bundle without an id fails (`schema.ts:76` `if (!str(b?.id)) issues.push({ bundle: n, field: "id", message: "Id is required." })`) — must be refused with a visible message; the file on the server must not be rewritten without the refusal being seen.
- Trigger: server bundles.json in the older no-id format. `load()` (bundlesStore.ts:110) runs `validateBundles(incoming)`; it returns not-ok ("Id is required"). Lines 113-119 then take exactly that failed file: `if (checked && !checked.ok && Array.isArray(...))` → `withIds(...)` assigns ids from names → re-validate → on success `void fetch("/api/bundles", { method: "PUT", ... })` (line 117) rewrites the server file, fire-and-forget, and lines 120-132 load the repaired list with `fileIssues` untouched (empty) and `loaded: true`.
- Behavior: an invalid file was silently repaired AND persisted back to the server with no visible message and no user click on any write control. Guard check: the repair is narrowly scoped (withIds only adds ids; any other invalidity — duplicate name, bad detent — still fails re-validation and lands in the else branch at line 136 with `fileIssues` set), deterministic on re-run (ids re-derived from names identically), and the code comments (lines 111-112, schema.ts:24, 47-51) frame it as a deliberate format migration. But the clause text has no migration carve-out: "never silently repaired" is categorical.
- Fix: either amend the spec clause to sanction the id-backfill migration explicitly, or surface it — e.g. set `fileIssues` (or a dedicated note) to `"Assigned missing bundle ids and saved the migrated file."` before/after the PUT so the repair is visible, matching the clause's refusal-with-message contract for everything else.
- CONFIRMED (code path re-read at lines 110-137; schema ground truth at schema.ts:76 and 52-64; no fileIssues write exists on the success branch; the PUT is unconditional once the repaired list validates).

## UNJUDGEABLE HERE

- BND-EDITOR-SURFACE (table listing, Files column, per-bundle file state, Save control): owned by `src/surfaces/BundlesSurface.tsx` — the store only supplies `bundles`, `fileIssues`, and `save()`.
- BND-SWITCH-ACTIVE, picker flyout behavior and the picker's face showing the chosen name: the store's half (`select` sets `selected` immediately, bundlesStore.ts:174-176) is satisfied; the flyout UI is owned by `src/components/DeckControls.tsx` (`SourceSelect ... onSelect={(name) => useBundlesStore.getState().select(name)}`, DeckControls.tsx:223).
- BND-FILE-DEFAULTS-SHOWN, the steppers display: the store rebuilds params from file defaults plus touched-only overlay on load (bundlesStore.ts:122-127) and save (line 166), so no cross-bundle residue exists at the data layer; what the steppers render is the Generate deck's territory (`src/components/DeckControls.tsx`, `src/surfaces/GenerateSurface.tsx`).
- BND-FRAME-DETENT-SNAP, message display: the store snaps and records `lastSnap` with the naming message (bundlesStore.ts:219-239; message text "Frames must be 8n+1. Snapped to 89." unit-asserted at stores.test.ts:46); the 4-second correction toast is owned by `src/surfaces/GenerateSurface.tsx` (lines 40-44). The boundary half (unparseable detents refused at schema) is owned by `src/bundles/schema.ts:93-98`.
- BND-VALIDATE-LOAD-AND-SAVE, the validation rules themselves (ids required/unique, detents parseable) and the rendering of `fileIssues`/save issues to the user: owned by `src/bundles/schema.ts` and by `src/components/DeckControls.tsx` / `src/surfaces/BundlesSurface.tsx` respectively. The store's error-path mechanics (save refuses while `loaded` is false, returns issues without any fetch when validation fails — bundlesStore.ts:141-156) match the clause's "writes nothing" term.

Satisfied clauses (silence per protocol): BND-TOUCHED-ONLY-PERSISTENCE in full — storage key is exactly `caliper.bundles-ui` (line 255) with no other storage writes in this file; touched params persist via `paramEdits` (partialize line 259, rehydrate lines 261-268, overlay lines 127/166); untouched params follow the file; the v1 full-map migration (lines 68-81) turns a factory-valued v1 store into empty `paramEdits` so file defaults show after reload, keeps any field differing from factory (no data loss), and cannot crash (unit-tested at stores.test.ts:389-394). BND-PROMPT-PER-BUNDLE: prompts keyed per bundle name, persisted, preserved across load (line 128) and save (line 167).
