# Colibri review — src/jcodemunch_mcp/server.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\server.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summary, artifacts reaudit/jcm/)
- sha256: `36a7fd0067d3a3798f44dfa0910c07e7cb08a6e66883ebe68555b7f3616e1269` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline; 10.6k lines — above the jCodemunch index cap, so navigation was by the summary's line numbers + Grep on the file)
- date: 2026-09-13
- mode: bug
- context pack: `_coerce_arguments` (1071-1100) and the coercion/validation site in `_call_tool_impl` (5304-5314); `_ensure_tool_schemas` (1115-1125) and `_build_tools_list`'s `_RAW_CATALOG` / `_DECLARED_ARG_KEYS` snapshot (4354-4371, taken before profile filtering and before the compact-schemas strip); `_declared_arg_keys` (392-402); `_handle_order` / `_handle_route` (5099-5110, 5134-5176) and `counter.shape_execute_args`; the two telemetry write sites (6877-6880, 7032-7035) and `_ANNOTATION_ONLY_WRITERS` (1179-1186); `_make_auth_middleware` (7250-7269); `tests/test_counter.py` for the surface/catalog reset idiom; the five audit probes re-run against these bytes (all RED). No prior `.colibri_reviews` record.

## Verdict
Five real defects, all fixed in the commit carrying this record. The two HIGHs share a root: the dispatcher's argument contract was derived from what a session could SEE (`list_tools()`), not from what the server can DISPATCH — so the hidden front door and any tool made visible after the first call ran uncoerced and unvalidated. One change closes both.

## Bugs & vulnerabilities
**[HIGH] `order`/`route` consent read from a truthy string — `bool("false") is True` — CONFIRMED — FIXED** - `line 5106, 5141` (pre-fix numbering)
- What: under the default `tool_surface=full` the front door is hidden from `list_tools()`, so `_TOOL_SCHEMAS` (built from that list) had no entry for `order`/`route`; `_call_tool_impl` skipped `_coerce_arguments` and `jsonschema.validate` for them, and `bool(arguments.get("allow_state_change"))` turned the string `"false"` into consent. A caller explicitly refusing got a state-changing action dispatched (probe 1: `invalidate_cache` ran).
- Fix: schemas now come from `_RAW_CATALOG` (below) so `"false"` is coerced to `False` and anything else fails validation; and `_handle_order`/`_handle_route` accept only a real `True` (`is True`) as defence in depth — the sub-agent's string-parsing snippet would have re-implemented the coercion the schema already provides.

**[HIGH] `_TOOL_SCHEMAS` built from the profile-filtered `list_tools()` and cached for the process — CONFIRMED — FIXED** - `line 1115-1125` (pre-fix numbering)
- What: the first call in a `core`-profile process snapshotted only core tools; after `set_tool_tier("full")` widened the session, a full-only tool (`get_extraction_candidates`) was visible but had no schema — a call with a missing required field and a wrong-typed one reached the handler instead of returning `Input validation error` (probe 3).
- Fix: `_ensure_tool_schemas` builds from `_RAW_CATALOG` — every dispatchable tool, front door included, independent of tier or surface. The sub-agent proposed invalidating the cache on tier change; that keeps the wrong dependency and is per-process while tiers are per-session, so a narrow session could still strip validation from a wide one. Tier-independence is the root fix.

**[MEDIUM] Any call could redirect telemetry's mkdir + sqlite write to a caller-named directory via an undeclared `storage_path` — CONFIRMED — FIXED** - `line 6879, 7032` (pre-fix numbering)
- What: both write sites read `arguments.get("storage_path")` for every tool, including unknown tool names (the `finally` block runs regardless). With `perf_telemetry_enabled`, `_call_tool_impl("no-such-tool", {"storage_path": X})` created `X/telemetry.db` (probe 2).
- Fix: `_declared_storage_path(name, arguments)` returns the argument only when the tool's declared inputSchema has a `storage_path` property (`_declared_arg_keys`, the same contract `list_tools` publishes); everyone else persists to the configured store.

**[LOW] `suggest_corrections` published `readOnlyHint=True` while `apply_weights=true` persists `tuning.jsonc` — CONFIRMED — FIXED** - `line 1179-1181`
- Added to `_ANNOTATION_ONLY_WRITERS` (dual-mode tools: read by default, write under a flag; conservative direction per the block's own comment). The write itself is legitimate and stays; the annotation now discloses it.

**[LOW] Non-ASCII `Authorization` header crashed `BearerAuthMiddleware` with `TypeError` instead of a 401 — CONFIRMED — FIXED** - `line 7261-7262`
- `hmac.compare_digest` refuses non-ASCII `str`; comparison now runs on UTF-8 bytes inside a `try`, with any `TypeError`/`UnicodeError` treated as unauthorized. Not a bypass (the sub-agent's own refutation, re-traced: the exception fired before either branch), an availability defect.

## Refuted (sub-agent's own, re-checked and agreed)
- Globally-disabled tools callable by name — `is_tool_disabled(name, repo=…)` at call time merges global + project.
- Idle-timeout task GC'd mid-sleep — the pending `TimerHandle` holds the reference in CPython.
- The auth crash as a bypass — traced; it is fail-closed.

## Adversarial verification (Phase 3)
- Every finding was reproduced through the REAL dispatcher entry point (`_call_tool_impl`) with only the recursive dispatch stubbed, not through the handlers directly; the `route` test first proves a real `True` executes before asserting the string does not (so it cannot pass vacuously — its first draft did).
- Confirmed `_RAW_CATALOG` is captured BEFORE both the surface collapse and the profile filter (4357 vs 4372/4387), so it is the complete dispatchable set; and that the compact-schemas strip mutates those dicts identically for `list_tools()`, so the raw-catalog build is at least as complete as the old one for every tool and strictly more complete for hidden ones.
- Checked that `is True` cannot regress a legitimate caller: MCP arguments are JSON, a JSON `true` arrives as `True`, and `"true"` is coerced by the schema before the handler runs (`test_order_still_dispatches_on_real_consent`).
- Ran the 459 server/counter/tier/http tests after the change — unchanged.

## Remediation postscript (same commit)
The fixes were applied after this review hashed the bytes above; the file is now `5d84aa174e9c659cb74c3eaaceb0bfce1fa29ab83098389a8069f6b70a129cfd`. TDD: `tests/test_server_reaudit.py` (9 tests) — 7 RED on the old bytes for exactly the five findings (the string-consent, tier-widen, telemetry-path, annotation and auth cases), GREEN after; probes 2 and 5 ALL PASS, probes 1/3/4's remaining FAIL lines are their own bug-precondition checks (now false because the bug is gone) and a `bool("false") is False` language demonstration.


## Postscript 2026-09-13 (handoff tranche, cross-file)
The search_symbols / get_ranked_context yield hook records the repo each served id came from and the finalize_handoff dispatch asks the tracker for the handoff's repo only, both through `_served_repo_key` (canonical owner/name when the id resolves, the caller's string otherwise) - closing the cross-repo attestation hole recorded in `src__jcodemunch_mcp__handoff.py__bug__65cf7f02.md`. File now `3e22e446826b42a2259c0f53fd4893aa6fefc0d0d590a48681b2459362be43b6`.
