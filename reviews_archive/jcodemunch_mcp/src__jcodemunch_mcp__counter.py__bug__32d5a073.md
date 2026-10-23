# Colibri review — src/jcodemunch_mcp/counter.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\counter.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summary, artifacts reaudit/jcm/)
- sha256: `32d5a073af277ce7b91fc5c210eb3832eb42785ad8c7430d19b6ea36db98e1d9` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: `_FORBIDDEN_VERB_RE` 59-63 (the charter tripwire: "``order`` refuses to dispatch any action whose name matches one of these verbs, even if such a tool were somehow added to the catalog later"), `forbidden_reason` 70-78, `order_gate` 81-110 (structural -> charter -> policy), `example_for` 226-229 (`dict(ex)` defensive copy) vs `catalog_entry` 232-243 (bare alias), the server's `_handle_order` (consent `is True`, this session's server tranche) which routes through `order_gate`; the live catalog (94 tools with `JCODEMUNCH_TOOL_SURFACE=full`) swept against the old and new rule; `tests/test_counter.py` (69) + `test_retrieval_counterfactual.py`; the audit probe re-run on these bytes (3 bypasses of 15 checks). No prior `.colibri_reviews` record.

## Verdict
The charter tripwire matched bare verbs only, so an inflected verb walked through the read-only dispatch surface. Fixed with an inflection-aware rule that keeps the word boundary; a sibling aliasing inconsistency hardened alongside.

## Bugs & vulnerabilities
**[HIGH] the exec/mutation tripwire is bypassed by a suffix glued onto a verb — CONFIRMED — FIXED** - `line 59-63`
- What: `(verb)($|[._-])` requires a separator or end right after the verb, so `execute_python_code`, `evaluate_expression`, `delete_files_batch` (and `write_files`, `executor_status`, `shells_list`, `patched_view`) passed `forbidden_reason()` and `order_gate()` as ALLOWED. The tripwire is the property that makes the Counter a charter checkpoint rather than ergonomics; a future tool with any of those names would be dispatchable.
- Fix: each verb may carry its common inflections before the boundary (`exec(ute|utes|uted|uting|utor|utable)?`, `eval(uate|...|uator)?`, `delete_file(s)?`, `write_file(s)?`, `patch(es|ed|ing)?`, `spawn(s|ed|ing)?`, `shell(s)?`, ...) while the trailing boundary STAYS - so a verb embedded in another word (`subshell_helper`, `patchwork`, `evaluation_report`, `mvp_tool`, `execution_plan`) is still not a verb. The sub-agent's snippet dropped the trailing boundary altogether, which blocks `mvp_tool`, `patchwork`, `evaluation_report` and `shellfish_index` - rejected. The live catalog of 94 tools has zero hits under the new rule (a test sweeps it every run).

**[LOW] `catalog_entry` aliased the shared `EXAMPLES` global into menu rows — PLAUSIBLE hardening — DONE** - `line 240-242`
- `example_for` copies (`dict(ex)`), `catalog_entry` did not; no live mutator was found, so this is consistency hardening, not a confirmed defect. Pinned by a test that mutates a returned row and asserts the global is untouched (cleaning up on failure).

## Adversarial verification (Phase 3)
- Thirteen must-block names (seven the old rule missed, six it caught) and eleven must-allow names, parametrised; plus the live-catalog sweep through the real `server.list_tools()` with the full surface.
- `order_gate` is exercised end to end for every blocked name with the name present in the catalog and consent given - the tripwire, not the unknown-action check, is what refuses.
- `tests/test_counter.py`, `test_retrieval_counterfactual.py`, `test_server_reaudit.py`: unchanged, 96 passed with the battery.

## Remediation postscript (same commit)
The fixes were applied after this review hashed the bytes above; the file is now `e955f69af1f901b1c42ecc566e2771f5d1ed235200c805bd6bf672118fd07a57`. TDD: `tests/test_counter_reaudit.py` (26 tests) - 8 RED on the old bytes (seven bypasses + the alias), 18 controls green throughout, GREEN after; the audit probe ALL PASS (15/15).
