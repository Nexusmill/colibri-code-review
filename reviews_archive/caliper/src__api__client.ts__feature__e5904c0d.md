# Colibri review — src/api/client.ts (feature)

- **Source:** `src/api/client.ts` · **sha256:** e5904c0d
- **Reviewer:** ZCode (GLM-5.3, in-session) · **Date:** 2026-09-14 · **Mode:** feature (DELTA vs 9f5e8b48 @ 2026-09-05)
- **Context pack:** 14 importers (App, FilmWizard, MediaView, ScreenStage, StatusFooter, llm/client, assetsStore, bundlesStore, queueStore, Graph/Outputs/Queue surfaces); deltas since last review = 6cc6391 (getVramPreflight), e2328d3 (NodeSync + getNodeSync), fe47cc0 (comfyStart/comfyRestart/caliperOff), 9102b79/ea80d20 (queue prompt blob ride); full current outline + absence-probe for a health helper.

## What this module does

The single typed API surface: ComfyUI queue ops (queuePrompt with typed rejections, history, object_info, live queue ids AND full entries, cancel/interrupt/clear), system truth (getSystemStats, getCaliperVram, freeVram which throws rather than lie), the new truth family — getVramPreflight (measured bench footprint vs live free memory), NodeSync/getNodeSync (the deployed custom node's identity verdict), and the power trio comfyStart/comfyRestart/caliperOff (POWER ON/RESTART/POWER OFF walk the launcher's own tail) — plus the graph seed/boot-sync/backup/restore family and film-aware viewUrl. Every function a thin honest fetch; no caching, no silent fallbacks.

## Fixed since last review

- "What is actually running" (queue prompt blob, Med·S) → BUILT: QueueEntry carries the prompt summary (E-4 orphan rows decode their graphs via queueNodes).
- backendHealth() one-liner → still ABSENT (verified: zero Health matches in the file) — carried below.

## Suggested add-ons

**backendHealth() — one honest probe** — Value Low · Effort S (CARRIED, third time listed)
- What: one exported probe (getSystemStats with a short timeout) answering up/down/starting.
- Why (verified): StatusFooter, QueueSurface, and the power seat each still own a slightly different away-backend story; the footer instrument is the honest one and the power seat's START-state derivation duplicates it.
- How: ~10 lines here; three call sites swap their hand-rolls. Cheap consolidation, zero behavior change.

**history 404 vs parse-failure split** — Value Low · Effort S-M (CARRIED nice-to-have)
- getHistory returns null on any failure; distinguishing "never existed" from "unparseable" sharpens the Outputs disconnect reconciliation. Bug-mode territory; note only.

## Nice-to-haves

- None — the file's spree additions (preflight, node sync, power) all landed inside its thin-fetch ethos; nothing to add without breaking it.
