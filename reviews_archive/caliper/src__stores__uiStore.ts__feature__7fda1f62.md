# Colibri review — src/stores/uiStore.ts (feature)

- **Source:** `src/stores/uiStore.ts` · **sha256:** 7fda1f62
- **Reviewer:** ZCode (GLM-5.3, in-session) · **Date:** 2026-09-14 · **Mode:** feature (DELTA vs 4cd8e2d3 @ 2026-09-05)
- **Context pack:** 17+ importers (every chassis component + screenStore + the Era-57 window pair); delta = 108628d (+13, the filmRunsOpen seat); ruling 33 (one panel at a time, panels ephemeral, closing never opens); full current read (64 lines).

## What this module does

The chassis navigation truth: the five-surface enum (persisted — reload lands where you left), the palette flag, and now FIVE console panels (aiConsole, filmWizard, filmRuns, settings, firstRun) whose setters implement ruling 33 mechanically — opening one closes every other; closing opens nothing; only `surface` persists (partialize). The Era-57 delta added the YOUR RUNS seat to the same matrix.

## Fixed since last review

- Palette hotkey legend (Low·S) → BUILT by E-6 (palette verbs + hotkey legend).
- Panel-open persistence → correctly STILL absent (ruling 33's design; the prior review recorded it so the suggestion dies on arrival — reaffirmed).

## Suggested add-ons

**Derive the one-panel matrix from a single PANELS list** — Value Low · Effort S
- What: one `PANEL_KEYS = [...]` constant; each setter builds its close-others object from it (`Object.fromEntries(PANEL_KEYS.map(k => [k, false]))` + its own true).
- Why (verified): the matrix is hand-maintained five times now (lines 43-62) — each setter lists the other four by name; the sixth panel will need five coordinated edits and a miss silently breaks ruling 33 (two panels open). One list makes the ruling structurally unbreakable.
- How: ~8 lines, pure refactor inside the store; zero observable behavior; the uiStore setter-enforcement tests (ruling 33, shipped at the store setters) still pass untouched.

## Nice-to-haves

- None that don't touch the settled chassis.
