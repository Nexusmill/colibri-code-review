# colibri-review — asset-forge/forge/concurrency.py (bug, round 1)

- **Source:** `asset-forge/forge/concurrency.py` (byte-identical twin: `asset-forge-user/forge/concurrency.py`, G23)
- **Model:** claude-fable-5 (in-session)
- **sha256 (reviewed bytes):** `2571d7f538bd2d74168f37d44b065fae0c69ac45693e96e2e367d5567011f7b5`
- **Date:** 2026-08-04 · **Mode:** bug
- **Context pack:** hunt plan + refuted ledger + remediation manifest (AF-CKPT-STREAM closed with kill-mid-run proof; junk/test_concurrency.py battery); call sites traced via jCodemunch: `library_gen.py:733` (imap_bounded, per-completion checkpoint consumer) and `bundle.py:206` (map_bounded, all-or-nothing). First-ever review of this module (created 91fb565f, fixed once 97b62cb5).

## Verdict
One HIGH money-path defect on the consumer-failure path; otherwise the module is sound and its
documented invariants (shared RateGate, cooperative Stop, caller-side single-writer) hold as
claimed. Fixed in-session with a behavioural proof.

## Bugs & vulnerabilities

**[HIGH] Consumer abort drains the queue — every still-pending item runs its PAID call with the result discarded** - `line 132-135`
- **What:** `imap_bounded`'s pooled branch yields from inside `with ThreadPoolExecutor(...)`.
  If the CONSUMER of the generator raises mid-iteration (library_gen's loop does checkpoint
  I/O — `_write_job` — and `on_progress` between items) or breaks early, the generator closes
  at the yield and the executor context manager runs `shutdown(wait=True)`, which **executes
  every not-yet-started future**. Each runs `work()` — a paid `provider.generate()` — its
  result is discarded, nothing is checkpointed, and `stop` is never tripped.
- **Trigger:** any exception in the consumer loop mid-run (disk-full/permission error on the
  job.json checkpoint, an `on_progress` callback raising), or any future consumer that
  `break`s out of the stream.
- **Impact:** on resume, all those items are still `pending` → regenerated → **re-billed for
  the entire remaining queue** (same blast radius the CKPT-STREAM fix removed on the
  crash path). Proven pre-fix: 12/12 fake-provider calls billed after the consumer raised on
  the first yield (`junk/hunt_test_f1_consumer_abort.py`, exit 1 pre-fix).
- **Fix (applied):** wrap the yield loop in `try/finally`; on abnormal close with futures
  still pending, `stop.trip("consumer", ...)` + `f.cancel()` each pending future. Cancelled
  futures never start; already-running ones finish (the same in-flight blast radius `Stop`
  already accepts). Post-fix: 4 in-flight billed, 8 spared, stop tripped (same test, exit 0).
  Battery `junk/test_concurrency.py` sections 1–7 all PASS post-fix (its only failure is the
  pre-existing test-7 tail lock issue, identical on HEAD bytes — verified by stash/restore).
- Call-site check: `bundle.py`'s `map_bounded` consumer does no I/O between yields (list
  comprehension over the returned list), so the fix changes nothing there; `library_gen`'s
  consumer gains protection with no interface change.

## Phase-3 refutations (not reported as findings)
- *Worker exceptions swallowed into the tuple* — by design; both call sites handle `exc`
  explicitly (library_gen fails the item; bundle re-raises the first error).
- *`retry_after_seconds` regex `~?(\d+)\s*s` matches "429s" → 429-second wait* — capped at
  `cap=60.0` on both branches; latent nit, no real harm path.
- *RateGate `wait` spin* — sleeps `min(remaining, 5)`; bounded, correct under the lock.
- *`resolve_workers` env parse* — `ValueError` caught; negative/zero clamped by `max(1, ...)`.

## Missing safeguards
- No test previously covered consumer-side failure; `junk/hunt_test_f1_consumer_abort.py` now
  does (kept in junk/ per the artifacts rule).
