# Colibri review — src/components/CommandPalette.tsx (feature)

- **Source:** `src/components/CommandPalette.tsx` · **sha256:** 4bf4ae90
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** the Ctrl+K palette; FEATURES.md `command-palette`; the App.tsx hotkey grammar (1-5/Ctrl+Enter/Ctrl+K); verified absence: actions are navigation-only; unchanged since 2026-08-17 — stable.

## What this module does

The keyboard command surface: surface jumps (5), per-bundle switches, recall-last-seed (only when a finished job for the selected bundle exists), and open-latest-output — substring filter, arrow cursor, Enter runs.

## Suggested add-ons

**The verb actions** — Value Med · Effort S
- What: add the chassis' one-press verbs as actions: toggle OPTIMIZE (AI on/off), open FILM / SETTINGS / LIBRARY, clear queue (with its consequence hint), unload models, toggle the single render guard.
- Why: the palette is the app's "every capability discoverable" surface and today it only navigates; the verbs exist as store actions with truthful result paths already. Verified absent.

**The hotkey legend section** — Value Low-Med · Effort S
- The static footer row App.tsx's grammar review (R1) asked for: 1-5 surfaces · Ctrl+Enter queue · Ctrl+K palette — listed as non-actionable hint rows at the list's foot.

**Fuzzy matching** — Value Low · Effort S
- Substring only; subsequence matching ("gc" → "go to graph") is the palette convention.

## Nice-to-haves

- Recently-used ordering when the query is empty. Low.
