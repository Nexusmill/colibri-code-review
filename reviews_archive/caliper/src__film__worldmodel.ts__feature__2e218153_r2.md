# Colibri review — src/film/worldmodel.ts (feature, run 2)

- **Source:** `src/film/worldmodel.ts` · **sha256:** 2e218153 (bytes identical to run 1 — per the 2026-09-14 feature-run doctrine this run loads run 1 as context and hunts ADDITIONAL features; run 1's artifact stands at src__film__worldmodel.ts__feature__2e218153.md)
- **Reviewer:** ZCode (GLM-5.3, in-session) · **Date:** 2026-09-14 · **Mode:** feature, pass 2
- **Context pack:** importers now FilmWizard + autopilot + vite.film (carriesAnchor is IN PRODUCTION since run 1 — the pre-spend gate shipped); the world review/edit gate (run 1's High) shipped as film-world-review 2026-09-05; rulings 42/43; outline + run-1 artifact as the delta base.

## What this module does (unchanged bytes — see run 1 for the full map)

The typed world model: strict validateWorld (character sheets garment-by-garment, set sheets with light physics), refuseDuplicates, compileAnchor, withWorldAnchor, carriesAnchor — now all wired: the anchor rides drafts and redrafts, coverage gates spend, THE PLAN shows the world for approval.

## Run-1 add-on status

- World review/edit gate → BUILT (film-world-review).
- carriesAnchor as pre-spend gate → BUILT (vite.film imports it; Era 52/53 wiring).
- Character-count guard (nice-to-have) → unverified this pass; rest in run 1.

## Suggested add-ons (NEW this pass)

**World-version stamping on shots — the run-level costume-change detector** — Value Med · Effort M
- What: `worldVersion: number` on WorldModel, bumped by the review gate's EDIT path; every board/segment record carries the version it was built under; the run view's grade cards mark takes that predate the current world.
- Why: the world is CONSTANT for a run's life — until the owner edits it at the review gate. After an edit ("her hair is auburn, not black"), every already-shot board and clip silently contradicts the new constant; the adversary grades each artifact against its own prompt (scope-blind to cross-take drift — the Era-45 addendum-3 lesson at run scale). A version stamp turns "which takes are stale" from archaeology into a column.
- How: worldmodel exports the version field; the review-edit patch path bumps it; produce stamps each artifact; FilmWizard's rail shows a dim "pre-edit world" pip on stale cards. Pure data plumbing — no engine change.

**A cast extractor — warn the wasted constant** — Value Med · Effort S
- What: `castOf(world, storyboard): { used: string[]; absent: string[] }` — names each character/set actually selected by shots (the anchor's names are the selection keys, ruling 42).
- Why: compileAnchor freezes EVERY character into EVERY prompt — a character the story never uses bloats every prompt past cheap-engine context windows (run 1 flagged the count guard; the sharper tool is usage, not count: THREE used characters plus one unused is the failure nobody sees). The plan judge flags character-without-sheet; nothing flags sheet-without-appearance.
- How: token-match each sheet's name across boardPrompt/shootPrompt (carriesAnchor's tokens() helper already exists in this file); THE PLAN renders "Rosa never appears" beside the world; the draft prompt could drop never-used sheets from later windows — owner call on that stronger form.

**Set-drift check across scenes** — Value Low-Med · Effort S
- What: normalized set-name matching across scenes (same location re-described in two scenes with drifted wording — "the lighthouse lamp room" vs "the lamp room").
- Why: sets are per-scene constants (ruling 43); the same PLACE as two sets is a costume change for scenery, and the anchor system cannot see it because each scene's prompt only carries its own sheet.
- How: a similarity pass over set names + their frame descriptors at world-build time; warn in the review gate. Pure function in this file.

## Nice-to-haves

- `validateWorld` max-character guard (carried from run 1) — the cast extractor subsumes most of its value.
