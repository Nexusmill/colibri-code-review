# Colibri review — src/api/client.ts (feature)

- **Source:** `src/api/client.ts` · **sha256:** 9f5e8b48
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** 14 importers (App, FilmWizard, MediaView, ScreenStage, StatusFooter, llm/client, assetsStore, bundlesStore, queueStore, GraphSurface, OutputsSurface, QueueSurface); sha matches the cached bug/spec reviews (file unchanged since the full hunt); last touch f7540c3 (2026-08-21).

## What this module does

The single typed API surface: ComfyUI queue ops (`queuePrompt` with typed rejections carrying nodeErrors, history, object_info, live-queue ids AND full entries with client attribution, cancel/interrupt/clear-queue), system truth (`getSystemStats`, `getCaliperVram`, `freeVram` — which throws rather than report a false success), the graph seed/boot-sync/backup/restore family, the film-aware `viewUrl`, and the two taskbar power calls. Every function is a thin honest fetch — no caching, no silent fallbacks.

## Suggested add-ons

**"What is actually running" — expose the queue entry's prompt blob** — Value Med · Effort S
- What: `getQueueEntries` (client.ts:67-79) currently reads `entry[1]` (prompt id) and `entry[3]` (client meta) and drops `entry[2]` — the full queued prompt/workflow. Carry a compact summary (bundle/loader class_types, or the raw object under a flag) on `QueueEntry`.
- Why: the Queue surface's untracked-entries section says WHO queued an orphan (`sourceLabel`) but not WHAT it is; a bench render or restart-orphan can only be identified by killing it and seeing what breaks. Diagnose-the-layer (ruling 25) wants the question answerable before the kill.
- How: extend `QueueEntry` with `prompt?: unknown` parsed from `entry[2]`; QueueSurface's untracked row gains an expandable "what" line. No server change — the data already rides `/queue`.

**A `backendHealth()` one-liner** — Value Low · Effort S
- What: one exported probe answering up/down/starting (system_stats with a short timeout) so new UI never hand-rolls the fetch-and-catch pattern that StatusFooter, QueueSurface, and the footer each repeat.
- Why: three surfaces currently each own a slightly different away-backend story; the footer instrument is the honest one.

## Nice-to-haves

- `getHistory` returns null on any failure; a variant distinguishing 404 (never existed) from parse-failure would make the Outputs "lost during disconnect" reconciliation (queueStore) sharper. Bug-mode territory; note only.
