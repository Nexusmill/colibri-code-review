# Colibri Review - bug (DELTA) - asset-forge/forge/library_gen.py

- **Source path:** `asset-forge/forge/library_gen.py`
- **Reviewer:** claude-fable-5-1 (in-session), Colibri G37 protocol, campaign item 1 (product cores), rank 14
- **sha256 reviewed:** `ea88d90afa638243c7229112140e29695b3c7602da66084b96b4efc51b6594cd` (sha8 `ea88d90a`)
- **Date:** 2026-09-10 · **Mode:** bug, stale-file DELTA against `1a262868` (2026-08-22 grok round-5 gate)
- **Delta reviewed:** 2 commits / 146 diff lines: 06580c2b (GROK-LG5: the quality floor inside the try so a crashed floor never re-bills, control re-read before each paid create, keying frames unlinked on every path, `seam_feather` carried into regen plans), 1ff34826 (run_job docstring names the `extra` provider kwarg) - every hunk read.
- **Context pack:** the prior review record(s) for the file, `docs/remediation_manifest.json` rows from 2026-07-24 on, `docs/deferred_manifest.json`, `_hunt_plan.json` + `_refuted_ledger.json` loaded; jCodemunch `get_symbol_source` on the symbols each finding depended on.

## Fixed since last review
- Every remediation row dated after the base review was verified present at the bytes (they are the delta).

## Verdict
Clean at the delta (twin byte-identical). A crashed floor is now recorded as a floor failure on the billed file (no resume re-bill); the shared Stop trips before a paid call when control flips; `*.black`/`*.rgba` keying frames never survive into the flat library.

## Bugs & vulnerabilities
None confirmed at the delta.

---

# FULL re-audit 2026-09-10 (appended - the record above predates the adversarial gate and is kept as history, not as baseline)

# Colibri Review - bug (FULL re-audit) - asset-forge/forge/library_gen.py

