# Spec review — src/film/analysis.ts

- Source: `src/film/analysis.ts` (211 lines) · Reviewer: ZCode in-session (GLM-5.3) · sha256: `067464bef31c37eef75298edaa5dc5485f683a83d4b0b4aae4ae9b7a2a8c641a` · 2026-08-31 · mode: **spec** · registries: `spec/film-wizard.json`, `spec/film-run.json`
- Context pack: full read; the draft-grid carve verified to live in vite.film.ts:1513/1521 (autopilot's `shotGrid(duration, clipSeconds ?? 15)`, NOT this file's section-aware shotGrid); tests at analysis.test.ts cross-checked.

## Verdict
Conforms for what it owns — no divergences. The DSP core (centered envelopes, tempo autocorrelation with the 90-150 prior, beat snap+refine, section novelty) feeds transcribe/lyric-slot material; it sets no timings policy, so no clip-length clause is violated here. The clause WIZ-CLIP-LENGTH-CAP's carve observable is satisfied at its true owner (vite.film.ts:1513/1521 — carved at `clipSeconds ?? 15`).

## Divergences
None.

## UNJUDGEABLE HERE
- RUN-CLIP-CHECKPOINT boundaries (20s accrual, final-window never pauses) — window math lives in vite.film.ts produce.
- This file's own `shotGrid(sections, beats, targetSec = 5)` — no draft caller traced (the draft uses autopilot's uniform grid); if any legacy path still calls it with the 5s default, that path would carve at 5s. Routed: vite.film.ts / film store own the call graph.
