# Colibri review — src/jcodemunch_mcp/storage/embedding_matrix.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\storage\embedding_matrix.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summary, artifacts reaudit/jcm/)
- sha256: `e6c5dd2aa04fa1614bc2905600179bce656a70ca009ddcb5138df599c27fc03c` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: the sub-agent's summary (1 CONFIRMED with a RED probe, 1 refuted); `_build` 186-248 (`dim = len(raw_rows[0][1]) // itemsize`, mismatched rows skipped and counted), `get_matrix` 251-295 (`EmbeddingStore(db).iter_raw()` - an un-ordered SELECT - into `_build`, cached by file stamp); `EmbeddingStore.get_dimension()` / `set_dimension()` (`embed_dimension` meta, the width of the model the repo was LAST embedded with); the sibling record `…storage__embedding_store.py__bug__…` (2026-09-13: nothing calls `delete_many`, so a re-embed with a new model leaves the old model's rows in place - the precondition of this finding is reachable in production); `tests/test_v1_108_223.py::TestMismatchedWidthRowsAreInert` (mismatched rows must be inert, not fatal). No prior `.colibri_reviews` record.

## Verdict
The matrix took its width from whichever row an un-ordered scan happened to yield first. One leftover row from a previous model landing first excluded every current row and the semantic channel scored nothing. Fixed: the width is the store's persisted dimension.

## Bugs & vulnerabilities
**[HIGH] `_build` derived the matrix width from `raw_rows[0]` instead of the persisted `embed_dimension` — CONFIRMED — FIXED** - `line 192`
- What: after a re-embed with a different model the store holds both widths (nothing deletes the old rows - see the embedding_store record). `_build` sized the matrix by the first row of an un-ordered SELECT and skipped everything else; with a 3-wide leftover first, three 4-wide current rows were skipped, the matrix was one stale vector wide, and a current-model query scored nothing. Trigger (audit probe, RED on these bytes): `set_dimension(4)`, rows `[3-wide, 4, 4, 4]` → `dim=3 rows=1 skipped=3`, scores `{}`.
- Fix: `_build(raw_rows, dim=None)` takes the width from the store's persisted dimension (passed by `get_matrix`) when it is a positive int, and falls back to the first row only when no dimension is recorded. Mismatched rows stay inert and counted exactly as before (`tests/test_v1_108_223.py` unchanged and green). The dimension is read through a NEW `EmbeddingStore.peek_dimension()` over the same sidecar-aware read-only connection `iter_raw` uses: the first form of this fix called `get_dimension()`, which opens a writable connection and runs the schema script, and `tests/test_v1_108_185.py::TestAReadThatWrote::test_a_fusion_search_does_not_move_the_index_mtime` caught the moved mtime in the full suite - a read that wrote, the exact class that pin exists for.

## Refuted (recorded so it is not re-raised)
- The sub-agent's one refuted claim was re-traced and stands (its record lists it).

## Adversarial verification (Phase 3)
- Pinned through `get_matrix` over a real `EmbeddingStore`: with `embed_dimension` 4 and a 3-wide row that sorts first, `dim == 4`, three rows kept, one skipped, and a 4-wide query scores the current rows.
- Controls: a store with no dimension recorded still uses the first row's width; a mismatched row among current rows stays inert, not fatal.
- `tests/test_v1_108_223.py`, `tests/test_v1_108_185.py` (the read-that-wrote pin, RED against the first form, green now) and `tests/test_embedding_store_reaudit.py` unchanged; 334 tests in the watch/embedding/matrix/semantic sweep green with the battery.

## Remediation postscript (same commit)
The fix was applied after this review hashed the bytes above; the file is now `bfb2c975248fa492683b732b200d1cbd949c528b0383c42e0781446422455ae7`. TDD: `tests/test_embedding_matrix_reaudit.py` (3 tests) - 1 RED on the old bytes, 2 controls green throughout, GREEN after. The audit probe passes 3/3 after.
