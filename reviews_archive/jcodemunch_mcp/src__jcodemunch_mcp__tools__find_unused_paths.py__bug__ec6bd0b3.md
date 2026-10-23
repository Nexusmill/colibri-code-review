# Colibri review — src/jcodemunch_mcp/tools/find_unused_paths.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\tools\find_unused_paths.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summaries, artifacts reaudit/jcm/)
- sha256: `ec6bd0b3cf712c129ccd28c2efad867b77075ab910f4da5f5b72bb97cc321890` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: the sub-agent's summary (1 CONFIRMED with a RED probe, 2 refuted); the result loop 218-266 (`break` at `max_results`, with `excluded_tests`, `excluded_entry_points` and `rescued_by_column_hit` incremented inside the same loop), the `_meta` block 280-296 (`truncated: len(results) >= max_results`, `total_unused: len(results)`); callers `server.py` and the CLI; `tests/test_runtime_phase3.py` (asserts `excluded_test_files >= 1`), `tests/test_runtime_phase4.py`. No prior `.colibri_reviews` record.

## Verdict
Every `_meta` counter stopped counting at the row where the result page filled up, so a caller reading `excluded_test_files: 0` had no way to know the scan never reached the test file. Fixed: the scan runs to the end and only the returned page is capped.

## Bugs & vulnerabilities
**[MEDIUM] Exclusion/rescue counters under-counted once the loop broke at `max_results` — CONFIRMED — FIXED** - `line 264-266, 279, 288`
- Trigger (audit probe, RED on these bytes): `max_results=1` with an unused `foo` before an unused test symbol → `excluded_test_files: 0`, `truncated: True`.
- Fix: `total_candidates` counts every candidate; `results` takes the first `max_results`; `total_unused` reports the candidates (not the page) and `truncated` is `total_candidates > max_results` (a full page with nothing behind it is no longer "truncated"). The counters now describe the whole scan.

## Refuted (recorded so they are not re-raised)
- `HAVING` string comparison across formats; dbt column rescue keyed by model name colliding: both re-traced and stand refuted.

## Adversarial verification (Phase 3)
- Pinned end to end over a real index with an injected `runtime_calls` row: `excluded_test_files == 1` past a `max_results=1` page; three candidates with `max_results=2` → two returned, `total_unused == 3`, `truncated True`; with `max_results=3` → `truncated False`. `tests/test_runtime_phase3.py`/`phase4.py` unchanged and green.

## Remediation postscript (same commit)
The fix was applied after this review hashed the bytes above; the file is now `6bbd59a559e06b2c65ce000c7274cb02eb306db30b6d69ea3650e2ca3169d62f`. TDD: `tests/test_tail_batch3_reaudit.py` (6 tests across the four units of this batch) - all 6 RED on the old bytes (each for its own reason, verified by the per-test failure), GREEN after; the audit probe passes after where one existed.
