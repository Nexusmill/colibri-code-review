# Colibri review — src/jcodemunch_mcp/runtime/http_routes.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\runtime\http_routes.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summaries, artifacts reaudit/jcm/)
- sha256: `2abfec74bfca3cda49a72b45354f8c5ce957d086b07e0f26fbc3b0f72519f00a` (current bytes at dispatch, 2026-09-13; the audit baseline was 000a03aee11b, the file changed since in the import-scip tranche d9f2521 (the bounded gunzip moved to security.py) and this finding was re-verified RED on the current bytes - a delta, not a stale finding)
- date: 2026-09-13
- mode: bug
- context pack: the sub-agent's summary (1 CONFIRMED with a RED probe, 1 refuted); `_shared_handler_setup` 249-284 (gate, auth, `_resolve_repo_param` - a single `partition('/')`), `_resolve_db_path` 287-294 (`store._sqlite._db_path(owner, name)` - the store's sanitiser raises ValueError on a separator in a component) and its three unguarded call sites in `handle_otel`/`handle_sql`/`handle_stack`; every other validation failure in the module returns a JSON error. The file's own record from earlier today (the T28 alias) stands.

## Verdict
The one identifier the routes accept from the wire was validated by a sanitiser that raises, at three call sites that did not catch. Fixed once, where the identifier is parsed.

## Bugs & vulnerabilities
**[MEDIUM] A malformed `X-JCM-Repo` (a second `/`) escaped `_resolve_db_path` as an unhandled ValueError — CONFIRMED — FIXED** - `line 311, 340, 373`
- Trigger (audit probe, RED on these bytes): `X-JCM-Repo: owner/sub/thing` → `ValueError: Path separator in name: 'sub/thing'` out of `handle_otel`.
- Fix: `_shared_handler_setup` runs the store's own sanitiser once (`IndexStore(...)._sqlite._db_path(owner, name)`) right after parsing and returns a JSON 400 (`invalid repo identifier owner/name: …`) on ValueError, so all three routes are covered by the one sequence they already share; `_resolve_db_path` and the routes are untouched.

## Refuted (recorded so it is not re-raised)
- `_safe_repo_component` sanitising to a literal `.`: re-traced and stands refuted.

## Adversarial verification (Phase 3)
- Pinned through the real Starlette routes (`raise_server_exceptions=False`, ingest enabled, token set): all three endpoints answer 400 with the message for the malformed header. `tests/test_v1_108_95.py` and the runtime route tests unchanged.

## Remediation postscript (same commit)
The fix was applied after this review hashed the bytes above; the file is now `1d9c524b019197a237fa2e82b2ff247a43843d383d8b3b8748ffe78e5369ebf3`. TDD: `tests/test_tail_batch2_reaudit.py` (7 tests across the four units of this batch) - 4 RED on the old bytes, 3 controls green throughout, GREEN after; the audit probe passes after.
