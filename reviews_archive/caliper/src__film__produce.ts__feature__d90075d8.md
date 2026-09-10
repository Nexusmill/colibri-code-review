# Colibri review — src/film/produce.ts (feature)

- **Source:** `src/film/produce.ts` · **sha256:** d90075d8
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** the resumable one-button flow's pure planner; the keyframe gate (owner 2026-08-30, universal 08-31); the 20s checkpoint doctrine (owner 2026-08-29); consumed by vite.film's startProduce/runProduce; unchanged since 82ff326 (2026-08-31) — stable.

## What this module does

89 pure lines: `planProduce` — keyframes for shots missing one, segments ONLY for owner-approved boards (the gate: no footage for an unapproved board; a board rendered this pass cannot shoot this pass), voice for missing narration, score when requested and absent, then assembly — ordered segments-BEFORE-keyframes so a resume lands the approved window's paid-for footage before drafting more boards, with skipped counts that refuse to call an unapproved board finished. `checkpointBoundary` accrues segment footage to the 20s window, checkpointing only when more work follows (the final window runs straight to assembly).

## Suggested add-ons

**A client-visible plan preview** — Value Med · Effort S
- What: surface planProduce's counts BEFORE the run starts — "this press: 3 boards · 2 footage gaps · score · assemble (7 finished shots skip)" — beside START THE RUN / START THE FIXES.
- Why (verified): the plan's shape reaches the user only as the job log's first line AFTER the run starts; the repair flows (START THE FIXES) especially promise "only the gaps run" without ever listing the gaps. The function is pure and already computed server-side at start; a preview call (or reusing the status payload) makes the resumability visible before spending.
- How: an autopilot-plan action or plan counts on the status response; the wizard renders them in the run pane.

**KF-review cadence note** — Value Low-Med · Effort S
- The keyframe review window accrues by shot SECONDS like clip checkpoints (kfBoundary reuses checkpointBoundary) — at clipSeconds 15 that reviews 1–2 boards per pause; a long film pauses many times. APPROVE ALL mitigates; a count-aware batch floor (e.g., review at least N boards per pause, still time-bounded for clip windows) would reduce ceremony on cheap boards. Owner call — boards are the cheap leg; the current cadence is the conservative reading of the universal-gate ruling.

## Nice-to-haves

- CHECKPOINT_SECONDS is doctrine (the owner's number); no per-run override suggested.
