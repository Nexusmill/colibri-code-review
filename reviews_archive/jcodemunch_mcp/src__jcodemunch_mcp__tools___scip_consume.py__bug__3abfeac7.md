# Colibri review — src/jcodemunch_mcp/tools/_scip_consume.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\tools\_scip_consume.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summaries, artifacts reaudit/jcm/)
- sha256: `3abfeac7c0e094cc2fe2a0541d7907ea31b304b857049f483d3d1e2842784584` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: the sub-agent's summary (1 CONFIRMED sharing the delete/edit-safe probe, 3 refuted); `scip_reference_files` 104-136 (file-aggregated `GROUP BY s_from.file`, docstring delegates "excluding the target's own file" to the caller); `find_references(scip_reference_files)` = exactly two production callers, `check_delete_safe.py` and `check_edit_safe.py` (+ `tests/test_v1_108_120.py`); `get_blast_radius._attach_scip_to_blast` carries its OWN inline query and a file-level pop (blast radius = affected OTHER files, so the pop is right there - untouched); `open_scip_reader` 32-47 and `scip_meta_and_stale` for the refuted claims. No prior `.colibri_reviews` record.

## Verdict
The reader aggregated edges by file and told its callers to drop "the target's own file" - a granularity at which a compiler-verified same-file caller and true self-recursion are indistinguishable. Fixed at the source: the self-edge is excluded by symbol identity here.

## Bugs & vulnerabilities
**[MEDIUM] `scip_reference_files` delegated self-reference exclusion to callers who could only do it by file — CONFIRMED — FIXED** - `line 111, 121-130`
- What: every returned row is a genuine `kind='reference'` edge, but after `GROUP BY s_from.file` the caller cannot tell "the target calls itself" from "another symbol in the same file calls the target". Both preflights popped the file and threw the second case away (see their records). Trigger: any SCIP-ingested repo where the only compiler-visible caller lives beside the target (dynamic dispatch inside a module is the common shape).
- Fix: `AND e.from_symbol_id != e.to_symbol_id` in the query; docstring now states the contract (self-edge excluded by identity, same-file edges from other symbols kept, the file is not the unit of exclusion).

## Refuted (recorded so they are not re-raised)
- `json.loads(raw)` on `file_hashes` uncaught: wrapped in `except (ValueError, TypeError)`, fails toward stale.
- `row['path']`/`row['hash']` KeyError escaping the `sqlite3.Error` guard: the `files` table is internal schema, not input - not a defect under this repo's threat model.
- `open_scip_reader` connection leak on `row_factory` assignment: cannot raise on a valid connection; the real failure path (probe SELECT) closes before returning None.

## Adversarial verification (Phase 3)
- The helper's new behaviour is pinned directly (a same-file edge from a different symbol is returned; the target's own edge is not) over a real `index_folder` index with `_ensure_scip_tables` edges, the same fixture shape as `tests/test_v1_108_120.py::TestScipReferenceFiles`, which stays green (its edges are cross-file).
- Blast radius: two callers, both updated in this commit; `_attach_scip_to_blast` does not use this helper.

## Remediation postscript (same commit)
The fix was applied after this review hashed the bytes above; the file is now `fa1da5292cac6a2bc468f0cefd16a6e71afdd0361f54b31b275d17967aa28a43`. TDD: `tests/test_scip_same_file_caller_reaudit.py` (5 tests, one battery for the shared root cause) - 3 RED on the old bytes (the helper's self-edge exclusion, the delete verdict, the edit verdict), 2 controls green throughout (a same-file edge from a different symbol already reached the helper's output; a purely recursive symbol stays safe in both preflights), GREEN after. Both audit probes (`probe_check_delete_safe_1.py`, `probe_check_edit_safe_1.py`) were RED on these bytes and pass after.
