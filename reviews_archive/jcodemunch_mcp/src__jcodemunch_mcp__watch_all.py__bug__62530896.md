# Colibri review — src/jcodemunch_mcp/watch_all.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\watch_all.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summaries, artifacts reaudit/jcm/)
- sha256: `625308969c31bd1f435b6b1c9205e7b7e03b8fa8ed3f6c661e428035d1c6aabb` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: the sub-agent's summary (1 CONFIRMED with a RED probe, 2 refuted); `watch_all` 80-186: the `asyncio.wait(FIRST_COMPLETED)` over the rediscover task, the manager task and the stop event, the `except (KeyboardInterrupt, CancelledError): pass`, the teardown in `finally`; the sole caller `server.py` (`asyncio.run(watch_all(...))`, which turns an exception into a non-zero exit). No prior `.colibri_reviews` record.

## Verdict
`FIRST_COMPLETED` returns for a task that failed just as it does for one that finished; the manager dying looked like a clean stop, the daemon exited 0, and nothing re-indexed until a human noticed. Fixed: the crash is re-raised after the teardown.

## Bugs & vulnerabilities
**[MEDIUM] A crash in `WatcherManager.run()` was swallowed and the daemon exited 0 — CONFIRMED — FIXED** - `line 164-172`
- Trigger (audit probe, RED on these bytes): a manager whose `run()` raises → `watch_all` returns None.
- Fix: after the wait, if the manager task is in `done`, was not cancelled and holds an exception, it is kept and raised after the `finally` teardown completes (folders removed, tasks cancelled) - so the process still cleans up and then exits non-zero through `asyncio.run`. Ctrl+C (a cancellation of the awaiting task) still returns normally (control).

## Refuted (recorded so they are not re-raised)
- The `stop_event.wait()` task never cancelled (it is in `pending` and cancelled there); duplicate discovered paths: both stand refuted.

## Adversarial verification (Phase 3)
- Pinned with a fake manager whose `run()` raises → `RuntimeError` propagates out of `asyncio.run(watch_all(...))`; control: a quiet manager cancelled from outside returns normally within the timeout.

## Remediation postscript (same commit)
The fix was applied after this review hashed the bytes above; the file is now `d5b6c6d868dc1cbd2bc2bcbea25f19699b2ed02440a5a9431ea2b013d381f3eb`. TDD: `tests/test_tail_batch2_reaudit.py` (7 tests across the four units of this batch) - 4 RED on the old bytes, 3 controls green throughout, GREEN after; the audit probe passes after.
