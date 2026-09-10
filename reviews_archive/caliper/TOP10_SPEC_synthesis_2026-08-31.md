# Spec-run synthesis — top 10 files by import-graph PageRank (2026-08-31)

Job: spec mode, per colibri-review v0.2.0, against the PROVISIONAL registries in spec/
(shipped 7475752). Ranking: jcodemunch file PageRank, index refreshed 2026-08-31.
Cache: zero prior spec-mode reviews existed (manifest held only bug/feature/audit rows).

## Score
8 of 10 files conform at their layer. 2 CONFIRMED divergences, 1 PLAUSIBLE (untraced),
2 staleness notes (comments), 2 registry-authority corrections for the owner.

## CONFIRMED divergences (adversarially verified, both ends cited)

1. **[HIGH] The 12-second shot-seconds ceiling vs the 15-second clip doctrine** —
   src/film/autopilot.ts:270 (validateStoryboard clamp) + vite.film.ts:1933 (adjust drawer
   "seconds are 1-12") vs WIZ-CLIP-LENGTH-CAP / film-kf-review. The grid is carved at
   `clipSeconds ?? 15` (vite.film.ts:1513/1521) but every shot's recorded seconds clamps
   to 12; non-song films then derive their ENTIRE timeline from the clamped sum
   (vite.film.ts:1299, 1316) — a 15s-slot script film's duration collapses to 80% of
   intent; the owner cannot even set 13-15s in the adjust drawer. This is a pre-Era-48
   leftover (the vitest coverage tests run at 5s slots, so the clamp never bites in
   tests). Fix direction: clamp to `maxClipSeconds(pair)` instead of the literal 12 —
   in BOTH validateStoryboard and the adjust route.

2. **[MEDIUM] CaliperVram type omits argv** — src/api/types.ts:50-56 vs
   PWR-VRAM-GROUND-TRUTH / PWR-STATUS-TRUTH. The node ships argv
   (comfy/caliper_vram.py:140: `"argv": list(sys.argv)`); the client interface has no
   field for it. Fix: add `argv?: string[]`.

## PLAUSIBLE (unverified — routed, not judged)

- SCR-PANELS-IN-PLACE "one at a time": uiStore's three console booleans have no mutual
  exclusion in the store; enforcement, if it exists, lives in the component layer
  (ScreenStage/wizard). Trace `setFilmWizardOpen`/`setSettingsOpen`/`setAiConsoleOpen`
  call sites before ruling.

## Staleness notes (comments lie, behavior is fine)

- src/providers/serviceKeys.ts: "adapter to come" hints for openrouter/eachlabs — both live.
- src/providers/modelRoutes.ts: "cloud: replicate today" — OpenRouter/EachLabs shipped.

## Registry-authority corrections the OWNER should rule on (clause faults, not code faults)

- SCR-RELOAD-RESTORE side_effect names only `caliper.screen`; the active-tab half
  persists under `caliper.ui`. Clause should name both keys.
- PWR-VRAM-GROUND-TRUTH's argv parenthetical is CORRECT server-side (caliper_vram.py:140)
  — finding 2 above is the client type lagging the clause, so the clause stands.

## Coverage notes for the next run

- The 12s finding's cousins live in vite.film.ts (rank: not in top 10 by PageRank but
  clearly load-bearing for the film pipeline) — a dedicated spec pass on vite.film.ts
  against film-run.json is the highest-value next dispatch.
- The harness denied read-only hashing for src/install/catalog.ts (4 attempts) — the
  cache key for that review is content-identified, not sha-keyed; re-hash when the hook
  permits.
