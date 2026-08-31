# colibri-review — asset-forge/forge/library_gen.py (bug, round 3 — post-marathon delta)

- **Source:** `asset-forge/forge/library_gen.py` (byte-identical twin: `asset-forge-user/forge/library_gen.py`, G23)
- **Model:** claude-fable-5 (in-session)
- **sha256 (reviewed bytes):** `0d017eb5a55f408fd209a1b9e56ba203127dc0818d4e4c5870f1119ef312116c`
- **Date:** 2026-08-04 · **Mode:** bug (DELTA vs r2 448a8345, 2026-07-24)
- **Context pack:** hunt plan rounds r1/r2; refuted ledger (2 library_gen entries); remediation
  manifest (LG-2, LG-3, AF-CKPT-STREAM, model-sweep null-row fix all closed); delta commits:
  FLAT layout 451f70b9, output knobs 7782bc51, expand_theme routing, CKPT-STREAM 97b62cb5,
  DOCTRINE-4 4ae751e3, estimate hardening. Consumers re-traced via jCodemunch (app.py libgen
  endpoints, concurrency.imap_bounded, output_opts).

## Fixed since last review
- LG-2 manifest-on-pause — **fixed** (folded into `_write_job`, failure-isolated; verified at line 436-443).
- LG-3 lock_palette falsy re-roll — **fixed** (flag-gated at line 285-287).
- AF-CKPT-STREAM checkpoint batching — **fixed** (imap_bounded consumption at 733; battery test 7 passes).
- Off-catalog/null-row estimate — **fixed** (double guard at 316-329; refusal messages actionable).
- Malformed selection types/count — **fixed** (400-clean ValueErrors at 209-226, 251-258).

## Verdict
The marathon rework held up well under delta review — the money doctrine survives FLAT layout,
CKPT-STREAM, and DOCTRINE-4. One MEDIUM money-honesty defect confirmed and fixed (G19):
`spent_est` under-reported real Replicate spend.

## Bugs & vulnerabilities

**[MEDIUM] `spent_est` = done×price under-states real spend — billed failures and QC retries count $0** - `line 748` (pre-fix)
- **What:** the per-checkpoint spend estimate multiplied only COMPLETED items by price. Two
  billed-but-not-done cases counted zero: (1) a `BilledFailure` item — the prediction was
  created and billed, that is the definition of the class — recorded `status=failed` and $0;
  (2) a quality-floor retry bills a SECOND generation for the same item (the code's own
  comment: "it was billed either way") but only one ever entered the count.
- **Trigger/Impact:** any run with moderation rejects or floor retries shows the user less
  than they actually spent — on the UI's live "$X spent" meter, the exact surface G19 exists
  for. The estimate() pre-quote is unaffected (it quotes the plan); this is the live meter.
- **Fix (applied):** items now carry `billed_failure: true` when failing with a
  `_BilledFailure`, and `spent_est` is recomputed each checkpoint as
  `price × Σ bills(item)` where bills = done(1) + billed_failure(1) + `_qc_retry`(1).
  Recomputing from items (not a running counter) keeps a RESUMED job honest too.
- **Proof:** `junk/hunt_test_spent_est.py` — 3 items (clean success / BilledFailure /
  floor-retry-then-success) at $0.01: old code reported $0.02, fix reports $0.04 = the 4
  predictions actually created. PASS. Full battery `junk/test_concurrency.py` 1–7 PASS after.

## Phase-3 refutations (candidates traced and dropped)
- *FLAT filename collision silently overwrites* — `base = {desc}_{seed}_{jobid[:6]}`; seed is
  `_seed_for(pack,type,i)` (content-hash) so two same-type items differ by i→seed, and cross-
  run collisions differ by job_id. A same-type+same-seed+same-job collision is the SAME item.
  QC retries write a distinct `_r{seed:04x}` name by design. No reachable overwrite.
- *Path traversal via type/pack names* — `_slug()` strips to `[a-z0-9_]{1,40}` before any
  path use; theme text never reaches a filename. Sound.
- *Consumer checkpoint raise drains the paid queue* — REAL, but the defect and fix live in
  `concurrency.py` (this file's consumer is the trigger); see the concurrency.py review.
- *expand_theme failure mid-plan* — `_expand_prompts` catches everything and falls back to
  deterministic variation; `build_plan` runs before the job dir exists (estimate-first order
  verified at 398-401). No orphan.
- *`prepare_job`'s `from forge.seamless import SEAMLESS_SUFFIX` (absolute) vs relative
  imports elsewhere* — works in both dev (repo root on sys.path) and frozen builds (both
  specs bundle `forge` as a package); the `except Exception: pass` fallback still yields a
  usable (unsuffixed) prompt, and the catalog prompt_suffix already carries the tiling
  contract for library items — LOW at most, not raised.

## Missing safeguards
- `_bills()` counts at most one QC retry per item (matches the one-retry policy); if the
  retry policy ever loosens, the accounting needs the actual attempt count.
