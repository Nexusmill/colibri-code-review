# Colibri review — src/jcodemunch_mcp/runtime/stack_log.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\runtime\stack_log.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summary, artifacts reaudit/jcm/)
- sha256: `d27fea59cd1b0bbf2bca0da7adae62448536e5d0ceb922f643f6ea20b974092b` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline, HEAD 42c30b9)
- date: 2026-09-13
- mode: bug
- context pack: jCodemunch outline + `find_importers` for otel/resolve/stack_log (callers: `runtime/__init__`, `runtime/ingest`, `runtime/stack_ingest`, `evidence/scip_ingest`); `get_symbol_source` of `_ingest_otel_iter`, `_BatchAggregator.unmapped_inc/iter_unmapped`, `_ingest_stack_iter`; the 2026-09-11 summary JSON + its RED probe re-run against current bytes; `.colibri_reviews/_manifest.json` (no prior record for this file); the repo's test idioms (`tests/test_runtime_phase0.py`, `test_runtime_phase6.py`). This is one unit of a five-file cluster remediated in ONE tranche because the five reported HIGHs share one root cause (an unbounded, untrusted line number reaching a SQLite bind).

## Verdict
Two real defects, both fixed in the commit carrying this record: the JSON-Lines path silently dropped every JVM and Node.js stack (regexes anchored without `re.MULTILINE`), and six `int()` parse sites accepted unbounded line numbers (the cluster's root cause, stack-frame flavour).

## Bugs & vulnerabilities
**[HIGH] `_JVM_AT_LINE` / `_NODE_AT_LINE` compiled without `re.MULTILINE` — JSON-Lines JVM/Node traces yield zero frames and the event is discarded — CONFIRMED — FIXED** - `line 221, 230-237` (pre-fix numbering)
- What: `_parse_frames` (the structured-log path, line 457/470) runs `.finditer()` over the whole multi-line `stack_trace` string; with `^`/`$` anchors and no MULTILINE the pattern can only match at absolute position 0 / end, so no `at …` line after the header ever matches. `_event_from_json_obj` then returns `None` (line 206-207) and the record is dropped — no `runtime_stack_events` row, no unmapped row, no diagnostic.
- Trigger: any JSON-Lines / array log whose `stack_trace` is a JVM or Node.js trace (the normal shape for those runtimes).
- Impact: silent 100% data loss for JVM/Node structured logs. Python traces were unaffected (`_parse_frames` line 447 has no anchors) — confirmed by reading, matching the sub-agent's note.
- Verification: probe `probe_jcm_runtime_stack_log_1.py` RED (3/3) on sha d27fea59, ALL PASS after the fix. The plain-text path (`_parse_jvm_block`/`_parse_node_block`, `.match()` per already-split line) is unchanged by MULTILINE — lines from `splitlines()` contain no newline, so the anchors behave identically; the existing phase-5 stack tests stay green.
- Fix: `re.MULTILINE` on both compiled patterns.

**[HIGH] Six `int(m.group(...))` sites accept unbounded line numbers — CONFIRMED — FIXED** - `line 301, 343, 378, 450, 460, 473` (pre-fix numbering)
- What: every dialect's `\d+` capture is coerced with bare `int()`; a 20+ digit line number becomes `StackFrame.line_no`, reaches `_ingest_stack_iter` → `resolve_to_symbol_id` (bind → `OverflowError`), and for unmapped frames is kept raw by `unmapped_inc` for the `runtime_unmapped` bind.
- Trigger: `at com.x.A.b(A.java:9999999999999999999999)` (or the Python/Node equivalents) in any ingested log.
- Impact: the whole stack batch is lost (`test_stack_ingest_batch_survives_one_oversized_frame_line`, RED on the old bytes).
- Fix: every site now uses `resolve.sanitize_line_no` (int64 bound, `None` on overflow — the frame keeps its file/function and resolves by name). The two Node sites' `try/except ValueError` became redundant and were folded into the helper (which also catches `TypeError`/`OverflowError`).

## Missing safeguards
- None new; the file/function strings are bounded by the regexes' structure and are only ever bound as TEXT.

## Adversarial verification (Phase 3)
- Refutation attempt for MULTILINE: "the JSON path is rarely used" — `_parse_json_lines` is the documented `.jsonl/.json/.ndjson` dispatch in `parse_stack_log_file` and the `fmt='jsonl'`/auto path of `iter_stack_from_text` (the HTTP route's entry point); it is a primary path, not a corner. CONFIRMED.
- Checked that MULTILINE cannot create false frames in `_parse_frames`: `.+?`/`[^):]+` can technically span a newline, but only when a frame line is itself malformed; the four new JVM/Node frame tests assert exact file/line/function tuples and pass.
- The sub-agent reported this as "HIGH × 3"; it is ONE defect observed through three probe angles, recorded once.

## Remediation postscript (same commit)
File is now `39ae18bfdfbf44bc72a94c5826025ed2d00d3746b04cd759ca91b600432265ac`. TDD: `test_json_lines_jvm_trace_yields_frames`, `test_json_lines_node_trace_yields_frames`, `test_parse_frames_bounds_line_numbers_in_every_dialect`, `test_plain_text_blocks_bound_line_numbers` RED on the old bytes, GREEN after.
