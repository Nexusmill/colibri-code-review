# Spec review — src/stores/screenStore.ts

- source: E:\AI\Caliper\src\stores\screenStore.ts (225 lines)
- reviewer: ZCode fresh-context subagent
- sha: 408e1830bcebec09d8963aebbdcbbb941fd028b812f081fab8dd5dfe2e2dd958
- date: 2026-08-31
- mode: spec (registry: E:\AI\Caliper\spec\screen-os.json, 6 controls, all PROVISIONAL)
- context: zustand store for the render-screen OS — asset windows (geometry, z,
  min/max/restore), the library window, the reproduce sheet, job auto-open
  memory, persisted under key `caliper.screen` via zustand/persist
  (partialize, screenStore.ts:217-224). Judgeable here: SCR-WINDOW-CONTROLS
  (store half), SCR-RELOAD-RESTORE. The other four clauses are owned by
  components (see UNJUDGEABLE HERE). Evidence: screenStore.test.ts (14 tests,
  read in full), ScreenStage.tsx, uiStore.ts, DeckControls.tsx, FilmWizard.tsx
  call sites via jcodemunch (index refreshed incremental 2026-08-31 before the
  panel trace).

## Verdict

PASS WITH ONE DIVERGENCE. The persistence key is exactly `caliper.screen`
(screenStore.ts:218, matching the registry side-effect and AGENTS.md); windows,
their geometry, z-seats and topZ persist wholesale (partialize :223, which
includes each window's `maximized` and `restore`); the active tab persists
under `caliper.ui` in uiStore.ts:37-38 (partialize surface only) — the
store-side halves of SCR-WINDOW-CONTROLS (close/toggleMinimize/toggleMaximize
do their named things, tests :37-47 and :129-144) are satisfied. The
closed-stays-closed quiet half holds: `close` (:155-164) marks the window's
promptId seen in persisted `openedJobs`, and the only boot auto-open path,
ScreenStage.tsx:50, goes through `openJobOutputs`, whose :149 guard
(`openedJobs.includes(promptId)`) blocks resurrection. One CONFIRMED
low-severity gap in the same quiet clause: the library window's maximized
state and restore slot are not persisted.

## Divergences

### 1. SCR-RELOAD-RESTORE — library maximize state and restore slot do not survive reload (CONFIRMED, low severity)

- **Expectation (violated clause, quoted):** "Open windows and the active tab
  survive reload; a window closed before reload stays closed after it." with
  side effect "persistence keys: the active tab under caliper.ui; screen
  windows and their geometry under caliper.screen."
- **Trigger:** Maximize the library (toggleLibraryMax, screenStore.ts:199-207
  sets libraryMax=true, libraryRestore=pre-max geometry, libraryGeo=full
  screen), then reload, then click the library's maximize/restore button.
- **Behavior:** partialize (:223) persists `libraryGeo`, `libraryZ`,
  `libraryMin`, `libraryOpen` — but NOT `libraryMax` and NOT
  `libraryRestore`. After reload libraryMax rehydrates to its default false
  and libraryRestore to undefined, while libraryGeo rehydrates as the
  full-screen numbers. The next toggleLibraryMax (else branch, :204-205)
  then saves the already-full-screen geometry as the restore target, so the
  pre-maximize geometry (e.g. {120,40,600,300} from the test at
  screenStore.test.ts:111-119) is irrecoverable — "maximize ... remembers
  the window's place" (:179-180) silently breaks for the library only. This
  is asymmetric with asset windows, whose whole object — `maximized` AND
  `restore` — persists inside `windows`, and with `libraryMin`, which IS
  persisted; the asymmetry is evidence of an oversight, not intent. The
  store's own comment (:65-68) declares the library "a window of the OS like
  any asset window", bringing it under "screen windows and their geometry".
  No test covers rehydration of libraryMax (the persist tests only read
  localStorage for libraryView :71-74 and libraryFolder/Geo :121-127).
- **Fix:** Add `libraryMax: s.libraryMax, libraryRestore: s.libraryRestore`
  to the partialize object at screenStore.ts:223.
- **CONFIRMED** — fully derivable inside this file (partialize list vs
  toggleLibraryMax logic); re-traced the trigger end to end; no guard
  elsewhere restores the flag (ScreenStage/Taskbar only read these fields).

## UNJUDGEABLE HERE

Behavior owned by other files; noted with observed evidence so their reviews
can consume it.

1. **SCR-PANELS-IN-PLACE — "Panels open IN PLACE, stay until closed, and only
   one is open at a time."** Owner: **src/stores/uiStore.ts** (the three
   independent booleans) and **src/components/ScreenStage.tsx** (the
   open/close call sites). screenStore.ts holds nothing about these panels.
   The directed trace of
   setAiConsoleOpen/setFilmWizardOpen/setSettingsOpen found:
   - uiStore.ts:30-35 — three plain setters, NO mutual exclusion in the
     store (confirmed: opening one never closes the others at the store
     layer).
   - ScreenStage.tsx:62-64 — `{consoleOpen && …}`, `{wizardOpen && …}`,
     `{settingsOpen && …}` render as independent conditionals: two panels
     CAN be mounted simultaneously.
   - ScreenStage.tsx:66, 69, 73 — the taskbar keys are pure self-toggles
     (`setWizardOpen(!wizardOpen)`, `setSettingsOpen(!settingsOpen)`,
     `setConsoleOpen(!consoleOpen)`): clicking FILM while SETTINGS is open
     leaves both open. The one-at-a-time half is NOT enforced here either.
   - The ONLY exclusion found is at a leaf call site: FilmWizard.tsx:598
     (`onClose(); setSettingsOpen(true)` — closes itself before opening
     settings). DeckControls.tsx:49-50 (AI ON) opens the console without
     closing wizard/settings; ModelPicker.tsx:175 opens settings without
     closing the wizard; ReproduceSheet.tsx:131-133 toggles only the wizard.
   - Also at the owner: ScreenStage.tsx:43-45 force-closes the console when
     the LLM stops running (`if (!llm?.running) setConsoleOpen(false)`) —
     relevant to the "stay until closed" half; owned by ScreenStage.
   Net: as written, one-at-a-time is enforced nowhere structural — store has
   no exclusion and the primary openers (taskbar keys) don't close siblings.
