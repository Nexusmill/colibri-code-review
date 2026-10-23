# Colibri review — src/jcodemunch_mcp/tools/get_watch_status.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\tools\get_watch_status.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summary, artifacts reaudit/jcm/)
- sha256: `a20a08ffb7c01ae217fd326728a1c2181b40c8ca44aec52d1147cf319b5b020e` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: the sub-agent's summary (1 CONFIRMED with a RED probe, 0 refuted); `_reindex_key` 29-47 (the #353 repo-id resolver with a broad `except Exception` falling back to the FOLDER PATH), `get_watch_status` 50-112 (the lazy `has_any_reindex_state()` gate from v1.108.81, `get_reindex_status(key)` returning the fresh-and-healthy default for an unknown key, `any_failing` from `reindex_failures`/`reindex_fatal`); `reindex_state.get_reindex_status` (no enumeration API - an unresolvable key cannot be looked up another way); the two pins that monkeypatch `_reindex_key` with a lambda returning a bare key (`tests/test_v1_108_78.py` line 164, `tests/test_v1_108_81.py` lines 24/48) - the reason the resolver keeps its `(folder, storage_path) -> str` shape. The sub-agent's note "no test file exists" is wrong: those two files cover the tool. No prior `.colibri_reviews` record.

## Verdict
The tool exists so an agent can check watcher health before trusting an index; the moment repo-id resolution broke, a crash-looping watcher read as fresh. Fixed: an unresolvable key is reported as unresolved and counted as failing.

## Bugs & vulnerabilities
**[HIGH] `_reindex_key`'s broad `except` fell back to the folder path, so a fatal watcher state was invisible whenever identity resolution failed — CONFIRMED — FIXED** - `line 45-47, 71`
- What: reindex_state is keyed by the repo_id a watcher registers; #353 made this tool resolve it. But a resolver failure (a git identity probe error, a bad path_map entry, anything raising inside `_local_repo_id`) returned the folder path - a key nobody registered - and `get_reindex_status` answered the healthy default for it. Trigger (audit probe, RED on these bytes): a fatal failure recorded under the real key, `_local_repo_id` made to raise → the entry shows `index_stale False`, no failure fields, `any_failing False`.
- Fix: `_reindex_key` no longer swallows the failure (it raises; its `-> str` shape is kept for the two existing pins); `get_watch_status` catches it per repo, keeps the neutral default fields for the entry, adds `reindex_state_unresolved: True` and a `reindex_error` naming the cause, sets a new top-level `any_unresolved`, and counts the repo in `any_failing` - the conservative direction for a health check. A working resolver and a healthy repo carry none of those markers.

## Adversarial verification (Phase 3)
- Pinned through `get_watch_status` over a real `index_folder` index with a fatal state recorded under the real key and `watcher._local_repo_id` monkeypatched to raise: the entry is marked unresolved with the cause in `reindex_error`, `any_failing` and `any_unresolved` are True.
- Controls: a working resolver surfaces the fatal state by its real key with no unresolved marker; a healthy repo carries no marker and `any_failing` False. The first draft changed the resolver's return shape to a tuple and broke `tests/test_v1_108_81.py::test_resolves_keys_when_reindex_state_present` - reverted to the raising form so both pinning files pass unchanged (18 passed together).
- 334 tests in the watch/embedding/matrix/semantic sweep green with the battery; the audit probe passes 4/4.

## Remediation postscript (same commit)
The fix was applied after this review hashed the bytes above; the file is now `44ff88613ec4e502d886d2fb52d455139b045ebf6e80eb823282515793796937`. TDD: `tests/test_get_watch_status_reaudit.py` (3 tests) - 1 RED on the old bytes, 2 controls green throughout, GREEN after.
