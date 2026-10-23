# colibri feature review - colibri-bounty/colibri_bounty/p2_inv.py

- source: `colibri-bounty/colibri_bounty/p2_inv.py`
- model: grok-4.7 via api.x.ai (external second opinion, OFF-LADDER - does not count toward the three-model lock)
- sha256: `45b4027112f6e7de930559bae10a468e0ecd74d6b812d0193acacae9cc911952`
- date: 2026-10-21
- mode: feature (the SUGGEST pass - owner standing order 2026-10-13)
- context pack: shared funnel/doctrine pack + AST-derived symbols + consumers + coverage gaps (tests) + live deferred/remediation manifest rows + run-1 backlog injected as already-planned + RSI ruleset (0 active)
- prompt: colibri/feature@2 (langfuse)
- cost: ~$0.0732 (in=3648 out=10986)

## grok-4.7 output (verbatim)

## What this module does

This is the S2 forge boundary: `write_invariant_test` writes the caller-supplied suite to `test/RSIFunnelInvariant.t.sol`, `run_forge_tests` runs `forge test --match-contract … -vv` fail-soft (missing forge, timeout, and other exceptions become `rc == -1` plus raw text, never a raise), and `parse_forge_results` turns that text into accumulated pass/fail counts and deduped failure name/reason records. A failing invariant is the execution-grounded candidate handed downstream; the returned dict does not say whether a zero came from invariants that held, a compile/setup failure, or a match that ran nothing.

## Suggested add-ons

### 1. Tier disposition on the forge result
Value: High
Effort: S
What: Add `status` and a short `status_reason` to the dict `run_forge_tests` already returns: forge-missing/timeout, compile-or-setup failure, no-tests-matched, invariants-held, invariant-failed.
Why it helps the user: S5 treats this tier as a measurement. Today `passed == 0` and `failed == 0` is also what a timeout, a compiler error, and a `--match-contract` miss look like, so a contest that never executed an invariant is indistinguishable from one whose properties held. That understates the partial foundry coverage this tier is supposed to record.
How: In `run_forge_tests`, after `parse_forge_results`, branch on the existing exception path (`rc == -1`), `proc.returncode`, and whether `failures` is empty. Classify from phrases already in `combined` (`Compiler run failed`, `No tests match the provided pattern`) without raising. Leave `parse_forge_results` count logic alone so `tests/test_p2_inv.py` fixtures stay valid.

### 2. Restrict the forge run to the generated file
Value: High
Effort: S
What: Add `--match-path test/RSIFunnelInvariant.t.sol` and `--match-test testInvariant_` next to the current `--match-contract`.
Why it helps the user: `parse_forge_results` adds every `Suite result:` line in the output (the in-code note: overwriting dropped earlier suites). `--match-contract RSIFunnel` is a regex filter, so another contract whose name contains that token shares the passed/failed totals S5 will treat as this tier’s denominator. The like-for-like set is the generated `testInvariant_*` file only.
How: Extend the argv in `run_forge_tests` (`run([FORGE, "test", …])`). Default `match_path` to `Path("test") / TEST_FILE` and `match_test` to `testInvariant_`, both overridable the same way `match_contract` already is, so injected `runner` tests can assert the argv.

### 3. Forge JSON channel, text parser kept as fallback
Value: High
Effort: M
What: Request `--json` when forge is actually invoked, and map suite/test objects to the same `{passed, failed, failures}` shape with stdlib `json`. If stdout is not that object, fall back to `parse_forge_results`.
Why it helps the user: Candidate identity (test name + reason) is what S5 dedups and matches. `parse_forge_results` already special-cases four text shapes; each new forge summary format is another denominator drift. One JSON object is a stable identity for the inv tier, still offline, still no new dependency, with the text path left in place for fixtures and older forge.
How: Add `parse_forge_json` beside `parse_forge_results`; return `None` unless the top level is Foundry’s suite → test → status object. In `run_forge_tests`, append `--json` to the argv, try stdout, and on `None` or `JSONDecodeError` call `parse_forge_results(combined)` as today. Keep `rc` and `raw`. Do not remove the text function — `tests/test_p2_inv.py` and `tests/test_p2_poc.py` feed it strings.

## Nice-to-haves

- After `run_forge_tests`, restore or unlink `TEST_FILE` if `write_invariant_test` created it, and return a `tree_mutated` flag so a later replay of the same corpus tree is not running last run’s suite — disclosure stays a returned fact, not a hidden write.
- Capture the `skipped` count already on the `Suite result` line inside `parse_forge_results` (the current regex stops at `failed`).
- Lift the hardcoded `timeout=600` out of the default `runner` lambda in `run_forge_tests` into a parameter; injected runners already bypass it.
- Record held tests with an anchored `(?m)^\[PASS\] … (gas: N)$` match in `parse_forge_results`, same end-of-line rule as the FAIL loop, so the property-held set is explicit and message bodies are not scanned.
- Stamp `forge --version` onto the `run_forge_tests` result via a second fail-soft subprocess so two replays can be compared when Foundry moves.

- ACCEPT tier disposition (status/status_reason on run_forge_tests) - VERIFIED: timeout/compile-fail/no-match all return {passed:0, failed:0}; held-vs-never-ran indistinguishable to S5.
- ACCEPT --match-path + --match-test testInvariant_ restriction - VERIFIED: argv carries only --match-contract (a REGEX); Suite-result accumulation means any name-matching suite's totals enter this tier's denominator.
- ACCEPT forge --json channel with parse_forge_results fallback - the code's own comment names forge --json "the structural fix" for the newline-forged-line residual; text path preserved for fixtures.
- DEFER 5 nice-to-haves (TEST_FILE cleanup/tree_mutated, skipped count, timeout param, anchored PASS record, forge --version stamp).
