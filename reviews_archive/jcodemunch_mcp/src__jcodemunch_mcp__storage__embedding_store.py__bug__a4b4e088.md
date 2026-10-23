# Colibri review — src/jcodemunch_mcp/storage/embedding_store.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\storage\embedding_store.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summary, artifacts reaudit/jcm/)
- sha256: `a4b4e088984b492e88e286a6f5dbe763593901dd4c5c32cc1f309ca120346480` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: `_GET_MANY_CHUNK = 900` (27) and `get_many` 278-320 (chunks its `IN (...)` at 900 "for exactly this reason"), `delete_many` 446-467 (one `IN (...)` with every id bound), `set_many`, `_invalidate_matrix`; callers of `delete_many`: NONE in `src/` (only `tests/test_semantic_search.py` and `tests/test_v1_108_223.py`, verified by search); the incremental paths that would need it: `sqlite_store.save_incremental` / `save_branch_delta` (deleted + changed files) and `tools/embed_repo.py` (`cached=True` short-circuit); the three audit probes re-run on these bytes (probe 3: `delete_many` of 33,766 ids raises `too many SQL variables`; probe 2: a changed symbol keeps its stale vector after an incremental reindex, a deleted file's symbol leaves an orphan row, a full `save_index` wipes `embed_dimension`/`embed_model`/`embed_task_type` from `meta` while the rows survive); `tests/test_v1_108_223.py::TestMismatchedWidthRowsAreInert` (mixed-width rows are deliberately inert). No prior `.colibri_reviews` record.

## Verdict
The one in-unit defect - `delete_many` dying past the bound-parameter limit - is fixed. The bigger problem the probe exposed is that nothing calls `delete_many`, so the vector table only ever grows and serves stale vectors; that fix lives in the store/indexer and is recorded here as deferred with the wiring named.

## Bugs & vulnerabilities
**[HIGH] `delete_many` built one unbounded `IN (...)` - `sqlite3.OperationalError: too many SQL variables` past SQLITE_LIMIT_VARIABLE_NUMBER — CONFIRMED — FIXED** - `line 446-467`
- What: 33,766 ids (the limit + 1,000 on this build) raised out of the tool; `get_many` in the same file chunks at 900 for exactly this reason.
- Fix: de-duplicated, blank-free ids deleted in `_GET_MANY_CHUNK` slices inside ONE transaction; the matrix cache is invalidated once. Pinned past the limit and for duplicates/blanks/unknown ids.

**[MEDIUM] `delete_many` has no caller in `src/` - deleted and changed symbols' vectors are never removed — CONFIRMED (probe 2) — DEFERRED, cross-file** - documented at `line 447` ("after incremental reindex")
- What: after an incremental reindex, a deleted file's symbol keeps its row (orphan; the matrix grows without bound) and a changed symbol keeps its OLD vector (semantic search ranks stale text). `embed_repo` then reports `cached: True` for the changed symbol because the row exists (`tools/embed_repo.py`), and a full `save_index` clears the `embed_*` meta keys while leaving `symbol_embeddings` rows in place (`storage/sqlite_store.py`).
- Why deferred: the fix is wiring in the indexer/store (call `EmbeddingStore(db).delete_many(removed_ids + changed_ids)` where `save_incremental` / `save_branch_delta` apply `deleted_files` and `changed_files`, and make `embed_repo` re-embed when the symbol's content hash differs from the one the row was built from - which needs a hash column), plus the meta-key survival in `save_index`. Three files, one design; `sqlite_store.py` and `tools/embed_repo.py` were outside this unit's scope by the campaign's own rule. Recorded here so the next pass over those units starts from the probe (`probe_jcm_storage_embedding_store_2.py`, 3/3 RED today).

## Refuted (sub-agent's own, re-checked and agreed)
- `set_many` should reject a vector whose width differs from `embed_dimension`: `TestMismatchedWidthRowsAreInert` pins the opposite as the design (mixed-width rows are inert, never fatal).

## Adversarial verification (Phase 3)
- The limit test reads SQLITE_LIMIT_VARIABLE_NUMBER from a live connection (no hard-coded 32,766), seeds limit+1,000 rows through the real `set_many`, deletes them all and asserts `count() == 0`.
- The exactness test asserts that duplicates, blanks and unknown ids neither raise nor touch other rows.
- `tests/test_embed_drift.py`, `test_semantic_search.py`, `test_v1_108_223.py` unchanged: 72 passed, 1 skipped with the battery.

## Remediation postscript (same commit)
The fix was applied after this review hashed the bytes above; the file is now `f6f467ef403299d2fd8fa8417168aeddb80566c9abaf18a792ccc00541c68a14`. TDD: `tests/test_embedding_store_reaudit.py` (2 tests) - 1 RED on the old bytes, 1 control green throughout, GREEN after; audit probe 3 ALL PASS; probe 2 stays 3/3 RED by the deferral above.
