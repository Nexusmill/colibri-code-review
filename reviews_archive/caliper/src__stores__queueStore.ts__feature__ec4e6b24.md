# Colibri review — src/stores/queueStore.ts (feature)

- **Source:** `src/stores/queueStore.ts` · **sha256:** ec4e6b24
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** 14 importers (App, CommandPalette, DeckControls, ReproduceSheet, ScreenStage, StatusFooter, assetsStore, all surfaces); FEATURES.md `render-guard`, `render-queue-done`, `queue-surface`; machine fact: 16 GB card shared with ComfyUI; last touch 69da98e (2026-08-20).

## What this module does

The render pipeline's client state: `queue()` builds the workflow through the bundle constraints, seeds (randomized or held), and posts with a TOCTOU-safe single-render guard (`queueInFlight` + store busy check, toggleable); rejections become honest failed rows with node-error details; `applyEvent` maps websocket events onto jobs with terminal-state guards (late events never resurrect finished work) and reconnect reconciliation against the server's live queue (a disconnect cannot deadlock the single guard); cancel and clear-all reconcile only what is still in flight.

## Suggested add-ons

**VRAM-fit pre-flight estimate on queue** — Value Med-High · Effort M
- What: before posting, a soft estimate line — "LTX at 1216×704×97f has measured ~11.2 GB; 9.4 GB free now" — from the bundle+params against the live VRAM read, shown beside RUN (not a hard gate; the queue button stays pressable).
- Why: on the 16 GB shared card the OOM class is a real waste path: `bundlesStore.select` unloads stale residents when free < 6 GB (switch-time stewardship), but nothing at QUEUE time weighs the ASK against what's free. The truthful-status doctrine is satisfied: the number states its source (measured history + live /caliper/vram).
- How: hook after `buildWorkflow` succeeds (queueStore.ts:95): read `getCaliperVram`/`cudaFreeGb` (pattern already imported in bundlesStore), a footprint table seeded from the bench corpus (knowledge/measured-results.md) with an honest "no measurement for this shape yet" fallback. Display in the Generate pane beside the existing queue error chip.

**Estimated time-to-done from the measured corpus** — Value Med · Effort M
- What: running jobs show an ETA derived from prior runs of the same bundle at similar shapes (the bench corpus already exists for exactly this).
- Why: QueueSurface shows elapsed + node progress but no projection; the corpus is the app's own measured truth and currently only feeds the optimizer.
- How: an api surface over the KB (`searchKnowledge("bench <bundle>")` exists server-side) or a small stats file; QueueSurface renders it with its provenance. See the QueueSurface review — cross-file add-on, filed once there.

## Nice-to-haves

- `randomSeed()` produces 48-bit values while the UI seed input caps at 2^47 — harmless today; note for the constraints review's seed-range item.
