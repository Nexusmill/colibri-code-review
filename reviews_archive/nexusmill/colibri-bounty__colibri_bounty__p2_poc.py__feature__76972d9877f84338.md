# colibri feature review - colibri-bounty/colibri_bounty/p2_poc.py

- source: `colibri-bounty/colibri_bounty/p2_poc.py`
- model: grok-4.7 via api.x.ai (external second opinion, OFF-LADDER - does not count toward the three-model lock)
- sha256: `76972d9877f843380c1571f42fb0532d88bddcdbe1dd41a005225686935ceb98`
- date: 2026-10-21
- mode: feature (the SUGGEST pass - owner standing order 2026-10-13)
- context pack: shared funnel/doctrine pack + AST-derived symbols + consumers + coverage gaps (tests) + live deferred/remediation manifest rows + run-1 backlog injected as already-planned + RSI ruleset (0 active)
- prompt: colibri/feature@2 (langfuse)
- cost: ~$0.0663 (in=3975 out=9717)

## grok-4.7 output (verbatim)

## What this module does

This is the S4 PoC executor: `write_poc_test` drops a generated suite at `test/PocSuite.t.sol`, `run_poc_tests` runs only `^PocSuite$` through local `forge test --json` (fail-soft, one 600s timeout), and `adjudicate_poc` maps each candidate index to CONFIRMED, REFUTED, or INCONCLUSIVE. CONFIRMED requires the `POC-{i}` marker on a failing `testPoc{i}`; REFUTED requires that name on the PASS roster; a missing run, a wrong-reason failure, or an absent test stays INCONCLUSIVE and is never evidence against the candidate. Parsing stays on forge’s structured `status`/`reason` (the text roster regex is only the legacy path).

## Suggested add-ons

**Per-candidate forge isolation**
Value: High
Effort: M
What: A batch driver that writes and runs one candidate source at a time, then merges single-idx verdicts, so one uncompilable or hung PoC cannot blank the rest of the tier.
Why it helps the user: Today a suite-level compile error or the single 600s timeout makes `ran` false and `adjudicate_poc` stamps every idx INCONCLUSIVE with the same evidence. That understates S4 recall on the contest and makes a generator miss look like “forge never ran.”
How: Add `run_poc_candidate(project_root, idx, test_source, runner=None)` and `run_poc_candidates(project_root, sources)` beside `run_poc_tests`. Each iteration calls the existing `write_poc_test` → `run_poc_tests` → `adjudicate_poc(results, [idx])` and merges dicts. Keep `POC_FILE`, `POC_CONTRACT`, and `POC_MATCH` as they are (sequential overwrite of `PocSuite`, not a new contract name) so S2’s `RSIFunnel*` match stays clean. A per-idx failure stays INCONCLUSIVE; do not treat it as REFUTED.

**Typed fail-soft cause on the inconclusive row**
Value: High
Effort: S
What: When nothing executed, record a distinct cause (missing forge, timeout, non-JSON/compile failure, empty suite) on the result and use it as the evidence string.
Why it helps the user: `run_poc_tests` already returns `rc` and `raw`, but the `not ran` branch in `adjudicate_poc` always says “compile error or missing forge.” Timeout, absent `forge`, and solc failure are different denominators; collapsing them hides whether S4 was unavailable or the candidate did not build. Verdict stays INCONCLUSIVE either way.
How: In `run_poc_tests`’s `except` path, set `cause` from the exception type already interpolated into `raw` (`FileNotFoundError` → `missing_forge`, `subprocess.TimeoutExpired` → `timeout`). When `parse_forge_json` hits `ValueError` or a non-dict, set `cause` to `compile_or_non_json`; when JSON parses but `passed` and `failed` are both 0, set `empty_suite`. `adjudicate_poc` reads `results.get("cause")` in the `not ran` branch instead of the fixed string.

**Convention preflight before forge**
Value: Med
Effort: S
What: Statically check that `test_source` actually contains `testPoc{i}` and `POC-{i}` for the idxs about to be judged, and specialize the absent-test evidence when the function was never generated.
Why it helps the user: The marker/name contract is only documented, never checked. A generator miss still pays a full `forge test` and comes back as a generic “absent from the run” or “failed without the candidate marker,” which the funnel cannot tell apart from a real execution disagreement. Idx whose function is missing is already determined INCONCLUSIVE; skipping forge for those idxs saves the 600s budget for candidates that can actually run.
How: Add `poc_source_gaps(test_source, idxs)` using `poc_test_name` and `poc_marker`. `run_poc_candidates` (or the caller of `write_poc_test`) skips forge for idxs with no function and passes the gap note into `adjudicate_poc` so the else-branch evidence can say the function was not in `POC_FILE`. Marker-missing but function-present still runs; do not widen CONFIRMED beyond `poc_marker(i) in reason`.

## Nice-to-haves

- Parameterize the hardcoded `timeout=600` on `run_poc_tests`’s default runner so corpus replays can cap a slow contest without a custom `runner`.
- After `run_poc_tests`, unlink `POC_FILE` if `write_poc_test` created it, and restore prior bytes if that path already existed, so a contest checkout is unchanged for the next tier.
- Attach `forge --version` and a sha256 of the written source on the dict `run_poc_tests` returns, so a later S5 row can be tied to the executor that produced it.
- In `parse_forge_json`, keep forge’s raw `status` (`Success` / `Failure` / `Skipped`) on each record so `adjudicate_poc` can say “skipped” instead of “failed without the candidate marker.”
- Ignore suites other than `POC_CONTRACT` inside `parse_forge_json` so a stray suite in `--json` cannot enter `roster` or `failures`.

- ACCEPT per-candidate forge isolation (run_poc_candidates) - VERIFIED: one compile error/timeout stamps EVERY idx INCONCLUSIVE via ran=False; sequential PocSuite overwrite kept deliberately (out of RSIFunnel namespace).
- ACCEPT typed fail-soft cause on the inconclusive row - VERIFIED: not-ran branch hardcodes "compile error or missing forge" while FileNotFoundError vs TimeoutExpired already differ in raw.
- ACCEPT convention preflight (poc_source_gaps) - marker/name contract is docstring-only today; skipping forge for absent functions saves the 600s budget.
- DEFER 5 nice-to-haves (timeout param, POC_FILE restore, version+sha stamp, Skipped status, suite filter).
