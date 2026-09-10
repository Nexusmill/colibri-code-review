# Colibri review — src/stores/uiStore.ts (feature)

- **Source:** `src/stores/uiStore.ts` · **sha256:** 4cd8e2d3
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** 17 importers (every chassis component + screenStore); ruling 33 (one panel at a time, panels ephemeral, closing never opens); FEATURES.md `nav-surfaces`, `command-palette`; last touch 91620a1 (2026-09-02).

## What this module does

The smallest load-bearing store: the five-surface enum with `setSurface` (persisted — reload lands where you left), the command-palette flag, and the four console panels (AI console, film wizard, settings, first-run) whose open/close implements ruling 33 exactly — opening one closes the others, closing opens nothing, only `surface` persists.

## Suggested add-ons

Honest answer: this module is settled by owner ruling and needs nothing added. Two restrained observations:

**Panel-open persistence is deliberately absent — keep it that way** — Value: n/a
- A reload closes the wizard/settings/first-run. That is ruling 33's ephemeral-panel design, not a gap; the film run itself survives server-side (reload resumes at THE RUN), so nothing is lost. Recorded here so a future "persist panels?" suggestion dies on arrival.

**Surface hotkey hints in the palette** — Value Low · Effort S
- What: the palette (Ctrl+K) lists commands; adding the raw hotkeys it does NOT own (1-5 surfaces, Ctrl+Enter queue — handled in App.tsx:72-91) as a static legend section would make the chassis' full keyboard grammar discoverable in one place.
- Why: the frontend protocol's "every capability discoverable" test; today the surface hotkeys are undocumented anywhere user-facing.

## Nice-to-haves

- None that don't violate the settled chassis rule (no visual changes without commission).
