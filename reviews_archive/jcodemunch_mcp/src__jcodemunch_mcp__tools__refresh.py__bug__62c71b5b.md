# Colibri review — src/jcodemunch_mcp/tools/refresh.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\tools\refresh.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summaries, artifacts reaudit/jcm/)
- sha256: `62c71b5bdd9944ffab14774aaeaf3ed26f9cb4e71afbf08135fdf368f57ebccd` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: FRESH PASS (the sub-agent's record was PARTIAL - credits ran out - with one unprobed PLAUSIBLE and one hypothesis its own probe did not confirm); the whole file read end to end: `_read_state`/`_write_state` 67-84, `run` 214-332 (read → slice → write of one cursor file per repo, no mutual exclusion), `_finish` 335-378 (stamps `parser_generation` only when the manifest is exhausted, the corpus has not grown and `errors` is empty); the CLI wiring `server.py` 9338-9366 (`--batch-size` is a free int); `tests/test_refresh_campaign.py` (37). The module's own ⚠⚠ contract: a campaign that stamps early is the index_store bug with a scheduler in front of it. No prior `.colibri_reviews` record.

## Verdict
The cursor file had no owner: two overlapping slices for one repo could drop each other's recorded batch errors and let `_finish` stamp over files never re-parsed - the one outcome the module forbids. One slice at a time per repo now, and a zero batch size is refused instead of counted.

## Bugs & vulnerabilities
**[LOW-MEDIUM] No mutual exclusion between concurrent `run()`s for the same repo — CONFIRMED by construction (was PLAUSIBLE) — FIXED** - `line 252-253, 330`
- Trace: run A and run B both read cursor c; A's batch fails and A writes `errors=[...]`; B (started from the same state object) writes after A with `errors=[]` → the next slice exhausts the manifest and `_finish` stamps. Also duplicate work, `.json.tmp` collisions on the shared temp name, and a cursor regression. Overlap is the operator's own scheduler scenario (a cron slice still running when the next fires, or a manual run beside it).
- Fix: `_acquire_lock` (`O_CREAT|O_EXCL` on `<state>.lock` holding pid/started_at/max_seconds and a random `token`) around the slice; a second run returns `success: False` naming the holder. A lock is stale only when it has gone UNTOUCHED for its holder's budget + `LOCK_GRACE_SECONDS` (300) - age measures silence, not elapsed time, because the module's own docstring says a running parse cannot be preempted. The holder heartbeats from a daemon thread (`_Heartbeat`, every `LOCK_HEARTBEAT_SECONDS` = 15) for as long as it runs - during a batch too - and touches once more at the top of each batch. Touch and release act only on a lock carrying OUR token; if the lock stops being ours (broken as stale and re-taken), the slice stops with `stopped_because: "lock_lost"`, `success: False`, and does NOT write its cursor - writing it would be the two-writer corruption the lock exists to prevent. The slice body moved to `_run_slice` otherwise unchanged.
- **Gate round 1 (gate_20260913-232653) caught my first form of this - EV-081.** The heartbeat fired only between batches, so one long batch (`batch_size` is an unbounded CLI int; slow storage is the module's target) could go silent past budget + grace and have its LIVE lock broken - re-enabling the exact defect; and `_release_lock` unlinked unconditionally, so a finished run deleted its successor's lock (ABA) and a third run started beside the second. My gate context had claimed a live slice "cannot overshoot by much" - the module's own docstring says otherwise. Both were RED on the round-1 bytes and are pinned now.

**[LOW] `batch_size <= 0` produced a silent no-op slice labelled `stopped_because: "complete"` — CONFIRMED — FIXED** - `line 234-235, 277-280`
- `min(batch_size, …)` ≤ 0 → empty batch → `break` with the default label; the state still counted a slice. `--batch-size` is an unvalidated CLI int. Fix: refused with the other budgets.

## Refuted (the sub-agent's second hypothesis, by its own probe and re-traced here)
- "A file deleted mid-campaign leaves a permanent `batch_errors` stamp block": `index_folder(paths=[<deleted>])` returns success, the campaign completes and stamps (`already_current` in the probe because the generation was current). Not a defect.

## Noted, not fixed (design, Damien's call)
- A campaign that recorded ANY batch error can never stamp without `reset=True` (which re-enumerates and re-parses from zero - the maintenance event the tool exists to avoid). A retry-once policy for failed batches would converge on transient failures; refusing to stamp on persistent ones stays right.

## Adversarial verification (Phase 3)
- Pinned: a live lock → refusal naming pid 4242, lock intact, no campaign started; a lock untouched past budget + grace → broken, the slice runs to completion, lock gone; a lock started long ago with a tiny budget but touched just now is NOT stale and still refuses; at least one touch per batch; a 0.6 s batch with the heartbeat at 0.05 s → the thread touches DURING the batch (≥ 5 touches for one batch); the lock replaced by a foreign token mid-batch → `lock_lost`, `success: False`, cursor still 0 / slices 0 on disk, the foreign lock untouched by our release; the lock is released after a slice and after a budget refusal; `batch_size=0` → error, no state written. `tests/test_refresh_campaign.py` (37) unchanged and green.

## Remediation postscript (same commit)
The fix was applied after this review hashed the bytes above; the file is now `c6243cf676695ce7e1fa3a1796e0f3c781ce158e7517e66a3426687e66077708`. TDD: `tests/test_refresh_reaudit.py` - 8 tests: 4 RED on the old bytes (three by the missing lock API, one by the accepted zero batch); the heartbeat pair; the in-batch heartbeat thread and the lock-lost refusal (RED on the round-1 bytes, the gate's catches), GREEN after.
