# Colibri review — src/jcodemunch_mcp/evidence/scip_ingest.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\evidence\scip_ingest.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summaries, artifacts reaudit/jcm/)
- sha256: `4857be9f4792b1b1b1505a77bbe7c14dd963bb44d7608b4eeec1a803c429576d` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: the sub-agent's summary (1 CONFIRMED sharing scip.py's probe, 1 PLAUSIBLE, 3 refuted); `ingest_scip_file` 101-113 (hands `file_path` straight to `parse_scip_file`; `max_rows` is the only size-shaped parameter and caps rows written after parsing); its sole production caller `tools/import_scip.py` (acquires the `indexwrite` process lock around the call, catches FileNotFoundError/ValueError); `_apply_fifo_eviction` and `_persist` for the refuted claims; `tests/test_scip_evidence.py`. No prior `.colibri_reviews` record.

## Verdict
Same root cause as `evidence/scip.py`: the orchestrator had no way to bound the input it handed to the parser. It now carries the knob through; the guard itself lives in the reader.

## Bugs & vulnerabilities
**[HIGH] `ingest_scip_file` passed an unbounded path to `parse_scip_file` with no size check — CONFIRMED — FIXED (in the reader; the knob is threaded here)** - `line 113`
- Fix: `ingest_scip_file(..., max_bytes: Optional[int] = None)` → `parse_scip_file(file_path, max_bytes=max_bytes)`; None resolves to the `scip_import_max_bytes` config (default 256 MiB). The docstring now distinguishes `max_rows` (rows written) from `max_bytes` (input read). The audit probe's fifth check looked for a `SIZE`/`MAX_BYTES` name in `dir(scip_ingest)`; the knob is a parameter plus a config key, which that heuristic cannot see - the behavioural check (a bomb refused through `ingest_scip_file`) is what the battery pins.

## Deferred / PLAUSIBLE (not fixed here)
- `ingest_scip_file` is callable without the `indexwrite` process lock its only production caller acquires. No second live caller exists; a race needs one. Recorded, not fixed (the lock belongs at the call site that owns the repo id, as today).

## Refuted (recorded so they are not re-raised)
- `_apply_fifo_eviction`'s f-string table name: iterates the fixed literal tuple, never input.
- A non-`sqlite3.Error` inside `_persist` skipping ROLLBACK: closing a connection with an open transaction discards it; no durable partial write.
- `doc.relative_path` traversal into the `files` lookup: a pure sqlite query.

## Adversarial verification (Phase 3)
- Pinned end to end: `ingest_scip_file(db_path=..., file_path=<bomb>, max_bytes=1 MiB)` raises the cap ValueError before any database is touched (the db path does not need to exist to prove it - parsing precedes `connect_readonly`).
- `tests/test_scip_evidence.py` (25) unchanged and green with the battery.

## Remediation postscript (same commit)
The fix was applied after this review hashed the bytes above; the file is now `981f7668c683c2daf12d7e81253cd9640b84299756ee92e48c6448d071262a1e`. TDD: `tests/test_scip_import_cap_reaudit.py` (7 tests; the battery imports the new names, so it is RED by ImportError on the old bytes - the audit probe `probe_jcm_evidence_scip_1.py` is the behavioural reproducer: 4/5 FAIL before; after, its two behavioural checks PASS with the cap set below its 64 MiB bomb (`JCODEMUNCH_SCIP_IMPORT_MAX_BYTES=33554432` - under the 256 MiB default the bomb is simply under the cap and is materialised, bounded), and its two remaining checks look for a `SIZE`/`MAX_BYTES` substring in `dir()` of each module, a naming heuristic the knob (`get_max_scip_import_bytes` + a config key + a parameter) does not satisfy by construction - recorded, not gamed). Supporting edits in the same commit: `security.py` gains `DEFAULT_MAX_SCIP_IMPORT_BYTES` / `get_max_scip_import_bytes` (the `get_max_response_bytes` shape) and `bounded_gunzip` (moved verbatim from `runtime/http_routes.py`, which now imports it and rebinds the old name at module level - `_bounded_gunzip = bounded_gunzip` - so `tests/test_v1_108_95.py` still reaches it; the gate's pre-review removed-symbol check refused round 1 because it does not count an `import … as` alias as a binding - EV-077, the assignment form is the fix); `config.py` gains `scip_import_max_bytes` at its four sites (env map, defaults, types, the JSONC template comment).
