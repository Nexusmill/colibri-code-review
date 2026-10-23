# Colibri review — src/jcodemunch_mcp/tools/register_edit.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\tools\register_edit.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summary, artifacts reaudit/jcm/)
- sha256: `6da292d4c156f4bddd377c2958e263b2531fc9468416ef4791094101141fbcea` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: the sub-agent's summary (1 CONFIRMED with a RED probe, 1 PLAUSIBLE, 2 refuted); `register_edit` 22-105: the docstring ("Register file edits to invalidate caches" - `reindex` "whether to reindex the edited files"), the symbol loop keyed on `sym["file"]` (repo-relative, from the index), the `reindex` branch handing the caller's strings to `index_file` (which resolves a relative path against the process cwd and returns a `success`/`error` dict) inside a `try` that only logged at debug; `server.py` tool schema for `register_edit` (reindex "default False"); `retrieval/freshness.py::classify` (the `_freshness` field is derived from an mtime comparison with a deliberate 1 s tolerance, not from this unit); `storage/sqlite_store.py::load_index` LRU (mtime-keyed, same object within a window - the sub-agent's second refutation, re-verified); `tests/test_register_edit.py` (6) and `tests/test_v1_108_95.py`. No prior `.colibri_reviews` record.

## Verdict
The audit's HIGH ("the default should reindex") is refuted - it argues with a documented opt-in. What its probe actually exposed underneath is real: the two halves of `register_edit` wanted different path forms, so no single call could both invalidate the symbols and reindex the file, and a reindex failure was invisible to the caller. Fixed.

## Bugs & vulnerabilities
**[MEDIUM] Repo-relative paths invalidated but silently failed to reindex; absolute paths reindexed but invalidated nothing — CONFIRMED — FIXED** - `line 61-66, 88-95`
- What: `edited_set = set(file_paths)` was compared against `sym["file"]` (repo-relative), while `reindex=True` passed the same strings to `index_file`, which resolves a relative path against the server's cwd - "File not found" for any cwd that is not the repo root. The reverse form (absolute) matched no symbol row. Trigger: `register_edit(repo, ["mod.py"], reindex=True)` from any cwd other than the repo root -> `invalidated_symbols: 1`, nothing re-parsed, no error surfaced; `register_edit(repo, ["C:/repo/mod.py"])` -> `invalidated_symbols: 0`.
- Fix: each path is resolved both ways against `index.source_root` (`rel_paths` for the symbol match, `abs_paths` for `index_file`); backslashes normalised; an absolute path on another drive is kept as given.

**[MEDIUM] A reindex failure was swallowed (debug log only) — CONFIRMED — FIXED** - `line 91-95`
- What: `index_file` returns `{"success": False, "error": ...}` for a missing file and the loop ignored the return value entirely; an exception was logged at debug. The caller was told `registered: N` with no hint that the requested re-parse did not happen.
- Fix: with `reindex`, the result now carries `reindexed` (count) and `reindex_errors` (`"<path>: <error>"`); the keys are only added when `reindex` is True so the default contract is byte-identical.

## Refuted (deleted from the findings; recorded so they are not re-raised)
- **HIGH "default `reindex=False` leaves symbol content stale" - REFUTED.** The docstring, the module docstring ("Register file edits to invalidate caches") and the server tool schema all document cache invalidation as the contract and `reindex` as the opt-in; `tests/test_register_edit.py` pins the default. The probe's "stale after a default call" is that contract working as written. The audit's proposed fix (flip the default) would make every hook-driven `register_edit` re-parse synchronously.
- **`_freshness` reads "fresh" after the edit - NOT THIS UNIT.** The field comes from `retrieval/freshness.py::classify`, which compares mtimes with a deliberate 1 s tolerance; the probe writes the new source within the same second as the index build. Out of scope here; the tolerance is the freshness module's documented choice.
- The sub-agent's own two refutations (branch deltas share the per-repo SQLite file with the base index; `load_index`'s mtime-keyed LRU makes the in-place cache pops reach subsequent same-branch reads) were re-verified against the current bytes and stand.

## Deferred / PLAUSIBLE (not fixed here)
- **[MEDIUM, PLAUSIBLE] no `branch` parameter:** `register_edit` always loads and mutates the base (`branch=""`) CodeIndex; a branch-composed cached object's ranking caches may stay warm between two branch-scoped reads. Unverified because no branch-scoped read path was exercised in this pass; the fix is an API addition (a `branch` argument threaded to `load_index`), which is a feature change, not a defect fix - left for the server-level branch work.

## Adversarial verification (Phase 3)
- Both confirmed defects are asserted end to end through `register_edit` over a real `index_folder` index, with the process cwd moved OFF the repo root (`monkeypatch.chdir(tmp_path)`) so the relative-path case cannot pass by accident, and the new signature read back through `search_symbols`.
- Control: the default call (no `reindex`) still invalidates, still leaves the signature unparsed, and gains no new keys - the documented contract.
- `tests/test_register_edit.py` (6) + `tests/test_v1_108_95.py` unchanged: 22 passed with the battery.
- The audit probe re-run on the fixed bytes still reports its two FAILs - both are the refuted claims above (default-call staleness; the freshness tolerance), not regressions.

## Remediation postscript (same commit)
The fixes were applied after this review hashed the bytes above; the file is now `bad1dcbeda6054a31f0e85a5376727038d64a863c08b2f5c9de6099e6b3dc70b`. TDD: `tests/test_register_edit_reaudit.py` (4 tests) - 3 RED on the old bytes, 1 control green throughout, GREEN after.
