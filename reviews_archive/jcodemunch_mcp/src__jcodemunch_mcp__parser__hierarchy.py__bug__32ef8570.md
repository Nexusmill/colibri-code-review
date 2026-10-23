# Colibri review — src/jcodemunch_mcp/parser/hierarchy.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\parser\hierarchy.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summaries, artifacts reaudit/jcm/)
- sha256: `32ef8570e60ef884172e30de372d33dda2ef7037d9f3123d83a1b975666dc87e` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: the sub-agent's summary (1 CONFIRMED with a RED probe, 2 refuted); `build_symbol_tree` 15-33 (a symbol with a parent in the map is appended under it and never becomes a root), `flatten_tree` 36-46 (walks from the roots only); the sole importer chain `parser/__init__.py` → `tools/get_file_outline.py`; the extractor's parent-id construction is out of scope (whether real source can produce a loop is not established here - the module must survive one regardless). No prior `.colibri_reviews` record.

## Verdict
Every node in a parent loop was attached under another node in the loop, so none was a root and the whole loop vanished from the outline without a trace. Fixed: a cyclic link is broken at the node that closes it, which becomes a root.

## Bugs & vulnerabilities
**[MEDIUM] Symbols in a cyclic or self-referential parent chain were silently dropped from the tree — CONFIRMED — FIXED** - `line 25-31`
- Trigger (audit probe, RED on these bytes): two symbols naming each other as parent → `flatten_tree(build_symbol_tree(...))` returns neither.
- Fix: `_closes_a_cycle(symbol_id, parent_id, node_map)` walks the raw `.parent` chain upward from the proposed parent; reaching the symbol itself, or a node already visited, means the link would close a loop and the symbol becomes a root instead. Signature unchanged; both call sites unaffected.

## Refuted (recorded so they are not re-raised)
- RecursionError in `flatten_tree` on cyclic input (the loop never reached the walk - that was the defect); duplicate ids crashing `node_map` (last write wins, no crash).

## Adversarial verification (Phase 3)
- Pinned on real `Symbol` objects: a two-node cycle surfaces both symbols; a self-parented symbol is a root with no children; control: a class with a method flattens to `[(class, 0), (method, 1)]` exactly as before.

## Remediation postscript (same commit)
The fix was applied after this review hashed the bytes above; the file is now `db50e05d96a50e8e4d2594da975577bf6f312f4144940be616bcdb1370f9b8c9`. TDD: `tests/test_tail_batch1_reaudit.py` (16 tests across the three units of this batch) - 13 RED on the old bytes, 3 controls green throughout, GREEN after; the audit probe passes after.