2. **SCR-INSPECTOR-CLICK — "The inspector's trigger is CLICK, never hover."**
   Owner: **src/components/FilmWizard.tsx** (ShotInspector :53; the ruling
   comment sits at :124 "the inspector opens IN PLACE on CLICK (owner
   2026-08-29...)"). Note for that file's reviewer: adjacent comments at
   :1109 and :1136 still say "hover a card" / "anchored at the hovered card"
   — wording only, but worth checking the actual handler there.
3. **SCR-COMMAND-PALETTE — hotkey, filter, Escape close.** Owner:
   **src/components/CommandPalette.tsx** (component, with its own
   CommandPalette.test.tsx covering open/Escape) and **src/App.tsx:69**
   (hotkey toggling `paletteOpen` from uiStore). screenStore.ts is not
   involved.
4. **SCR-TASKBAR-TOOLTIPS — "The FILM, SETTINGS, and LIBRARY taskbar keys
   each carry a tooltip naming what they open."** Owner:
   **src/components/ScreenStage.tsx** (FILM title :66, SETTINGS title :69,
   LIBRARY title :378). Observed satisfied there (all three `title`
   attributes name what they open), but the rendering is not this file's to
   judge.
5. **SCR-WINDOW-CONTROLS, rendering half** ("Opening an item shows the OS
   trio") — Owner: **src/components/ScreenStage.tsx:350-352** (minimize /
   maximize-restore / close buttons, each wired to this store's actions) and
   taskbar minimize at :390. Store half (each action does its named thing)
   is judged satisfied above and gets silence per protocol.
