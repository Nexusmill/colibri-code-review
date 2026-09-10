# Colibri review — src/components/GameScreen.tsx (feature, DELTA)

- **Source:** `src/components/GameScreen.tsx` · **sha256:** 74810a45 (prior feature review a23a28cc, 2026-08-18 — file changed; this is a delta)
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature (delta)
- **Context pack:** the four-cabinet arcade (Queue: BRICKS · Outputs: SERPENT · Bundles: PADDLE · Graph: SILO), module save table, arcadeSound module; FEATURES.md `arcade-boot`; last touch 08068f9 (2026-08-26).

## What this module does (delta view)

The cabinet shell gained dated TOP-5 score tables (with migration from single-best saves) and full arcade SOUND (the `snd` WebAudio module rides every event: bounces per row, lasers, booms, fanfares, alarms). Beyond the shell: BRICKS grew stage-shape patterns, silver/gold bricks, combo x2, laser cannons (Z), catch (C), pierce (D), multiball (M), and from level 3 a descending wall on a timer; SERPENT gained sealed borders at 60 with drifting sine mazes at 60/120, warp gates at 90, burst (hold A, paid in appetite), bonus pickups, rival tail-bite bounties, and rivals that steal food and grow; PADDLE gained smash, two-player deploy (hold A/D), rubber-band AI, serve english, deuce/win-by-two, and match-point hush; SILO gained the bomber, the killer sat, smart bombs that weave, MIRV splits, fallout populations (cities and crews die by headcount under settled clouds), squalls that carry dust away, chain-kill bonuses, and 10k bonus-city rebuilds.

## Fixed since last review (the 2026-08-18 deferred list, closed)

- **Sound (WebAudio bleeps)** — IMPLEMENTED (arcadeSound.ts + pervasive snd.* calls). The old caveat "the machine is silent by design" was superseded by commission.
- **Persistent top-5 score tables per game** — IMPLEMENTED (bestFor/saveBest/insertBest, dated, slice(0,5), legacy migration at GameScreen.tsx:63-88).
- **BRICKS multiball** — IMPLEMENTED (the M drop spawns two balls, capped at 6; lines 335-342).
- **Rival serpents eating food/growing** — IMPLEMENTED (rivals steal the meal and grow; line 609) — adopted despite the old economy-muddying worry, balanced by the tail-bite bounty.
- **SILO screen-shake on nuke** — STILL ABSENT, and the old reasoning stands (a shaking "monitor" reads as chassis damage in the fitted-glass conceit; the nuke flash covers the beat). Stays deferred.

## Suggested add-ons (new)

**A PAUSE key** — Value Med · Effort S
- What: P (or Escape) freezes the step loop mid-play with a PAUSED plate; any input resumes. No cabinet has any pause today (verified — no pause concept in the file).
- Why: the games sit BESIDE working surfaces; a phone-call-length interruption currently costs a life or a city. The module save table already preserves state across surface switches, so the mechanism's spirit exists — just not within a run.
- How: a shell-level `paused` flag checked at the top of `step`; the host loop's try/catch already isolates per-frame failures.

**Attract-mode self-play** — Value Med · Effort M
- What: on the attract screen, a scripted/simplified bot plays a short loop beneath the title art (the classic arcade attract).
- Why: the attract screen shows static art + scores; self-play is the arcade genre's own "what is this game" advertisement and the cabinets already have the full game engines in scope to drive.
- How: a canned input script per cabinet (deterministic seeds already exist); draw through the normal draw path dimmed under the art overlay.

**Sound mute key** — Value Low · Effort S — **PLAUSIBLE, unverified**: arcadeSound.ts is outside this review's scope, so whether a mute already exists there is unconfirmed. If absent: a cabinet-shell mute toggle persisted in localStorage, default ON (sound is commissioned behavior).

## Nice-to-haves

- High-score export/share (copy the top-5 line as text) — low value for a single-machine app; noted only.
