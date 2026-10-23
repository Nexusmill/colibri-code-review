# colibri feature review - colibri-bounty/tests/test_p2_poc.py

- source: `colibri-bounty/tests/test_p2_poc.py`
- model: grok-4.7 via api.x.ai (external second opinion, OFF-LADDER - does not count toward the three-model lock)
- sha256: `90a916339096fabe299d6de38b4e3e8f045f3dd56c3777a64c265730f46ee304`
- date: 2026-10-21
- mode: feature (the SUGGEST pass - owner standing order 2026-10-13)
- context pack: shared funnel/doctrine pack + AST-derived symbols + consumers + coverage gaps (tests) + live deferred/remediation manifest rows + run-1 backlog injected as already-planned + RSI ruleset (0 active)
- prompt: colibri/feature@2 (langfuse)
- cost: ~$0.0644 (in=5419 out=8933)

## grok-4.7 output (verbatim)

## What this module does

S4 turns a candidate PoC into a forge harness outside the `RSIFunnel` namespace, runs `forge test --json` exact-anchored to `POC_CONTRACT`, and parses that into passed/failed counts, a pass roster, and failure reasons. `adjudicate_poc` then labels each candidate index `CONFIRMED` (failure reason carries `POC-{i}`), `REFUTED` (that `testPoc{i}` is on the pass roster), or `INCONCLUSIVE` (wrong reason, absent test, nothing ran, rawless counts, or a crashed runner), fail-soft, preferring a structured roster over raw text.

## Suggested add-ons

### 1. Closed reason class on each verdict
- Value: High
- Effort: S
- What: Keep the three verdicts, and add a closed `reason_class` (`confirmed_marker`, `refuted_pass`, `wrong_reason`, `absent`, `nothing_ran`, `no_roster`, `runner_failed`) next to the existing evidence string.
- Why it helps the user: Precision and the always-on contamination column need to separate "claim did not reproduce" from "harness never executed." Those branches already exist, but only free-text evidence distinguishes them, so a later table can collapse a compile failure and a true refutation-adjacent inconclusive into one denominator.
- How: Extend `adjudicate_poc` only. The split is already implied by `test_adjudicate_wrong_reason_failure_is_inconclusive`, `test_adjudicate_missing_test_is_inconclusive_not_refuted`, `test_adjudicate_nothing_ran_is_inconclusive`, `test_adjudicate_rawless_dict_cannot_refute`, and `test_adjudicate_fail_soft_never_raises` (`rc == -1`). Do not change the verdict enum or fail-soft behavior.

### 2. Suite-scoped JSON parse
- Value: High
- Effort: S
- What: Before counting roster and failures, keep only the forge `--json` suite identified by `POC_CONTRACT` / `POC_FILE`. Any other suite is ignored; unparseable input stays the current nothing-ran dict.
- Why it helps the user: S2 and S4 share a foundry project. Match-contract already stops the PoC suite from polluting invariant runs; the reverse is only locked for a single-suite blob (`FORGE_JSON`). A multi-suite JSON would let invariant passes enter the PoC roster and move the like-for-like denominator.
- How: `parse_forge_json`, keyed off `POC_CONTRACT` and `POC_FILE`. `run_poc_tests` already passes `--match-contract` `POC_MATCH`; this is the same isolation on the structured path `adjudicate_poc` prefers over raw text.

### 3. Marker-stamping harness renderer
- Value: High
- Effort: M
- What: A sibling of `write_poc_test` that wraps caller-supplied assertion bodies into a contract named `POC_CONTRACT`, one function per `poc_test_name(i)`, with `poc_marker(i)` in every assertion/revert string, and writes that through the existing verbatim writer.
- Why it helps the user: Adjudication is only honest if generation and judging share the marker contract. Today `write_poc_test` dumps a caller string unchanged, so a real failing PoC can be judged `INCONCLUSIVE` for a missing marker, and nothing in this module produces the harness the suite docstring describes.
- How: New function beside `write_poc_test`, calling `poc_test_name`, `poc_marker`, and `POC_CONTRACT`, then `write_poc_test` (do not change its verbatim write; `test_write_poc_test_creates_the_harness` locks that). Destination should be `POC_FILE`. Wrapping only — do not synthesize candidate PoCs.

## Nice-to-haves

- Return the runner stdout and `rc` on the `run_poc_tests` result so a table can be recomputed from the captured blob without re-invoking forge.
- Fail-soft timeout on the default runner, collapsing to the existing `rc == -1` shape `adjudicate_poc` already treats as inconclusive.
- Surface suite `duration` and per-test gas from `parse_forge_json` for the disclosed-cost column (both are already in `FORGE_JSON` / the napier text shape).
- When the suite summary reports skipped, mark that `testPoc{i}` inconclusive with its own evidence token instead of the generic absent path.

- ACCEPT closed reason_class enum beside evidence strings - all five cited adjudication test names verified; branches exist, only free text distinguishes them today.
- ACCEPT suite-scoped JSON parse (keep only the POC_CONTRACT suite) - the reverse isolation (PoC out of invariant runs) is locked in-module; multi-suite JSON entering the roster is real.
- ACCEPT marker-stamping harness renderer wrapping assertion bodies through poc_test_name/poc_marker - write_poc_test is a verbatim dump today; generation/judging marker contract has no producer.
- DEFER 4 nice-to-haves (stdout+rc on result, fail-soft timeout, duration/gas surfacing, skipped evidence token).
