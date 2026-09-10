# Colibri review — src/surfaces/QueueSurface.tsx (feature)

- **Source:** `src/surfaces/QueueSurface.tsx` · **sha256:** a679ed2b
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** reads queueStore + bundlesStore + uiStore + api/client (getQueueEntries/cancelQueued/interrupt) + llm/client; FEATURES.md `queue-surface`, `optimizer-console`; prior bug review at this sha; last touch e339b17 (2026-08-20).

## What this module does

The server-truth queue surface: a 2s poll of the SERVER's queue (not just this window's jobs) with the untracked-entries section (bench renders, restart orphans — named by source, killable per-entry with the pending-delete vs running-interrupt distinction), the app's own job cards (elapsed ticking per second, node progress + GaugeLine, per-job cancel / recall-seed / open-output), the optimizer status plate when the AI is on (download progress included), and the clear-queue wedge cleaner with its consequence-stating tooltip.

## Suggested add-ons

**ETA from the measured corpus on running jobs** — Value Med · Effort M
- What: beside the elapsed timer, an honest projection — "typically 4m 10s for this bundle at this shape (7 measured runs)" — from knowledge/measured-results.md.
- Why: elapsed + raw node progress says how long it HAS run, never whether 40% means two minutes or twenty; the app's whole optimizer premise is that durations are measurable. Sourced ETAs satisfy the truthful-status rule; unsourced ones would violate it.
- How: a tiny server endpoint (or reuse of the KB search) summarizing per-bundle durations; QueueSurface renders it under the card meta. Filed once here; the queueStore review cross-references.

**"What is this" on untracked entries** — Value Med · Effort S
- What: an expandable line on each untracked row naming the queued WORKFLOW (bundle/loader class types) — needs the client.ts add-on (carry `entry[2]`), then this surface renders it.
- Why: today an orphan's identity is only knowable by killing it; sourceLabel answers who, nothing answers what.

**Queue-length badge on the chassis rail** — Value Low · Effort S-M
- What: a count on the Queue nav plate while work runs, so the arcade/generate screens carry the signal without switching.
- Why: pervasive-responsiveness doctrine; the socket already pushes queueRemaining into the store (queueStore.ts:132) and no surface outside Queue reads it. Visual chrome change — needs commission.

## Nice-to-haves

- `killEntry` for a running entry calls `interrupt()` globally (the server's only lever, honestly documented in the tooltip) — when ComfyUI gains per-prompt interrupt (already stubbed client-side in `interrupt(promptId)`), pass the id here.
