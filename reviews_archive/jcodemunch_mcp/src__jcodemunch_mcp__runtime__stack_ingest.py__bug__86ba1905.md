# Colibri review — src/jcodemunch_mcp/runtime/stack_ingest.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\runtime\stack_ingest.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summary, artifacts reaudit/jcm/)
- sha256: `86ba1905f2e83b384d94eca1542c1c290bf7363dfe74dc412a1eb3f1d1ebb5a4` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline, HEAD 42c30b9)
- date: 2026-09-13
- mode: bug
- context pack: jCodemunch outline + `find_importers` for otel/resolve/stack_log (callers: `runtime/__init__`, `runtime/ingest`, `runtime/stack_ingest`, `evidence/scip_ingest`); `get_symbol_source` of `_ingest_otel_iter`, `_BatchAggregator.unmapped_inc/iter_unmapped`, `_ingest_stack_iter`; the 2026-09-11 summary JSON + its RED probe re-run against current bytes; `.colibri_reviews/_manifest.json` (no prior record for this file); the repo's test idioms (`tests/test_runtime_phase0.py`, `test_runtime_phase6.py`). This is one unit of a five-file cluster remediated in ONE tranche because the five reported HIGHs share one root cause (an unbounded, untrusted line number reaching a SQLite bind).

## Verdict
No edit to this file. The sub-agent reported the finding "by code identity" with `ingest.py` and explicitly did not probe it; this unit probes it and confirms the same shape, fixed at the root (stack_log.py line bounds + resolve.py guard) in the commit carrying this record.

## Bugs & vulnerabilities
**[HIGH] `_ingest_stack_iter`'s per-frame resolve is unguarded — reported PARTIAL/by-identity, NOW CONFIRMED by a direct probe — FIXED AT ROOT** - `line 150` (`sid = _resolve_with_conn(db_path, frame.file_path or "", frame.line_no, frame.function_name)`)
- What: identical structure to `ingest.py` (`get_symbol_source` of `_ingest_stack_iter` read in full): no exception boundary per frame, `_persist` after the loop, `unmapped_inc(frame)` keeps the raw `line_no`.
- Verification: `test_stack_ingest_batch_survives_one_oversized_frame_line` drives THIS file's `ingest_stack_log_stream` with a Python traceback whose second frame has a 29-digit line — RED on the old bytes (OverflowError at resolve.py:57, both frames lost), GREEN after (`records == 1`, `frames == 2`, `mapped == 2`).
- Fix: at the source (`stack_log.py` now bounds every parsed line number; `resolve.py` sanitizes on entry). No local try/except, for the reason given in the ingest.py record.

## Refuted (sub-agent's own, kept so it is never relitigated)
- "Docstring says FIFO eviction covers 4 tables but `_apply_fifo_eviction` handles 3 (missing `runtime_columns`)" — this file never writes `runtime_columns` (SQL ingest owns it); refuted by the sub-agent, re-checked against the outline here (`_apply_fifo_eviction` line 318-340 trims calls/unmapped/stack_events), agreed.

## Remediation postscript (same commit)
File unchanged (sha as above).
