# Colibri review — src/components/ScreenStage.tsx (feature)

- **Source:** `src/components/ScreenStage.tsx` · **sha256:** 838a818b
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** the window-manager OS render layer — composes screenStore (windows/library), assetsStore, provenance, queueStore, api/library (delete/exportZip), api/film (filmList), power/state, llm/client, FilmWizard/FirstRun/SettingsConsole/ReproduceSheet; FEATURES.md `screen-*`, `library-*`, `power-*`, `optimizer-console`; scale-compensation contract (screen px / --stage-scale); last touch 91620a1 (2026-09-02).

## What this module does

The render screen as an OS: AssetWindow (drag/resize with stage-scale compensation, focus-on-press, double-click maximize, the OS trio), the Taskbar (library launcher-and-seat semantics, per-window keys with minimize toggling, power keys with the arm-then-fire two-press idiom and render-busy confirm lines), the AgentConsole (auto-analysis on open with heartbeat + retry, brain picker with live switching, per-turn cost/tokens/citations, proposal cards with APPLY/DISMISS — the human-clicked write), and the Library (rail = the disk's truth: films own their assets, one-off shelf by subfolder; film scopes as typed pipeline groups; the filter lens that never shrinks the export set; two-press delete; byte-exact zip export with remembered dir; every empty state an invitation with its next click).

## Suggested add-ons

**Console transcript persistence (session-scoped)** — Value Med · Effort S
- What: keep the AgentConsole's turns + spend tally in a store (or sessionStorage) so closing and reopening CONSOLE restores the conversation.
- Why: every other draft surface honors drafts-persist-across-close (the click-safe doctrine); the console is a panel that closes by one × and takes its whole analysis + proposals with it. Session-scoped (not disk) matches the console's ephemeral-by-ruling-33 nature while not punishing an accidental close mid-analysis.
- How: lift `turns`/`spend`/`applied` (ScreenStage.tsx:89-99) into a module-level or zustand slice; reset on app boot.

**Library: sort/group honored in film scope** — Value Low-Med · Effort S
- What: the SORT/GROUP keys hide in film scope (`!filmScope &&` at lines 794-795); film files render in fixed pipeline order. Sorting WITHIN each typed group (newest/oldest/name) is free structure.
- Why: a 70+ file film (the adversary's own M6 case) has one fixed reading order; within-group sort is the same "structure is information" pattern the group labels already implement. Minor chrome risk — flag for commission.

**A "what changed" note on window reopen** — Value Low · Effort S
- What: when `openAsset` focuses an EXISTING window (line 135-139), a brief highlight pulse on the title bar so the press has a visible result even when the window was buried under others.
- Why: ruling "every button press must produce a visible result" — focusing a buried window can look like nothing happened. The z-raise is the mechanism; the pulse is the acknowledgment.

## Nice-to-haves

- The library's `films` fetch is mount-once (line 536-545); a refresh on reopen would pick up films produced since it was minimized (the library stays mounted while minimized — data ages across a whole session).

## Notes

- Verified non-gaps: filter-lens vs export-set safety (R5) is implemented (selection resolves against full scope); schema-lag guard for older middleware exists (noArtifacts fallback).
