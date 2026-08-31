# Asset Forge bug hunt — 2026-08-04 synthesis (post-marathon delta sweep)

- **Model:** claude-fable-5, in-session (scanner subagents abandoned after 5 consecutive
  infra failures — context thrashing ×4, API credit error ×1; G10 switch-approach).
- **Scope decision:** the 2026-08-03→04 forge marathon (~50 asset-forge commits: DOCTRINE-1..6
  incl. the DOCTRINE-4 LLM rip-out, concurrency on all provider paths, CKPT-STREAM, 49-model
  sweep, FLAT library layout, prompt-library v4) landed AFTER the last hunt sweep (07-24/25),
  staling every major unit. This sweep covered the changed money surface end-to-end.

## Units reviewed this sweep (current bytes, sha-recorded in each review)
| unit | mode | outcome |
|---|---|---|
| forge/concurrency.py (NEW module) | bug r1 | **HIGH fixed** — consumer-abort queue drain (paid calls) |
| forge/quality.py (NEW module) | bug r1 | **MEDIUM fixed** — direction-blind detail metric |
| templates/library.html | bug r1 | **HIGH fixed** — null catalog rows kill boot(); page dead |
| forge/library_gen.py | bug r3 (delta) | **MEDIUM fixed** — spent_est under-reports billed spend |
| forge/imagegen/replicate_flux.py | bug r3 (delta) | clean — AF-SDXL-404 fallback + retry ladder verified money-safe |
| forge/imagegen/schema.py | inspected (delta) | clean — get_latest_version pre-bill only, cache discipline sound |
| forge/output_opts.py (NEW module) | inspected r1 | see cross-file finding #1 below |
| forge/seamless.py | inspected (delta) | clean — blend math strictly seam-reducing, no-raise contract holds |
| forge/userlib.py | inspected (delta) | clean — FLAT pack/type inference correct, surrogatepass handling sound |
| forge/bundle.py | delta vs ef93ca2c | clean — map_bounded conversion preserves order + all-or-nothing + INCOMPLETE.txt; trip-first-then-raise correct |
| app.py | delta (DOCTRINE-4 lines) | clean — estimate endpoints report retired upgrade at $0 |
| forge/imagegen/prompts.py | core engine pass | clean — DOCTRINE-4 removal coherent; _legacy shim; guards (COLOUR-5/COMPOSITION-2/3) traced |
| templates/index.html | bug r1 | clean — esc() discipline consistent, no unguarded null reads |
| asset-forge-user/build.py | delta | clean — unbundling removal correct and well-documented |

## Confirmed + fixed this sweep (all twin-mirrored, sync_builds green, battery + harness green)
1. **HIGH concurrency.py consumer-abort re-bill window** — proof junk/hunt_test_f1_consumer_abort.py (12/12 billed pre-fix → 4/12 post).
2. **HIGH library.html boot() dead on null-priced rows** — proof junk/hunt_verify_f5.js; page unusable since model-sweep.
3. **MEDIUM library_gen.py spent_est under-reporting (G19)** — proof junk/hunt_test_spent_est.py ($0.02 shown vs $0.04 real).
4. **MEDIUM quality.py vertical-pattern false reject (wastes a paid retry)** — proof junk/hunt_verify_f14.py (detail 0.0 → rejected).

## Cross-file findings (not fixed here — need decisions)
1. **Output-knobs backend is written but UNWIRED (product contract gap).** `output_opts.py`
   ships dual-pass alpha (`alpha_from_dual`, `alpha_by_removal`, `wants_dual_render`) and SVG
   (`vectorize`) — with detailed docstrings and Damien's "give them all the knobs" mandate —
   but `check_references` shows **zero callers** for all four entry points, no UI control
   posts an `output`/`background`/`vector` param (index.html sends `mode_class` only;
   library.html sends nothing), and emblem mode's default `background: transparent` therefore
   never produces alpha. Emblems ship on their keyable backdrop, opaque. Nothing crashes —
   it is a silent feature no-op. Deferred-docket candidate: wire the knobs into both UIs +
   the two generate paths, or descope the promise.
2. **Registry drift closed:** AF-STUDIO-CONTROLS anchored `id="pupgrade"`, which DOCTRINE-4
   deliberately removed; anchor now points at the page's live G19 surface
   (`cost_with_margin`). Fixed in the same commit (harness covenant).
3. **Pre-existing, NOT this sweep's changes (verified identical on HEAD bytes via
   stash/restore):** junk/test_concurrency.py's tail resume-check hits a Windows
   `msvcrt.locking` PermissionError on `.run.lock` after the kill-simulation (the killed
   run's handle) — test-infra artifact, sections 1–7 all PASS. Also pre-existing dirty-tree
   harness rows: AF-BUNDLE-FRESH STALE (build 2026.08.01 predates the marathon — a REAL
   owed rebuild, already flagged by the harness), 7 SP-* FAILs from a locked live Spector DB
   (HEAD's committed results are all-PASS; a live app held warehouse.db during the run), and
   PS-LIB-FLAT-INSTALL undeclared-untested (pre-existing debt).

## Refuted-this-sweep highlights (recorded so later rounds skip them)
- FLAT filename collisions (seed/job-id namespacing holds), traversal via type names
  (_slug), expand_theme mid-run failure orphans (estimate-before-mkdir order), version-pinned
  404 fallback double-POST (404 is pre-bill, one retry, `"version" not in body` guard),
  _FETCH_HOSTS suffix bypass (exact-or-dot-suffix match), bundle.py trip-order, userlib
  surrogate ids, seamless feather math, schema stale-cache poisoning (only real schemas cached).

## Session lessons
- Scanner subagents thrash their context on files ≥150 lines with context packs; this
  machine's sub-agent path also intermittently routes through a credit-limited API. Run
  colibri units IN-SESSION here until that changes.
- jCodemunch does not index HTML — template review units must be Read directly; its index
  also staled mid-session once (re-index before absence claims; `index_file` needs `path=`).
