# Colibri review — src/jcodemunch_mcp/runtime/ingest.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\runtime\ingest.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summary, artifacts reaudit/jcm/)
- sha256: `188fd431d76add6c621425d5eb5809fb84f7ac45e60154f2901ae945ed9471ec` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline, HEAD 42c30b9)
- date: 2026-09-13
- mode: bug
- context pack: jCodemunch outline + `find_importers` for otel/resolve/stack_log (callers: `runtime/__init__`, `runtime/ingest`, `runtime/stack_ingest`, `evidence/scip_ingest`); `get_symbol_source` of `_ingest_otel_iter`, `_BatchAggregator.unmapped_inc/iter_unmapped`, `_ingest_stack_iter`; the 2026-09-11 summary JSON + its RED probe re-run against current bytes; `.colibri_reviews/_manifest.json` (no prior record for this file); the repo's test idioms (`tests/test_runtime_phase0.py`, `test_runtime_phase6.py`). This is one unit of a five-file cluster remediated in ONE tranche because the five reported HIGHs share one root cause (an unbounded, untrusted line number reaching a SQLite bind).

## Verdict
No edit to this file. The reported HIGH is real as a SYMPTOM (one malformed span aborts the batch) but its root cause is the unbounded line number parsed upstream; it is fixed at the source in the commit carrying this record and pinned by an end-to-end test that drives this file's `ingest_otel_stream`.

## Bugs & vulnerabilities
**[HIGH] `_ingest_otel_iter`'s per-span resolve is unguarded; an `OverflowError` from one malformed span aborts the batch — CONFIRMED (symptom) — FIXED AT ROOT** - `line 141-146`
- What: `_resolve_with_conn(...)` is called inside the loop with no exception boundary; `_persist` runs only after the loop, so a raise discards every aggregated span.
- Root cause: `OtelSpan.line_no` could be any-size int (otel.py `_coerce_int`). With the int64 bound now applied at parse time, no span can carry a line number that overflows a bind, and `unmapped_inc`'s raw copy (line 193-195) is bounded for the same reason.
- Why NOT the sub-agent's proposed `try/except OverflowError` here: after the root fix the branch is unreachable, and a broad exception boundary around resolve would convert future real bugs into silent per-record drops (the exact "silent failure" class this campaign hunts). Root fix + end-to-end test instead.
- Verification: `test_otel_ingest_batch_survives_one_oversized_lineno` — two spans, one with a 29-digit `code.lineno`; RED on the old bytes (OverflowError at resolve.py:57), GREEN after: `records == 2`, `mapped == 2`, two `runtime_calls` rows.

**[LOW] `_persist`'s `except sqlite3.Error` does not catch `OverflowError`, skipping the explicit ROLLBACK — CONFIRMED as written, MOOT after the root fix** - `line 318`
- The connection `close()` discards the uncommitted transaction anyway (sub-agent's own note, verified: `_persist` closes in `finally`); with bounded ints the bind cannot raise `OverflowError`. No change.

## Adversarial verification (Phase 3)
- Sub-agent's "empirically confirmed: runtime_calls left empty when it should have 2" was reproduced by the end-to-end test above rather than trusted (its ad hoc script was not preserved).

## Remediation postscript (same commit)
File unchanged (sha as above). Fix landed in `otel.py` / `resolve.py`; this record closes the finding so it is not re-fixed here.
