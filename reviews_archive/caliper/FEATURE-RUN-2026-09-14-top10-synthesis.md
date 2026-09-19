# Feature run synthesis — top 10 by import PageRank (2026-09-14)

Owner commission: "another feature run on the top ten files in caliper."
Method: file-level ranking from jcodemunch symbol PageRank over src/
(same as the 2026-09-05 runs); cache gate honored — three files are
byte-identical to their reviewed shas and are REPORTED, not re-reviewed;
six got DELTA reviews against their 2026-09-05 artifacts; one
(install/catalog.ts) is fresh to feature mode.

## The board

| # | File | Mode | Verdict in one line |
|---|------|------|---------------------|
| 1 | src/bundles/schema.ts | delta 33e6a4f4 | Vocabulary complete; remaining: export/import (3rd carry), migrations stamp, min sizes |
| 2 | src/bundles/constraints.ts | delta e75972de | Agenda BUILT by the spree; seed bounds + fps bounds are the tail |
| 3 | src/api/types.ts | delta 6cdf2c46 | Settled; the one owner-valued add-on is per-process cmdlines on the VRAM table |
| 4 | src/film/worldmodel.ts | cached 2e218153 | byte-identical — standing add-ons live in its artifact, unrestated |
| 5 | src/film/autopilot.ts | delta ada229eb | Two-tier landed today; the big open item is LAST-FRAME conditioning (h3-max's own differentiator, filtered dead at the schema) |
| 6 | src/api/client.ts | delta e5904c0d | Spree additions all landed inside its ethos; backendHealth carried a THIRD time |
| 7 | src/providers/modelRoutes.ts | cached dbe64730 | byte-identical — reported |
| 8 | src/install/catalog.ts | FRESH a52e4d35 | Never feature-reviewed; two real ones: render-side size+sha verify (install hardening), -c context per LLM model |
| 9 | src/film/analysis.ts | cached 067464be | byte-identical — reported |
| 10 | src/stores/uiStore.ts | delta 7fda1f62 | Fifth panel landed; derive the one-panel matrix from one list so ruling 33 is structurally unbreakable |

## Ranked add-ons (the de-facto next-commission menu)

1. **Last-frame conditioning** — High · M (autopilot + openrouterVideo +
   vite.film): h3-max sits in BOTH tiers and lists last_frame; the schema
   filters it dead today. Approved board N+1 as the ending frame of shot N
   = designed continuity bookends on the arena-#1 i2v engine.
2. **Finish-resolution pick (the 2K finish)** — Med-High · M: the
   EXPENSIVE note advertises "$0.13/s at 2K" the run cannot buy (the
   replicate leg sends no resolution). Also the research-backed answer to
   the retired upscale question — render at 2K instead of paying to
   invent detail afterward.
3. **Win-rate sample honesty** — Med · S: n is COMPUTED then discarded on
   winRatesFromRuns' return line; one line from done.
4. **Strategy truth under EXPENSIVE** — Med · S: both seats cost $0.08/s —
   DRAFT-FIRST buys an audition, not savings; the suggestion line should
   say so.
5. **Catalog render-side size+sha verify** — Med · S-M: the install-
   hardening tail's .part-rename gap, data + one downloader check.
6. **Serve each LLM's context window** — Med · S: the catalog knows
   (contextTokens), the spawner serves 16k regardless.
7. **Bundle export/import** — Med · S: THIRD consecutive carry; with the
   constraint vocabulary now real, tuned bundles are worth moving.
8. **VRAM process cmdlines** — Med · M: the footer's process table answers
   "WHICH python squatting my VRAM" — the diagnosis path this machine's
   history actually walks (needs a canonical-node re-sync).

Low tier (all · S): backendHealth (THIRD carry — commission or kill),
migrations stamp, PANELS-list matrix, seed bounds, fps bounds, width/height
minimums, vocabulary consolidation, WsEvent guard, catalog deprecated flag,
MANUAL blocked-state display.

## Cross-file findings

- **Convergence is real**: of the ten add-ons these files carried on
  2026-09-05, the spree BUILT eight (constraint ceilings, lora strength,
  live-ladder cards, bill price basis, energy pacing, queue prompt blob,
  hotkey legend, battery wiring). The surface is getting cheaper to review
  each pass — the delta+cache discipline working as designed.
- **The carry pattern**: backendHealth and bundle export/import have now
  been suggested three runs running without an owner pick. They're cheap;
  they should either ride a future wave or be explicitly declined so the
  backlog stays honest.
- **Today's two-tier wave seeded the two highest-value items**: both #1
  and #2 exist BECAUSE h3-max entered the doctrine (its last-frame
  capability and h3's 2K tier are newly load-bearing).

Artifacts: seven per-file reviews beside this synthesis; the three cached
files' standing suggestions remain in their 2026-09-05 artifacts
(worldmodel 2e218153, modelRoutes dbe64730, analysis 067464be).


---

# Wave 6 (route intelligence) - cross-file synthesis, 2026-09-15

Files in this pass: vite.routes.ts, vite.film.ts, src/api/modelRoutes.ts,
src/components/SettingsConsole.tsx, tools/ui-harness.mjs, vitest.setup.ts,
src/components/SettingsConsole.test.tsx, src/api/modelRoutes.test.ts.

1. **The contract loop is closed end to end**: producers (vite.film's three
   stamped legs) -> store (vite.routes recordRouteHealth, fire-and-forget) ->
   transport (modelRoutes health/presets normalization) -> consumer
   (SettingsConsole row, newest verdict wins). Each seam has a pinning test
   (vitest 498 green) and the row is live-verified through the real app
   (harness route-intelligence PASS, 75/0/8 fast tier).
2. **One confirmed bug found and fixed in-session** (ok-wins-regardless-of-
   recency) plus three latent harness bugs (restore-chip delete target,
   document-wide gone-check, TS generic in .mjs) - all caught by the review
   pass and the first post-fix harness run, all closed with proving tests.
3. **Accepted LOW findings recorded, not fixed**: store read-modify-write
   races (serialized in practice; memory-only impact) and preset-apply
   skipping validateRoute (self-authored snapshots; GONE flag surfaces
   staleness).
4. **Environment note that cost a false FAIL**: restarting the preview
   server orphaned/duplicated vite children (port fallback to 4174) and the
   driven Edge served the app from CACHE while every API call died with
   "Failed to fetch" - the documented stale-cache false-bug class. Recovery:
   kill by PID from netstat, start ONE preview, verify the API through the
   port before trusting any harness verdict.
