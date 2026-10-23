# Colibri review — src/jcodemunch_mcp/investigator/retrieval_counterfactual.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\investigator\retrieval_counterfactual.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summaries, artifacts reaudit/jcm/)
- sha256: `ec504932b38762eeb08ccb7be88a9784a3713bdaef81e175c1c85543ac42df2a` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: the sub-agent's summary (1 CONFIRMED, doc-only); the module docstring's gate list 35-41 and the `Gate 4` sentence 44; `GATES` 66-74 ("Gates in pipeline order"); `explain_route` 188-221 - rules (2/3) run BEFORE tokenizing (4), and the inline comments already carry that numbering; `explain_misses` 292-297 (`by_gate` sorted by count - `GATES` order is not load-bearing); `tests/test_retrieval_counterfactual.py` (`set(out["by_gate"]) <= set(GATES)` - order-insensitive; `test_rule_preemption_reports_never_scored` drives "who calls this"). No prior `.colibri_reviews` record.

## Verdict
The module's own contract text ("the gate order is the pipeline order") listed `empty_query` before the rules gates while the code runs the rules first; `GATES` repeated the inversion. Doc/constant-only fix; the code was right.

## Bugs & vulnerabilities
**[LOW] Documented gate order inverted relative to the code (docstring list, `Gate 4` sentence, `GATES`) — CONFIRMED — FIXED** - `line 36-39, 44, 68-74`
- What: a reader following the docstring would expect an all-stopword query that trips a rule to report `empty_query`; the code (correctly) reports `rule_preempted` because `route` consults rules before it tokenizes.
- Fix: the list is renumbered to the code's order (rules = 2/3, `empty_query` = 4), the "Gate 4" sentence becomes "Gate 3", and `GATES` lists `RULE_PREEMPTED` before `EMPTY_QUERY`. Nothing consumes `GATES` for ordering (verified: the only consumer is a set-membership assertion).

## Adversarial verification (Phase 3)
- Pinned: docstring index order and `GATES` order; control on the code itself - "who calls this" against the live catalog → `rule_preempted` with `decision_path == ["catalog", "intent_rules"]` and no `query_tokens` key (the tokenizer was never consulted).

## Remediation postscript (same commit)
The fix was applied after this review hashed the bytes above; the file is now `57fb0df5c160c35efeaa445b07d03bcac50f83226674951ab2d3d2987ad90ca3`. TDD: `tests/test_tail_batch4_reaudit.py` (14 tests across the eight files of this batch) - 11 RED on the old bytes (each for its own reason, verified by the per-test failure), 3 controls green throughout, GREEN after.
