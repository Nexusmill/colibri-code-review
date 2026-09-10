# Colibri review — vite.bench.ts (feature)

- **Source:** `vite.bench.ts` · **sha256:** d8f385ab
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** the A/B machine (the agent chooses the experiment, this file owns every number); the WDDM warmup lesson (8-step cold 33.2s vs 6-step warm 6.0s was load, not steps); results append to the corpus via appendMeasured; verified: no VRAM reads, cold timing discarded; last touch 91620a1 (2026-09-02).

## What this module does

105 lines: `timedRender` (buildWorkflow → queue with client_id caliper-bench → poll to completion, 10-minute ceiling, wall-clock ms), the warmup render that absorbs the weight-load so variant order never contaminates timing, median-of-repeats with the ±5% tie band, deltaPct, and the measured-results append that makes every run retrievable knowledge.

## Suggested add-ons

**Record the VRAM footprint** — Value High · Effort S-M
- What: read /caliper/vram around the bench (before warmup, after the final run — or peak resident during) and append the model's loaded/total bytes and free-after to the corpus entry.
- Why: this is the natural source for the R1 VRAM-fit pre-flight estimate (queueStore's add-on) — the app's own measurement loop is already loading the exact bundles; recording the footprint turns every bench into a row of the estimate's table. Verified: no vram reads today.

**Keep the cold number** — Value Low-Med · Effort S
- The warmup exists to EXCLUDE load cost from the comparison; the load time itself (the warmup's wall clock) is useful knowledge — first-render latency per bundle — and is discarded today. One extra timing recorded under a `cold` tag.

**Queue-conflict guard** — Value Low · Effort S
- timedRender queues on the live server; a render already in flight would contaminate both variants equally but time them wrong. A pre-bench check of the live queue (getLiveQueueIds pattern, server-side fetch to /queue) refusing with "the queue is busy" keeps measurements clean. Note: the optimizer's analysis pass already refuses bench, this is the in-flight-render case.

## Nice-to-haves

- BenchResult carries runs with ms only; adding the prompt per run is redundant (fixed prompt string) — fine as is.
