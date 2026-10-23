# Colibri review — src/jcodemunch_mcp/tools/assemble_task_context.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\tools\assemble_task_context.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summary, artifacts reaudit/jcm/)
- sha256: `d84e593a89574a3d31f82373df67692629cc03a3941c816904817e7172e93cc4` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline and to HEAD 857a4d5 after CRLF reconstruction)
- date: 2026-09-13
- mode: bug
- context pack: `get_file_outline` (the 560-line `assemble_task_context` with 18 nested stage handlers, `_add_entry`, the dispatch loop 663-670, the savings ledger 689-693, the result dict 697-716); `find_references`/`search_text` (registered in config.py tool profiles, counter.py hints, cli/init.py + cli/skills.py docs; tests/test_assemble_task_context.py + test_v1_108_95.py are the callers); `digest.py` `compose_digest` (line 99: returns `briefing` / `structured{delta{files,...},hotspots,dead_code,regret?,scip?}` / `_meta`, and PERSISTS the session head via `_write_state` unconditionally); `token_tracker.estimate_savings` (max(0, (raw-response)//4)); the savings convention across tools (get_ranked_context / search_symbols / get_symbol scope raw_bytes to the files delivered; find_implementations / winnow_symbols still sum the whole index); both RED probes re-run on these bytes (probe 1: 3 FAIL, probe 2: 1 FAIL). No prior `.colibri_reviews` record for this file or for digest.py.

## Verdict
The orientation stage has never worked - its import target does not exist - and the capsule could not tell its reader what it had failed to deliver. Three of the four reported findings confirmed and fixed; the fourth is a recorded design decision, not a defect.

## Bugs & vulnerabilities
**[HIGH] `_stage_orientation` imports `digest` from `.digest`; the export is `compose_digest` — CONFIRMED — FIXED** - `line 302`
- What: `ImportError` on every call for every repo, swallowed into `logger.debug("digest skipped")`. The `explore` intent (orientation weighted 0.35) has been shipping without its first stage since the tool landed. Probe 1 captured the swallowed message on these bytes.
- Beyond the sub-agent's snippet (which only swapped the name): the call site read `summary/changed_files/hotspots/dead_code` off the TOP level of the result, but `compose_digest` returns `briefing` + `structured` - the renamed call would have produced an entry of empty strings and lists. And `compose_digest` writes the digest tool's since-last-session state on every call, so an orientation read would have silently consumed the user's next `digest` delta. Fix: `compose_digest(repo_id, storage_path=..., persist_state=False)` - a new keyword-only parameter on `compose_digest` (digest.py `9b4c0b5f` -> `b529048e`, default True, every existing caller unchanged) - and the entry is built from `briefing` and `structured` (`delta.files`, `hotspots`, `dead_code`).

**[HIGH] `stages_run` lists a stage even when it delivered nothing, and a budget drop is not flagged — CONFIRMED — FIXED** - `line 663-670, 280-281`
- What: `_add_entry` returns False on a budget refusal and no stage checks the return; the dispatch loop appends to `stages_run` after every handler regardless. A reader seeing `stages_run=[..., "callers", ...]` with no callers entry concludes "no callers" when the answer was never delivered. Probe 1 reproduced it with a budget of anchor+1: `callers`, `callees`, `blast` listed, no entries, no flag.
- Fix: the result now carries `stages_without_entries` (ran, delivered nothing - budget refusal, a swallowed sub-tool failure, or nothing to say) and `budget_exhausted` (a payload was refused, the loop stopped early, or the cross-repo layer was skipped for budget). `stages_run` keeps its meaning (handlers that ran). The docstring says so.

**[MEDIUM] the token-savings baseline is the whole indexed repository — CONFIRMED — FIXED** - `line 690`
- What: `raw_bytes` summed every symbol in the index, so an anchor-only call over a 51-file repo claimed 974 tokens saved against a 29-byte file (probe 2). The number feeds `total_tokens_saved` and `cost_avoided` - a user-facing ledger.
- Fix: the baseline is the files the capsule reaches - the anchors plus every `file` or indexed symbol id an entry names (walked recursively, so callers/callees/blast rows count) - using `index.file_sizes` where the view carries them and the symbols' `byte_length` per file where it does not (a view built without stored contents has an empty `file_sizes`; get_ranked_context's baseline reads 0 there - noted, out of this unit's scope).

## Refuted
- **`strategy_applied` ignores `include` narrowing (sub-agent MEDIUM, line 702) — REFUTED, not changed.** `tests/test_assemble_task_context.py::test_strategy_applied_is_full_intent_strategy` pins the current behaviour with its reason: "strategy_applied should reflect the full intent recipe even when include narrows what actually runs - so callers can see what was considered vs. what fired". A recorded decision, tested; the probe encoded the sub-agent's preference. The name is arguable; the behaviour is not a defect. The docstring now states it.

## Missing safeguards
- Each stage handler still swallows its sub-tool exception into a debug log; `stages_without_entries` makes the omission visible, the reason is not (a per-stage error map would need all 18 handlers touched - deferred, not a defect of this pass).

## Adversarial verification (Phase 3)
- The orientation entry was checked against a real `compose_digest` return on a fresh index (briefing non-empty, hotspots/dead_code lists) and the state file asserted ABSENT afterwards, with a control call to `compose_digest` proving the path.
- The budget test learns the anchor cost from a full-budget call and asserts on `budget_exhausted` + `stages_without_entries`, not on token arithmetic.
- The savings tests bracket the number from both sides: an anchor-only call over 50 unrelated files stays under the 29-byte file's ceiling; reaching a large caller through the callers stage raises it and it never exceeds the two files' real sizes.
- Existing tests: `tests/test_assemble_task_context.py`, `tests/test_digest.py`, `tests/test_v1_108_95.py` all unchanged and green on the new bytes (49 passed together with the new battery).

## Remediation postscript (same commit)
The fixes were applied after this review hashed the bytes above; the file is now `2957d7b52e88a1c51a91ea7b040d4398be39f5850ad75b059a564bcf7f35a6a7`; `digest.py` is `b529048e8125a122fbea5364360c57393f03d1d53ece72ea0eb67a48d75eda7c` (the `persist_state` keyword only). TDD: `tests/test_assemble_task_context_reaudit.py` (6 tests) - 4 RED on the old bytes for exactly the three confirmed findings (the state-consumption guard green before and after, as it must be), GREEN after; probe 2 ALL PASS; probe 1 passes its two defect checks and fails only the refuted `strategy_applied` expectation.

**Gate catch (round 1, gate_20260913-145049, LOW, accepted):** the cross-repo layer - the one stage outside the dispatch loop - appended itself to `stages_run` without honouring `_add_entry`'s refusal, so with `cross_repo=True` and a budget already spent it was listed with no entry and no per-stage flag: the exact class this tranche closed for the strategy stages, left open in the branch the same diff edited. The battery never set `cross_repo=True`. Fixed (the refusal now lands in `stages_without_entries`) and pinned by `test_cross_repo_layer_refused_for_budget_is_named_too` (RED on the round-1 bytes at the invariant assertion). Docketed as EV-074.
