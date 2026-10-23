# colibri feature review - colibri-bounty/tests/test_p2_inv.py

- source: `colibri-bounty/tests/test_p2_inv.py`
- model: grok-4.7 via api.x.ai (external second opinion, OFF-LADDER - does not count toward the three-model lock)
- sha256: `cb0543c06d03e13c180bf1fe628aaaab616a76a39ff93c586a2403decc9aaa79`
- date: 2026-10-21
- mode: feature (the SUGGEST pass - owner standing order 2026-10-13)
- context pack: shared funnel/doctrine pack + AST-derived symbols + consumers + coverage gaps (tests) + live deferred/remediation manifest rows + run-1 backlog injected as already-planned + RSI ruleset (0 active)
- prompt: colibri/feature@2 (langfuse)
- cost: ~$0.0520 (in=3812 out=7397)

## grok-4.7 output (verbatim)

## What this module does
This suite locks the S2 invariant tier's offline contract: `parse_forge_results` turns forge stdout (summary lines, `Fail suite` blocks, and real `[FAIL:]` / `Suite result` output) into passed/failed counts plus `{test, reason}` failures, including multi-suite accumulation and line-start anchoring. `write_invariant_test` drops a Foundry harness into `proj/test`, and `run_forge_tests` invokes an injectable runner with `--match-contract`, returning `rc`/`raw` instead of raising when forge is missing. Assertions stop at that parse/run shape; they never build a funnel candidate or read `p2_inv.TEST_FILE`.

## Suggested add-ons
**Contest-scoped harness identity**
- Value: High
- Effort: S
- What: Let the harness file and contract name vary per corpus contest, defaulting to today's `RSIFunnelInvariant` / `TEST_FILE`, and drive `--match-contract` from that same name.
- Why it helps the user: Replay is a multi-contest corpus, but `test_write_invariant_test_creates_the_harness` locks a single `RSIFunnelInvariant.t.sol`. A second contest overwrites or mis-labels the only artifact this tier writes, so later title_key dedup cannot tell which contest an invariant failure came from.
- How: Extend `write_invariant_test` to take an optional contract name stored on `p2_inv.TEST_FILE` (keep the current string as the default). Have `run_forge_tests` pass that contract to `--match-contract`. Lock both in `test_write_invariant_test_creates_the_harness` and `test_write_and_run_invariant_test_runs_the_runner` (today the latter only checks that the flag is present).

**Skipped counts in the parsed denominator**
- Value: High
- Effort: S
- What: Return `skipped` from `parse_forge_results` and accumulate it across `Suite result` lines the same way `passed` and `failed` already accumulate.
- Why it helps the user: `REAL_FORGE` and `test_multi_suite_counts_accumulate` already contain `0 skipped`, and nothing reads it. A contest whose invariants were skipped currently looks like those tests never existed, so S2's contribution to the honest table is not like-for-like with suites that actually ran.
- How: Extend `parse_forge_results`. Assert `skipped == 0` in `test_parse_real_forge_shape`, and add a non-zero skipped suite to the string in `test_multi_suite_counts_accumulate` so accumulation is locked the way failed-count accumulation already is.

**Failure-to-candidate projection**
- Value: High
- Effort: M
- What: A pure helper that maps each parsed failure to a tier-tagged candidate `{title_key, test, reason, tier}` using the test symbol `parse_forge_results` already extracts (`RSIFunnelTest::testInvariant_...`, bare `testInvariant_...`, `testPoc0`).
- Why it helps the user: The suite docstring promises grounded candidates, but every test stops at counts and `{test, reason}`. S5 can only union and dedup what S2 actually emits; raw forge reasons are not a stable key across the three dialects this file already accepts.
- How: Add something like `failures_as_candidates` beside `parse_forge_results`, call it from `run_forge_tests` when a suite result is present, and assert the key on the existing failure fixtures in `test_parse_forge_results_fail_extracts_names_and_reasons`, `test_parse_real_forge_shape`, and `test_failure_lines_anchored_to_result_lines_not_message_text` (embedded `[PASS] testPoc1()` must not become the key).

## Nice-to-haves
- Assert `out.name == p2_inv.TEST_FILE` and that the `// stub` body is actually in the file in `test_write_invariant_test_creates_the_harness`.
- Assert the `--match-contract` value, not only flag presence, in `test_write_and_run_invariant_test_runs_the_runner`.
- Empty or whitespace stdout through `parse_forge_results` returns zero counts and `failures == []` without raising.
- When the injected runner sets `stderr`, include it in `raw` next to the `FileNotFoundError` path in `test_run_forge_tests_fail_soft_on_missing_binary`.
- Optional contest-id comment argument on `write_invariant_test` so the written harness can carry corpus identity without a new dependency.

- ACCEPT contest-scoped harness identity (per-contest contract/file name, default unchanged) - all cited test names verified; a second contest overwrites the single RSIFunnel artifact today.
- ACCEPT skipped counts in the parsed denominator - VERIFIED: the Suite-result regex captures passed/failed and stops before skipped; REAL_FORGE contains "0 skipped" unread.
- ACCEPT failure-to-candidate projection (title_key-tagged candidates from parsed failures, anchored against embedded-look-alikes).
- DEFER nice-to-haves (TEST_FILE/body asserts, match-contract value assert).
