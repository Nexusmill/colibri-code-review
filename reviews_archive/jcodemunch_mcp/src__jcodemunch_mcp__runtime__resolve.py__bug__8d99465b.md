# Colibri review — src/jcodemunch_mcp/runtime/resolve.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\runtime\resolve.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summary, artifacts reaudit/jcm/)
- sha256: `8d99465b1d64588d8f196b1d9674d225e76d05e71ce57a339da369d56011a681` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline, HEAD 42c30b9)
- date: 2026-09-13
- mode: bug
- context pack: jCodemunch outline + `find_importers` for otel/resolve/stack_log (callers: `runtime/__init__`, `runtime/ingest`, `runtime/stack_ingest`, `evidence/scip_ingest`); `get_symbol_source` of `_ingest_otel_iter`, `_BatchAggregator.unmapped_inc/iter_unmapped`, `_ingest_stack_iter`; the 2026-09-11 summary JSON + its RED probe re-run against current bytes; `.colibri_reviews/_manifest.json` (no prior record for this file); the repo's test idioms (`tests/test_runtime_phase0.py`, `test_runtime_phase6.py`). This is one unit of a five-file cluster remediated in ONE tranche because the five reported HIGHs share one root cause (an unbounded, untrusted line number reaching a SQLite bind).

## Verdict
Not shippable before this tranche: one malformed trace record (a `line_no` outside SQLite's int64) aborted the whole ingest batch, and the suffix fallback let `_`/`%` in an untrusted path act as LIKE wildcards. Both fixed in the commit carrying this record.

## Bugs & vulnerabilities
**[HIGH] Unbounded `line_no` reaches the SQLite bind and raises `OverflowError` — CONFIRMED — FIXED** - `line 57-67` (pre-fix numbering)
- What: `line_no` is bound directly (`(file_path, line_no, line_no)`); a Python int outside [-2^63, 2^63-1] makes sqlite3 raise `OverflowError: Python int too large to convert to SQLite INTEGER`. Nothing between here and `_ingest_otel_iter` / `_ingest_stack_iter` catches it.
- Trigger: OTLP `code.lineno` or a stack-frame line number of 20+ digits (both parsed with bare `int()` upstream, both log-shipper/attacker controlled).
- Impact: the whole batch is lost — every already-aggregated record is discarded because `_persist()` is never reached (proven end-to-end by `test_otel_ingest_batch_survives_one_oversized_lineno` and `test_stack_ingest_batch_survives_one_oversized_frame_line`, RED on the old bytes).
- Verification: probe `probe_jcm_runtime_resolve_1.py` check 1 RED against sha 8d99465b; traced the crash to the first `conn.execute` at line 57; confirmed the sub-agent note that a resolve-local guard alone is INSUFFICIENT — `_BatchAggregator.unmapped_inc` stores the caller's raw `line_no` and `_persist` binds it into `runtime_unmapped`, so the bound must live at parse time too (otel.py / stack_log.py, same tranche).
- Fix: new `sanitize_line_no()` (module-public, the single int64 bound for the whole runtime package) applied at the top of `resolve_to_symbol_id` (defence in depth: an out-of-range line becomes `None`, falling through to the function-name match) AND at every parse site in `otel.py` / `stack_log.py`.

**[MEDIUM] Unescaped LIKE metacharacters in the suffix fallback — CONFIRMED — FIXED** - `line 89-92` (pre-fix numbering)
- What: `f"%{cut}"` interpolates the raw path segment; `_` matches any single char and `%` any run, so a suffix probe for `my_module.py` also matches `myXmodule.py`, and the candidate ranking (`ORDER BY range ASC LIMIT 1`) can then attribute the record to a symbol in the wrong file.
- Trigger: any trace path containing `_` (ubiquitous in Python module names) whose exact match misses (absolute or re-rooted paths — the very case the fallback exists for).
- Impact: runtime confidence mis-attributed to a symbol that never ran. Deterministic in the test (`test_resolve_suffix_match_escapes_like_wildcards`: the decoy's smaller line range wins the ranking on the old bytes).
- Verification: reproduced through the real code path (the sub-agent's probe check 2 only re-ran a raw `LIKE` query against SQLite, so it can never turn green and is NOT evidence about this file — recorded here so nobody chases it).
- Fix: `_like_suffix()` escapes `\`, `%`, `_` and the query carries `ESCAPE '\'`. (`cut` is already backslash-free after the `replace("\\", "/")` at line 83; the backslash escape is belt-and-braces.)

## Missing safeguards
- `evidence/scip_ingest.py` also calls `resolve_to_symbol_id` with line numbers from SCIP occurrences; it is now covered by the resolver-side bound but its own parse path was not reviewed in this unit (flagged to that unit).

## Adversarial verification (Phase 3)
- Re-ran the sub-agent's RED probe against the exact bytes (sha 8d99465b): check 1 RED with the OverflowError text quoted above. CONFIRMED.
- Traced the "batch lost" consequence through `_ingest_otel_iter` (no try/except around `_resolve_with_conn`; `_persist` only runs after the loop) — CONFIRMED, and covered by an end-to-end test rather than trusted from the probe.
- Attempted to refute the LIKE finding as "harmless because the exact match runs first": the exact match misses precisely for absolute/re-rooted paths, which is the documented purpose of the fallback — the finding stands. CONFIRMED.
- Considered whether escaping could break real suffix matches: `_like_suffix` only escapes metacharacters and keeps the leading `%`, so literal paths still suffix-match; the existing `test_resolve_suffix_match_for_absolute_paths` stays green.

## Remediation postscript (same commit)
The fixes were applied after this review hashed the bytes above; the file is now `e1e0bd361d77038180ef2e63036a9a55299b8d0e40b35fdc7fc331f7fe766581`. TDD: `tests/test_runtime_line_no_bounds.py` (10 tests) RED on the old bytes — the two resolve tests failed with the OverflowError and the decoy attribution respectively — GREEN after; the 527 runtime/resolve/stack/otel/scip tests already in the suite stay green.
