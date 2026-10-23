# Colibri review — src/jcodemunch_mcp/runtime/sql_ingest.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\runtime\sql_ingest.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summary, artifacts reaudit/jcm/)
- sha256: `4f456fbfa45317f1d4dc181409c37954a8569c9a5dbf5e464d2b6d1eba95cb0a` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: `get_symbol_source`-level read of the redaction branch that calls `_build_record` a second time; the sub-agent's summary ("fix belongs entirely in sql_log.py"); this file's own note that it resolves by table/model name, so the resolve.py line-number cluster does not apply here (verified by reading the resolver call).

## Verdict
No edit to this file. The reported HIGH is the `sql_log.py` regex blowup counted twice per row (redaction re-runs `_build_record`); it is closed by the linear extractor landed in the commit carrying this record.

## Bugs & vulnerabilities
**[HIGH] Doubles per-row exposure to `_SELECT_LIST_RE`'s blowup by re-calling `_build_record` on the redacted text — CONFIRMED (as an amplifier) — FIXED AT ROOT** - `line 154`
- With extraction now linear (`sql_log._select_list`), the second call costs a second linear scan — no longer a vector. The double call itself is by design (columns must be re-extracted from the redacted text that is actually persisted); not changed.

## Remediation postscript (same commit)
File unchanged (sha as above). Fix landed in `runtime/sql_log.py`; this record closes the x-ref so it is not re-fixed here.
