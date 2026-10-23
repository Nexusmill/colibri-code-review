# Colibri review — src/jcodemunch_mcp/tools/get_dead_code_v2.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\tools\get_dead_code_v2.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summary, artifacts reaudit/jcm/)
- sha256: `da02bd8cd4a8618f9470bb795b9086ed3694cd4f987d5a4f4a1b81832e260647` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: the sub-agent's summary (1 CONFIRMED with a RED probe, 4/5 checks failing on these bytes); Signal 2's inputs - the AST fast path 640-663 (`called_names_by_file`, `search_files = (sym_file, *rev.get(sym_file))`), `_sweep_module_level_callers` 411-505 (#409, same scoping), the text fallback 678-711, `_call_graph_only_dead_code` 921-1030 (already repo-wide: `called_names` over the whole graph); the scoring loop 745-790 and the #408 degeneracy machinery (`_informative_signals`, denominator held at 3); `parser/extractor._extract_call_name` (an attribute call `make().run()` IS recorded as `run` in the caller's `call_references`); the coverage-oracle benchmark `benchmarks/deadcode_eval/` (README: "the accuracy of every subsequent change to the detector" must be measurable; `MCPClient.__init__` sits in the 2026-08-03 false-positive sample); `find_similar_symbols._DUNDER_SKIP` (the only other dunder awareness in tools/); tests: `test_dead_code_v2.py`, `test_v1_80_10…`, `test_v1_80_7…`, `test_v1_80_9…`, `test_v1_108_229/230/271/275.py`, `test_parse_warnings.py`. No prior `.colibri_reviews` record.

## Verdict
The `no_callers` signal reported live methods dead in two structurally blind shapes - protocol (dunder) methods, and methods reached through an instance that travelled past the module's direct importers - and both landed at 0.67, above the default threshold. Fixed, and measured against the repository's own coverage oracle.

## Bugs & vulnerabilities
**[HIGH] `no_callers` fired on every protocol method — CONFIRMED — FIXED** - `line 762`
- What: `__init__`, `__enter__`/`__exit__`, `__eq__`, `__iter__` … are invoked by syntax (`Box()`, `with`, `==`, `for`), never by a name token, so no call site ever puts the name into `call_references`. The by-name signal fired on all of them; with `not_barrel_exported` (which fires on every method - methods are never barrel-exported by name) that is 0.67 = "dead" for being used correctly. Production evidence: the 2026-08-03 benchmark sample lists `cli/init.py::MCPClient.__init__#method` as a definite false positive.
- Fix: `_is_protocol_method(sym)` (method + `__x__`, len > 4); Signal 2 abstains on it in the 3-signal path AND in `_call_graph_only_dead_code` (same blindness, single-signal mode at exactly the 0.5 threshold). Abstaining is per signal: an orphan file's dunders still die with the file through `unreachable_file` (pinned).

**[HIGH] A method called from a file that does not import its module had "no callers" — CONFIRMED — FIXED** - `line 659-663`
- What: `search_files` scoped the lookup to the symbol's own file and its DIRECT importers. An instance travels wherever it is passed or returned: `svc.make()` returns `Impl()`, `main` calls `.run()` without importing `impl`; the AST index records `run` in `main`'s call_references, in a file the scoping never consulted. 0.67 again.
- Fix: for METHODS the fast path matches against `all_called_names` (every file's recorded calls, O(1) per symbol) - exactly what `_call_graph_only_dead_code` already did for everything; plain functions keep the importer scoping (they must be imported by name to be called). Disclosed residual: `_sweep_module_level_callers` (#409, module-level calls) keeps the importer scoping - widening it means reading every file's residue whenever any method is unresolved, which defeats that sweep's laziness; a method called ONLY at module level from a non-importing file is still missed. Recorded, not fixed.

## Measured (benchmarks/deadcode_eval, coverage oracle from this tree's full suite)
Oracle: this tree's full suite under `pytest-cov` (8113 passed, 17 skipped) → 2,387 symbols proven alive by an executed line inside their body, 242 files with coverage. Both runs use the same `coverage.json` and the same live index; only the detector bytes differ. `min_confidence` 0.5 (default), `max_results` 0.

| cutoff | flagged before → after | definite false positives | fp_rate | alive_caught |
| --- | --- | --- | --- | --- |
| 0.90 (default) | 0 → 0 | 0 → 0 | vacuous | vacuous |
| 0.95 | 471 → 388 | 241 → 176 | 51.2% → 45.4% | 10.1% → 7.4% |
| 1.00 | 471 → 388 | 241 → 176 | 51.2% → 45.4% | 10.1% → 7.4% |

- 83 fewer symbols flagged; 65 of them (78%) were definite false positives - live methods the suite executed. The other 18 are unobservable to this oracle (alive-but-untested or genuinely dead); no recall is claimed, per the benchmark's own README.
- The 2026-08-03 results file (766 flagged / 482 FP / 62.9% at 1.0) is a different tree and index and is not directly comparable; the before/after pair above is.
- Observation, not this tranche: at the DEFAULT cutoff 0.90 the tool returns nothing on this repository before AND after - `not_barrel_exported` fires on ≥ 90% of its symbols (this package has few barrel exports), the #408 degeneracy rule drops it, and no symbol reaches 0.5 on the two remaining signals. That is the documented "nothing discriminates → return nothing" behaviour (v1.108.231), recorded here because the benchmark's headline column is vacuous on this repo at the default.
- `benchmarks/deadcode_eval/coverage.json` is gitignored (generated); the before/after JSON rows are kept in the session scratchpad (`bench_before.json` / `bench_after.json`).

## Refuted / declined
- The sub-agent's fix snippet (dunder abstention only) left the factory-chain case RED by its own account; the widening above closes it, and the `never_called` control shows methods are still measured.
- Not made: exempting `__init__` etc. by NAME LIST (`find_similar_symbols._DUNDER_SKIP` style). The shape rule `__x__` covers `__call__`, `__getattr__`, `__len__`, `__hash__` … without a list to maintain, and a user-defined `__weird__` on a class is invoked the same way if at all.

## Adversarial verification (Phase 3)
- Both defects pinned end to end through `get_dead_code_v2` over a real `index_folder` index (5 RED on the old bytes, 1 control), with the fixture holding `not_barrel_exported` UNDER the #408 degeneracy cutoff (five barrel-exported, called functions) - the first draft had it degenerate, every reachable symbol topped out at 0.33 and the tests passed vacuously on the broken bytes. A zero-threshold test asserts the signal does not FIRE, not merely that it falls under a threshold.
- Controls: a function nobody calls and a method no file calls by name are still reported with `no_callers`; the fallback's plain `unused` method is still reported.
- The existing dead-code test files (above) are unchanged and green with the battery.

## Remediation postscript (same commit)
The fix was applied after this review hashed the bytes above; the file is now `62e4b35c2abbc6d6f2b98d982cf982f226e202d5d2a8e46d3ee4fc153f8bcc28`. TDD: `tests/test_dead_code_v2_reaudit.py` (6 tests) - 5 RED on the old bytes, 1 control green throughout, GREEN after. The audit probe passes 5/5 after (4/5 FAIL before).