- **Source path:** `asset-forge/forge/library_gen.py` (twin `asset-forge-user/forge/library_gen.py` byte-identical at this sha, G23 - the fix applies to both)
- **Reviewer:** claude-fable-5-1 (in-session fork), Colibri G37 protocol, campaign item 1 (product cores), rank 14
- **sha256 reviewed:** `ea88d90afa638243c7229112140e29695b3c7602da66084b96b4efc51b6594cd` (sha8 `ea88d90a`) - the PRE-fix bytes
- **Date:** 2026-09-10 · **Mode:** bug, FULL review of the current bytes (owner ruling 2026-09-10: every prior record of this file - the 07-20..08-04 rounds, the 08-14 LG-4..17 tranche, the 08-22 grok round-5 gate and this morning's delta - predates the adversarial gate and is untrusted; no delta against them)
- **Context pack:** jCodemunch `get_file_outline` (34 symbols) + `find_importers` (two harness probes; app.py binds it as `_libgen`) + the twelve app.py call sites printed in full (libgen_estimate/start/regen_estimate/regen/control, `_run_libjob`, `_evict_finished_lib`, `libgen_poll`) + `get_symbol_source` on the cross-file contracts (concurrency.imap_bounded/RateGate/Stop, quality.check/prompt_wants_colour, output_opts.normalize/wants_dual_render/prompt_fragment, seamless.make_seamless, replicate_flux.BilledFailure); 39 remediation rows, 16 deferred rows and 24 features-registry rows naming the file loaded as CLAIMS; the 08-22 r5 gate record and the 09-10 delta record read; `tests/harness/probes/lg_money_resume.py` (ALL PASS on these bytes) read for the fixture pattern; catalog.json price rows listed (52 models, every row priced, none null or zero). All 1455 lines read.

## Verdict
Shippable after ONE fix. The money rules inside a run hold at the bytes (single billed attempt, BilledFailure never retried, control re-read before every paid create, per-item checkpoints, spent_est recomputed from the items, keying frames never survive). The defect is at the seam the prior reviews never exercised: the checkpoint write against the app's own poll reader on Windows - the shipped platform - which turns a routine 2-second poll into a mid-run abort and a Resume re-bill.

## Bugs & vulnerabilities

**[HIGH] The per-item checkpoint has no tolerance for the poll reader - on Windows the `replace` raises, the run aborts to `error`, and the next Resume re-bills the item(s) that were paid but never written** - `_write_job` line 661 (`tmp.replace(Path(out_dir) / "job.json")`), reached from the coordinator at lines 1298 and 1356
- What: Python's `open()` on Windows requests `FILE_SHARE_READ|WRITE` but not `FILE_SHARE_DELETE`, so `MoveFileEx(REPLACE_EXISTING)` over a file another thread currently holds open fails with `PermissionError: [WinError 5]` (verified on this machine: `win_share_test.py`). `libgen_poll` (app.py 1506) runs `load_job` -> `read_text` on `job.json` every 2 s from a Flask request thread while the job thread checkpoints after every image; `_evict_finished_lib` and `_run_libjob`'s own error handler read it too. The file is open ~0.3 ms per poll (measured, 460-item record).
- Trigger: a poll landing inside the `replace` - ~1.5e-4 per checkpoint with one poller (two tabs double it). ~7 % of 460-image runs and ~26 % of 2000-image runs hit it at least once. Reproduced deterministically in `probe_af_library_gen_1.py` with an exaggerated reader.
- Impact (traced end to end): the raise propagates out of the `for ... in imap_bounded` loop -> the generator's `finally` trips the shared Stop as "consumer" and cancels the queue (started workers finish their PAID calls and the results are discarded) -> `run_job` raises -> `_run_libjob` (app.py 1409-1431) loads the STALE on-disk job, marks it `error` and writes it -> the item that had just been generated (billed) plus every in-flight one are still `pending` on disk -> the user's Resume re-generates and re-bills up to `workers`+1 images ($0.01-$1.20 at catalog prices), after a run that stopped with an opaque "Access is denied" and needed a manual restart. Probe: 7 provider calls for a 6-image job.
- Fix (verified GREEN on a temp copy of the package, `verify_fix_lg.py`; unified snippets in `fix_af_library_gen.json`): a module-level `_replace_checkpoint(tmp, dst, budget=3.0)` that retries the `replace` on `PermissionError` every 10 ms for a bounded window and then raises, used by `_write_job`, `_write_manifest` and `_write_quality_report` (the terminal `_write_manifest` calls at 1365/1371 sit outside any try and read the same class of file from `library_types`, app.py 899). Readers hold the file for a millisecond, so the retry lands in the first gap; a reader that never lets go still surfaces (probe check 2: bounded, 0.5-15 s). Checked against every call site: no caller depends on an immediate raise; `lg_money_resume.py` unchanged in behaviour (its writes never collide).
- Verification: CONFIRMED - Windows share-mode behaviour reproduced, the coordinator/app.py/resume chain traced at the bytes, the money consequence measured (7 calls for 6 images), RED on the current bytes, GREEN on the patched copy.

## Missing safeguards (not fixed)
- `_run_job_locked` line 907: `cat["models"].get(job["model"], {}).get(...)` raises `AttributeError` when the catalog row exists but is `null` (the MODEL-SWEEP "unpriced" shape) - a job priced before a row was nulled cannot resume (the LG-6 fallback only covers a MISSING row). No null row ships today; `(... or {})` would close it.
- `estimate` line 516 refuses only a `None` price; `bundle_start` (app.py 1195) refuses `<= 0`. A `0`/negative catalog price would launch a $0.00 library run while the Studio path refuses it. No such row ships today.
- A pause/cancel/stop that lands between the white and black frames of a dual-pass item (lines 1136-1145) leaves the item `done` and permanently OPAQUE with only `alpha_error` set: nothing flags it, nothing re-runs just the black frame on Resume, and the user paid for (and was priced for) a transparent render.
- A regeneration of a flagged file whose ORIGINAL prompt carries no keyable backdrop clause is still priced as dual-pass when the regen's output knob is transparent (`prepare_regen_job` -> `estimate` 2x) but can only render once (line 1207) - an over-estimate, never an under-bill, and the estimate's `dual_pass: true` is untrue for those items.
- The `_variation()` fallback (line 274) ignores `colour_locked`: when `expand_theme` is unavailable a colour-locked type gets "vivid colors" etc. before its identity guard - degraded install only.
- `png.rename(_fdst)` for a flagged item (line 1324) is the same Windows share-mode class as the finding: a reader holding the png leaves a substandard image in the render folder unmarked ("left in place") - the poll's flagged glob never opens files and the UI learns the path only after the checkpoint, so the window is theoretical today.
- Crash window (documented, accepted): a deterministic `png` already on disk for a `pending` item is evidence of a prior billed generate that Resume ignores - it re-bills rather than adopting the file.
- Outside this unit, one sentence for the lead: `libgen_estimate` (app.py 1368) calls `build_plan` OUTSIDE its `try`, so the LG-8 fail-closed `ValueError`s (unknown pack/type, bad count) surface as a 500 from the estimate endpoint, not the 400 the comment promises - app.py's reviewer should check for a global error handler.

## Adversarial verification pass (refuted claims - deleted)
- "`_RunLock` locks byte 0 of an EMPTY `a+` file, so `msvcrt.locking` cannot refuse a second caller" - refuted: Windows byte-range locks apply beyond EOF; `runlock_test.py` shows a second PROCESS refused with the "already active" RuntimeError and a clean re-acquire after release.
- "`it.update(_upd)` races the `json.dumps` in `_write_job`" - refuted: both run on the coordinator thread in sequence; workers only return values (LG-7 holds at the bytes).
- "`prepare_job` normalizes `opts` and `build_plan` normalizes them again, so `_forced` combinations drift" - refuted: `normalize` is idempotent (`defaults_for(mode)` + update with the already-normalized dict).
- "Resume re-runs `failed` items = double bill" - refuted: the resume queue excludes `billed_failure`; a transient failure never created a prediction (the provider raises before create) so re-running is the first bill.
- "`list_flagged` attaches a wrong record by substring" - refuted: LG-15's anchored `_seed_jobid6(?:_\d+)?$` regex is present at line 720.
- "The whole-plan size is unbounded across packs x types" - refuted as a defect: `MAX_COUNT_PER_TYPE` bounds each type and the estimate endpoint prices the exact plan the user then launches (G19 satisfied); no doctrine caps the total.

## Remediation postscript (same session)
The fixes were applied after this review hashed the bytes above; the file is now `b6ee29bf06760c4893cfee65012812798ff897cf5c7de8b6f5c905622b5133bc`. Rows AF-LG-CKPT-SHARE in `docs/remediation_manifest.json`, same commit.

