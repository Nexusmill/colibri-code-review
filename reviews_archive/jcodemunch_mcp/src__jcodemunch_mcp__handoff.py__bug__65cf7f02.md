# Colibri review — src/jcodemunch_mcp/handoff.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\handoff.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summary, artifacts reaudit/jcm/)
- sha256: `65cf7f020d7a973eb5f805602c04a08db32dcfdb8e6048452cf73906f367b941` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: `get_file_outline` (`_norm_file` 103, `note_absence` 241-286 with the 500-cap eviction at 281-284, `_validate_evidence` 341-452: exact id / file-level broadening / absence ref / receipt routes, `finalize_handoff` 716-955); the served-symbol record it attests against - `storage/token_tracker.py` `_State.note_served` 343 / `served_symbol_ids` 361 (`_yield_served`, keyed by symbol id ONLY) and its two producers in `server.py` (search_symbols / get_ranked_context yield hook, 6887-6895) and one consumer (finalize_handoff dispatch, 5906: `served_symbol_ids()` unscoped); `tools/_utils.resolve_repo` (string split for owner/name, registry lookup for bare names); the 16 test files importing this module (test_v1_108_16x-19x, 419 tests) - none covers the three defects; the three RED probes re-run on these bytes (all FAIL). No prior `.colibri_reviews` record for this file; `token_tracker.py` has `133e72bb` and `server.py` `36a7fd00` (both amended with a postscript in this commit).

## Verdict
Attestation could be widened in three ways - by path shape, by repo, and by eviction order - and each one let a handoff cite something the session had not retrieved (or lose something it had). All three confirmed and fixed.

## Bugs & vulnerabilities
**[HIGH] the served-symbol record carries no repo, so a symbol served under repo A attests a handoff for repo B — CONFIRMED — FIXED (cross-file)** - `line 341-452, 716-955`; `token_tracker.py 343/361`; `server.py 5906/6887`
- What: symbol ids are repo-relative (`src/x.py::f#function`), `note_served` stored them with no repo, and the dispatcher handed `finalize_handoff` the whole unscoped set. `finalize_handoff(repo=...)` used `repo` only as a label. Probe 3 reproduced it end to end.
- Fix: `_State` keeps `_served_repos: id -> set(repo)`; `note_served(ids, repo=)` records the repo (evictions drop it), `served_symbol_ids(repo=)` returns only ids served under that repo - an id recorded with NO repo never attests a scoped handoff (fail-closed; the unscoped call is unchanged for the yield block). The server records `_served_repo_key(arguments["repo"], storage_path)` at both producers and scopes the finalize dispatch with the same key - canonical `owner/name` via `resolve_repo` when it resolves, the caller's string otherwise, so the two sides always agree. `finalize_handoff`'s explicit `served_ids` contract is untouched: a caller that passes a set asserts it. Probe 3's second check (a `repo` parameter on `tt.TokenTracker.served_symbol_ids`) and third (finalize refusing an explicitly-passed set) test that API shape, not the defect - the class is `_State` and the scoping lives at the source; the pinned tests go through the tracker and the dispatcher.
- One existing test updated: `tests/test_v1_108_162.py::TestServerDispatch::test_success_is_plain_content_list` recorded its served id with no repo and expected the dispatcher to attest it - it now records under the handoff's repo, which is the contract.

**[HIGH] `_norm_file` used `str.lstrip("./")` - a character class - so unserved paths normalised onto served files — CONFIRMED — FIXED** - `line 103`
- What: `github/ci.py` (never served) attested as `.github/ci.py`; `../../src/x.py` attested as `src/x.py` through the file-level broadening. Probe 1 reproduced both; the legitimate `./src/x.py` control passes before and after.
- Fix: a literal `./` prefix strip (repeated). The same idiom in `token_tracker.note_edited_files` (372, 376 - edit-through yield accounting, lower stakes) is the same class and is fixed in the same commit with a shared `_strip_dot_slash`.

**[MEDIUM] `note_absence` re-assigned an existing ref in place, so a just-reconfirmed scan was evicted as "oldest" — CONFIRMED — FIXED** - `line 281-284`
- What: dict assignment to an existing key keeps its position; the cap evicts from the front. At the 500-cap, re-running the FIRST scan handed the caller the same citable ref and the very next distinct scan evicted it - `finalize_handoff` then refused the ref it had just issued. Probe 2 reproduced it.
- Fix: pop-then-insert, so a re-confirmed scan is the newest record.

## Missing safeguards
- `_handoffs` (finalized-handoff store) has no size cap, unlike `_absences` (500). Process-lifetime growth only; flagged, not fixed here (a cap would need a policy for the resource URIs it invalidates).

## Adversarial verification (Phase 3)
- Repo scoping: the battery pins both directions (served under A is unknown for B; the same relative id served under both attests both; an unscoped legacy record attests neither scope; eviction drops the repo record) and the two server wirings (the yield hook records the search's repo; the finalize dispatch asks for the handoff's repo), through `_call_tool_impl` with the tool body stood in.
- `_norm_file`: checked that every existing served-file consumer (`served_files`, the `backing` sort) goes through the same helper, so both sides of the comparison changed together.
- The 41 related test files (test_v1_108_16x-19x, session/yield/token-tracker tests, the two re-audit batteries): 766 passed after the one contract update above.

## Remediation postscript (same commit)
The fixes were applied after this review hashed the bytes above; the file is now `f3d9fb7d1c67fc6c485c5c890ef3d348cfa0d64d926e1393782496b13ab4bf60`; `storage/token_tracker.py` is `2d98de709d16817aaaa1cbb623636133e3d355aae4ed46cb5c09a7be8dfb1c55` and `server.py` is `3e22e446826b42a2259c0f53fd4893aa6fefc0d0d590a48681b2459362be43b6` (their own records carry a postscript). TDD: `tests/test_handoff_reaudit.py` (7 tests) - all 7 RED on the old bytes (three on behaviour, four on the missing `repo` parameter that the behaviour needs), GREEN after; probes 1 and 2 ALL PASS; probe 3 passes its defect check and fails only the two API-shape checks described above.
