# Colibri review — src/stores/screenStore.ts (feature)

- **Source:** `src/stores/screenStore.ts` · **sha256:** 33d0507d
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** 8 importers (CloudPane, FilmWizard, ModelPicker, ReproduceSheet, ScreenStage, OutputsSurface); FEATURES.md `screen-*`/`library-*` rows (draggable/resizable/z-ordered windows, persistent geometry, reload-restore); ruling 40 (the press carries you to its window); last touch 82ff326 (2026-08-31).

## What this module does

The window-manager OS's state: asset windows (open-focuses-existing, cascade placement, clamped move/resize inside the fixed stage, min/max with restore memory, shared z-order), the library as a first-class window (geometry + z seat + scope), the Reproduce formula-sheet payload, and the auto-open memory (`openedJobs`, capped at 49, where CLOSING a window marks its job seen so boot never resurrects what the user dismissed). Everything persists under `caliper.screen` — reload starts exactly where you left, and a closed window stays closed. `openAsset(a, reveal)` implements ruling 40: a press from off-stage carries the user to the render screen; machine auto-opens never reveal.

## Suggested add-ons

**A one-key window organizer (tile/cascade)** — Value Low-Med · Effort S
- What: a taskbar key that re-tiles all open windows into a grid (or re-cascades them) inside the stage bounds.
- Why: with several assets open, manual arrangement is the only option; the move/resize clamps and geometry memory make a deterministic layout trivial to compute from existing state.
- How: one action iterating `windows` assigning the tile rects the clamps already enforce. NOTE: keyboard-behavior add-on, but it creates visible layout motion — needs the owner's explicit commission under the no-visual-changes rule.

**Selection in the store (optional)** — Value Low · Effort S
- What: the Library's selection Set currently lives in component state (ScreenStage.tsx:528) — ephemeral by design ("crossing the rail starts a new page honestly"). If a future feature needs selection to survive minimize (the library stays mounted, so it already does) or feed other windows, lift it here — until then, correctly left alone.

## Nice-to-haves

- `topZ` grows unboundedly across a session; a compaction on close would keep persisted numbers small. Cosmetic, no behavior effect.

## Notes

- The fixed stage constants (SCREEN_W 990 etc.) mirror the chassis art's measured glass — do not touch without commission; all geometry math already respects them.
