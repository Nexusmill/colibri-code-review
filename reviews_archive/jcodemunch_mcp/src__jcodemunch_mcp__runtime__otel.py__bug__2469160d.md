# Colibri review — src/jcodemunch_mcp/runtime/otel.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\runtime\otel.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summary, artifacts reaudit/jcm/)
- sha256: `2469160d19ca150d0d5dc3ccc1f1fa53cef881effdb1bfc506ecee2632298a2c` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline, HEAD 42c30b9)
- date: 2026-09-13
- mode: bug
- context pack: jCodemunch outline + `find_importers` for otel/resolve/stack_log (callers: `runtime/__init__`, `runtime/ingest`, `runtime/stack_ingest`, `evidence/scip_ingest`); `get_symbol_source` of `_ingest_otel_iter`, `_BatchAggregator.unmapped_inc/iter_unmapped`, `_ingest_stack_iter`; the 2026-09-11 summary JSON + its RED probe re-run against current bytes; `.colibri_reviews/_manifest.json` (no prior record for this file); the repo's test idioms (`tests/test_runtime_phase0.py`, `test_runtime_phase6.py`). This is one unit of a five-file cluster remediated in ONE tranche because the five reported HIGHs share one root cause (an unbounded, untrusted line number reaching a SQLite bind).

## Verdict
The one defect is the root cause of the cluster: `_coerce_int` accepted any-size integers for `code.lineno`, which then crashed the SQLite bind two layers down. Fixed in the commit carrying this record; the rest of the file (OTLP walking, attribute flattening, `extra` scoping for the redactor) re-read end to end and clean.

## Bugs & vulnerabilities
**[HIGH] `_coerce_int` has no bound; an oversized `code.lineno` propagates to a SQLite bind and aborts the whole batch — CONFIRMED — FIXED** - `line 262-268` (pre-fix numbering)
- What: `int(value)` on the stringified OTLP attribute accepts arbitrary-precision ints; `_span_to_otelspan` (line 179) stores it on `OtelSpan.line_no`, which `_ingest_otel_iter` passes to the resolver and, for unmapped spans, `_BatchAggregator.unmapped_inc` keeps raw for `_persist` to bind into `runtime_unmapped`.
- Trigger: `{"key": "code.lineno", "value": {"intValue": "999…(20+ digits)"}}` in any ingested OTLP payload (HTTP route or file).
- Impact: `OverflowError` out of the bind — one span kills the batch (see the resolve.py record; end-to-end test `test_otel_ingest_batch_survives_one_oversized_lineno`).
- Verification: `_coerce_int` has exactly one call site (jCodemunch `search_text`: line 179, `code.lineno` only), so bounding it to int64 cannot change any other value's semantics. Unit test `test_coerce_int_bounds_to_sqlite_int64` pins both edges (2^63-1 kept, 2^63 rejected).
- Fix: `_coerce_int` now delegates to `resolve.sanitize_line_no` — one bound, one definition, shared with `stack_log.py`. A span with an out-of-range line keeps its file/function (`test_otel_span_with_oversized_lineno_keeps_the_span`) and resolves by name.

## Missing safeguards
- None new. `duration_ms` (line 187-191) also parses untrusted ints but only divides them — no bind — so it is correctly left alone.

## Adversarial verification (Phase 3)
- Tried to refute "attacker-controlled": the value is read from the request/file body with no schema validation upstream (`iter_otel_from_text` → `_extract_spans_from_record` → `_span_to_otelspan`); CONFIRMED.
- Checked the `runtime/__init__` import graph for a cycle after adding `from .resolve import sanitize_line_no`: `resolve.py` imports only stdlib; no cycle (full suite imports clean).

## Remediation postscript (same commit)
File is now `4f79d633ee451ea468d7005bf19419a015d194b26227356d0e10d94ae1b525fd`. TDD as in the resolve.py record.
