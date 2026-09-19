<!-- source: src/stores/uiStore.ts | reviewer: glm-5.3-zai-in-session | sha256: 7fda1f62887c4bda4a647ba734cffa29e438acda32855fd0ac6429f5aeec6212 | date: 2026-09-16 | mode: bug -->
<!-- context: owner commission 2026-09-16: colibri bug hunt on the top ten files by import PageRank (the 2026-09-14 board); fresh-context subagent per file under the 0.3.0 doctrine (prior review = context, never a skip; delta files report new/changed only + close the loop; same-sha files hunt beyond the record). -->

## Verdict

Shippable — the fifth panel seat (`filmRunsOpen`) is wired symmetrically into the ruling-33 exclusivity matrix and every hand-off path (taskbar toggle, wizard/runs footers, palette verb) traces clean end to end. Two new integration defects survive refutation, both in how the now-five-seat matrix meets its consumers: a boot-time seat-guard that wasn't updated for the fifth seat, and panel-open setters that don't route to the panels' only host surface (two palette verbs already fell into that gap).

## Fixed since last review

- Prior review (4cd8e2d3 @ 2026-09-05) carried **no open findings** — nothing to close. Its shippable claims re-verified on the current file and still hold: the exclusivity matrix grew 4->5 panels and stayed symmetric (each open-branch at lines 43, 47, 51, 55, 59 closes the other four flags); every close-branch (44, 48, 52, 56, 60) touches only its own flag, so closing still never opens anything; persistence still partializes only `surface` (line 63), panels stay ephemeral.

## Bugs & vulnerabilities

**[MEDIUM] Panel-open setters never route to the panels' only host surface — settings/optimizer verbs strand invisible windows off the Generate screen** - `line 42`
- What: All five panel flags (`aiConsoleOpen`...`firstRunOpen`, lines 13-29) render exclusively inside `ScreenStage` -> `GenerateSurface` (ScreenStage.tsx:69-73, GenerateSurface.tsx:199, App.tsx:99), yet none of the opening setters (lines 42-60) set `surface: "generate"`. Every caller must remember to route by hand — and the drift already happened: palette verbs `verb-film`, `verb-film-runs`, `verb-library` (CommandPalette.tsx:42, 43, 45) and DeckControls' AI ON (DeckControls.tsx:49-50) all call `setSurface("generate")`, but `verb-settings` (CommandPalette.tsx:44) and `verb-optimize` (CommandPalette.tsx:54) do not. Both verbs shipped 2026-09-06, after the prior review.
- Trigger: From the Queue/Outputs/Bundles/Graph surface, Ctrl+K -> "Open settings" (or "Turn the optimizer AI on"). The palette dismisses and nothing appears — the flag sits `true` with the window unrendered, popping open unexpectedly only when the user later visits Generate.
- Impact: Violates the repo's standing "every button press must produce a visible result" rule; the state is the "open but unfocusable" stranding class. `verb-optimize` is worse because it is a toggle: run once from Queue (starts the llama sidecar, opens an invisible console), see nothing, run again -> the second call sees `running: true` and `llmStop()`s the brain just started.
- Fix: Put the routing where ruling 33 already lives — the store: each open-branch (42-43, 46-47, 50-51, 54-55, 58-59) also sets `surface: "generate"`. That fixes both verbs and every future caller in one place (the manual-every-callsite pattern has already drifted twice).

**[LOW] App.tsx boot seat-guard omits `filmRunsOpen` — first-run can unseat a just-opened RUNS window** - `line 21`
- What: The delta added the fifth seat (lines 21-22, 50-52) but App.tsx's boot guard — commented "unless a panel is already seated (ruling 33 - one at a time)" — still enumerates only the original four (`firstRunOpen`, `filmWizardOpen`, `settingsOpen`, `aiConsoleOpen`; App.tsx:37).
- Trigger: On a machine whose first-run record is not `done`, boot, open RUNS (taskbar key or Ctrl+K -> verb-film-runs) before the `getFirstRun()` fetch resolves; the guard then passes, calls `setFirstRunOpen(true)`, and the exclusivity at line 59 closes `filmRunsOpen`. The user's window is yanked shut milliseconds after opening. (The guard's enumeration is otherwise dead weight — all panel flags are `false` at boot since line 63 persists only `surface` — so this race is exactly what those four checks exist for.)
- Impact: Narrow (first-run machines only, boot-window race, recoverable with one click), but it defeats the guard's stated intent for one of the five seats.
- Fix: Add `!ui.filmRunsOpen` to App.tsx:37 — or better, derive both that guard and the exclusion matrix from one `PANELS` list so the next seat can't drift.

## Missing safeguards

- The one-panel matrix is five hand-maintained 5-key object literals (lines 43, 47, 51, 55, 59) plus a hand-maintained guard in App.tsx:37 — a sixth panel needs 7+ coordinated edits, and a single missed key silently seats two panels at once (ruling 33 broken with no error). No dedicated test asserts mutual exclusion across the full matrix (FilmWizard.test/FilmRuns.test cover only their own transitions).
- Nothing validates the persisted `surface` string on rehydrate (lines 62-63) — safe today because no surface id has ever been removed from the union, but a future rename would strand old localStorage on an id that renders no surface and no arcade (App.tsx:99-104); a one-line `merge` filter or `version`/`migrate` would close it.

context-pack: uiStore.ts delta 108628d (+13, the filmRunsOpen seat) — 5-panel exclusivity matrix verified symmetric; traced through ScreenStage:69-89 (render + RUNS toggle), CommandPalette:42-58 (verbs), FilmWizard:1834-1837 and FilmRuns:44-60 (pair hand-offs), App.tsx:35-41 (boot guard), GenerateSurface:199 (sole panel host); console-watchdog close race refuted via dep-equality ([llm?.running] fires only on change).
new-findings: 2
