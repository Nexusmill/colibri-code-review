# Spec review — src/film/autopilot.ts

- Source: `src/film/autopilot.ts` (714 lines) · Reviewer: ZCode in-session (GLM-5.3) · sha256: `32b00e7e442885f9f61bb2e2c2ae7af3a72d9cdcdbb89e32ceaa8e4f0a2cfc9f` · 2026-08-31 · mode: **spec** · registries: `spec/film-wizard.json`, `spec/film-run.json`
- Context pack: full read (two passes); grid carve verified at vite.film.ts:1513/1521 (`shotGrid(duration, record.shape.clipSeconds ?? 15)`); seconds consumers verified at vite.film.ts:442, 1299, 1316, 1933; ENGINE_TIERS/prices cross-checked against FEATURES film-engine-doctrine.

## Verdict
One divergence, CONFIRMED, and it is the load-bearing one: the 12-second ceiling on shot seconds contradicts the 15-second clip doctrine everywhere seconds are consumed.

## Divergences
**[HIGH] The 12s shot-seconds ceiling predates and contradicts the 15s clip doctrine** - `autopilot.ts:270` (validateStoryboard)
- **Expectation (quoted):** WIZ-CLIP-LENGTH-CAP — "the default clip length is 15s" · film-kf-review — "the draft grid carves the song at the chosen length" (boundaries).
- **Trigger:** any film drafted with the default `clipSeconds ?? 15` (vite.film.ts:1513/1521 carve 15s grid slots).
- **Behavior:** `seconds: Math.max(1, Math.min(12, Math.round((grid[i].end - grid[i].start)*10)/10))` clamps every 15s slot's recorded seconds to 12. Traced consumers: (1) vite.film.ts:1299 — non-song films derive the run's ENTIRE duration from `sum(shot.seconds)` → a 15s-slot script film's timeline collapses to 80% of intended; (2) vite.film.ts:1316 — per-shot walk `t += s.seconds` inherits the same drift; (3) vite.film.ts:1933 — the ADJUST drawer rejects 13-15 outright ("seconds are 1-12"); (4) storyboard.md's table (:442) and the redraft prompt display 12s for 15s shots. Song films keep their song-derived timeline, but their recorded per-shot seconds are still wrong on paper and in every display.
- **Fix:** raise the clamp (and the adjust validation) to the pair's `maxClipSeconds()` ceiling instead of the literal 12.
- CONFIRMED — trigger path traced end to end into four consuming sites.

## UNJUDGEABLE HERE
- WIZ-CRITIQUE-GATE, WIZ-ADVERSARY-FIRST, WIZ-BRIEF-OUTRANKS, WIZ-INTERROGATIVES observables (what the MODEL does with these prompts) — judged at the run/brain layer (vite.film.ts call sites + wizard UI).
- RUN-KEYFRAME-GATE / RUN-CLIP-CHECKPOINT behavior (plan refusing segments, CONTINUE gating) — window/plan logic lives in vite.film.ts produce.
- Conforming by direct read: ENGINE_TIERS owner's picks and prices (p-video $0.02/20s, h3 $0.08/15s, sora-2-pro $0.30@720), `maxClipSeconds` min-of-pair, ENGINE_QUESTIONS riding the draft, redraft freeze rules (beats/seconds frozen, anchor verbatim), patch step-forward law.
