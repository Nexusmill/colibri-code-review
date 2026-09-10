# Colibri review — src/stores/bundlesStore.ts (feature)

- **Source:** `src/stores/bundlesStore.ts` · **sha256:** 575055ae
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** 13 importers (App, CommandPalette, DeckControls, ReproduceSheet, queueStore, all five surfaces' consumers); FEATURES.md rows `param-persistence`, `param-migration`, `bundle-switch`, `vram-instrument`; memory: "exactly one explicit reset" design rule; last touch 0068895 (2026-08-20).

## What this module does

The client home of bundle state. Load is honest-failure (a failed load never masquerades as the server file; `save()` refuses until `loaded`), legacy id migration is persisted on first read, and persistence is touched-only (`paramEdits` v2 + `migratePersisted` stripping factory-equal values so changed file defaults still reach old sessions). Bundle switching is VRAM-stewardship: it reads the server's resident truth (never the previous selection), auto-unloads under 6 GB free with a race guard, else offers the unload prompt. `setParam` snaps frames/CFG to constraints and records only touched fields.

## Suggested add-ons

**Divergence indicator from `paramEdits`** — Value Med · Effort S
- What: a view-only affordance on the deck listing which params differ from the bundle FILE defaults ("EDITED: steps, seed"), driven straight off `paramEdits` (the store already holds exactly this data).
- Why: `param-persistence` guarantees touched fields survive, but nothing shows the user WHICH fields are session edits vs file defaults — after a long session the deck state is opaque. Deliberately view-only: the app's design rule is exactly one explicit reset, and this suggests none.
- How: `Object.keys(paramEdits[bundle])` rendered in DeckControls/AdvancedDrawer; no new state.

**Per-bundle prompt history** — Value Med · Effort S
- What: keep the last N prompts per bundle (store array beside `prompts`) with a recall affordance.
- Why: prompts persist per bundle but a typed prompt that was never rendered is lost on edit — REPRODUCE only covers rendered work. See also the GenerateSurface review (same add-on, UI side).
- How: `prompts` stays the live value; a `promptHistory: Record<string, string[]>` appended on queue (queueStore already calls `saveProvenance` with the prompt — the append can hook there or in `setPrompt`).

## Nice-to-haves

- A "what changed in the file" note after `save()` — the store already diffs implicitly (fresh defaults vs paramEdits overlay); a one-line status naming fields whose FILE default changed since last load would close the loop with the v2 migration's promise.

## Notes

- The `select()` VRAM stewardship (race-guarded, server-truth) is the module's signature behavior — add-ons must not touch its invariants.
