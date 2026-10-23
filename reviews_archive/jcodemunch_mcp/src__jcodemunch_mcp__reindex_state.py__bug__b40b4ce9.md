# Colibri review — src/jcodemunch_mcp/reindex_state.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\reindex_state.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summary, artifacts reaudit/jcm/)
- sha256: `b40b4ce913f01509c68a619ada5573475fe6da08ca0fad26bfad2e65cd3edbc0` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: `_RepoState.fatal` 55-57 ("surfaced immediately, bypassing the 2-failure tolerance"), `_get_state` 81-89 (creates state + a SET event + a lock per new repo id), `mark_reindex_failed(..., fatal=)` 147-170, `get_reindex_status` 198-205 (honours `fatal`), `await_freshness_if_strict` 246-265 (`_get_state(repo)` for any id), `wait_for_fresh_result` 270-328 (refuses phantom state at 291-294, but both persistent-failure checks at 301 and 320 test `consecutive_failures >= 2` only); the four reindex/freshness test files (82 tests); the audit probe re-run on these bytes (2/3 FAIL). No prior `.colibri_reviews` record.

## Verdict
Two functions in one module disagreed about what "persistently failed" and "known repo" mean. Both confirmed and fixed to the rule the module already states.

## Bugs & vulnerabilities
**[MEDIUM] `wait_for_fresh_result` ignored the `fatal` flag `get_reindex_status` surfaces immediately — CONFIRMED — FIXED** - `line 301, 320`
- What: `mark_reindex_failed(..., fatal=True)` sets `state.fatal` and the event; `get_reindex_status` reports `reindex_fatal` at once, but both branches of `wait_for_fresh_result` required two consecutive failures, so a caller waiting on a fatally failed repo was told `fresh: True` (probe: status says fatal, wait says fresh).
- Fix: both branches use the status function's rule - `reindex_error and (fatal or consecutive_failures >= 2)`; a single transient failure is still tolerated (pinned).

**[LOW] `await_freshness_if_strict` created phantom per-repo state for never-indexed ids — CONFIRMED — FIXED** - `line 260-263`
- What: `_get_state(repo)` for any id the caller passed - a mistyped or never-indexed repo left a `_RepoState`, an event and a lock behind (`has_any_reindex_state()` True) for the life of the process; `wait_for_fresh_result` already refused to do this. The phantom event started SET, so no stall - growth only.
- Fix: unknown repo -> return True without creating anything, the same rule as `wait_for_fresh_result`; a known repo still waits on its event (pinned with a timer that completes the reindex mid-wait).

## Refuted (sub-agent's own, re-checked and agreed)
- A `mark_reindex_start` vs deferred-summarize deadlock: every acquisition in this module follows `deferred_save_lock -> _states_lock`; no inversion.
- `stale_since_ms` going negative: `time.monotonic()` is non-decreasing by contract.

## Adversarial verification (Phase 3)
- Fatal-before-wait and fatal-DURING-wait (a `threading.Timer` fails the reindex 50 ms into a 2 s wait) both return `reindex_failed`; a single transient failure still returns fresh (the tolerance is not widened by accident).
- Strict mode: an unknown id leaves `has_any_reindex_state()` False and no event; a known id still blocks until `mark_reindex_done` sets the event.
- `tests/test_reindex_state*.py` + freshness tests (82) unchanged: 87 passed with the battery.

## Remediation postscript (same commit)
The fixes were applied after this review hashed the bytes above; the file is now `ce5b824656e5c10b06736f5d97b38626405370946fe779bb479760fd4e500f7a`. TDD: `tests/test_reindex_state_reaudit.py` (5 tests) - 3 RED on the old bytes, 2 controls green throughout, GREEN after; the audit probe ALL PASS.
