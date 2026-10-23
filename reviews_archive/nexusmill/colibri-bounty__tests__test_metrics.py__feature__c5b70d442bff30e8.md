# colibri feature review - colibri-bounty/tests/test_metrics.py

- source: `colibri-bounty/tests/test_metrics.py`
- model: grok-4.7 via api.x.ai (external second opinion, OFF-LADDER - does not count toward the three-model lock)
- sha256: `c5b70d442bff30e84b18075aaff72d9cd5f3254f17f002c0e0e47f1857e496e5`
- date: 2026-10-21
- mode: feature (the SUGGEST pass - owner standing order 2026-10-13)
- context pack: shared funnel/doctrine pack + AST-derived symbols + consumers + coverage gaps (tests) + live deferred/remediation manifest rows + run-1 backlog injected as already-planned + RSI ruleset (0 active)
- prompt: colibri/feature@2 (langfuse)
- cost: ~$0.0583 (in=3107 out=8683)

## grok-4.7 output (verbatim)

## What this module does
This pytest module locks the funnel's offline scoring math on synthetic findings. It builds `JudgedFinding` and `ScanFinding` rows, runs them through `scanner.OracleScanner` and `match.match_findings` (or injects `MatchRecord` rows directly), and checks that `metrics.score` returns precision, recall, severity_acc, dup_acc, matched, and elapsed_s. It also pins empty inputs to 0.0 and proves dup_acc falls when `match.count_duplicate_claims` sees a second claim on the same root cause.

## Suggested add-ons

### v2 and v3 score locks, kept apart
- **Value:** High
- **Effort:** S
- **What:** Two new tests, one per matcher, that score a fixed synthetic set on the deterministic free path and assert precision, recall, and matched separately for each version.
- **Why it helps the user:** The published figures (v3 agent-tier 16/60, v2-era union 13/48) come from these matchers, but this file only drives `match.match_findings`, so a v2/v3 drift never fails the suite. Separate tests keep the two denominators from being conflated.
- **How:** Mirror the fixture shape in `test_known_counts` and `test_oracle_scores_perfect`. Replace the hand-built `MatchRecord` list with the return of `match.match_findings_v2` in one test and `match.match_findings_v3` in another, both with `adjudicator=None`, and pass those records to `metrics.score`. Do not share one expected table across both versions, and do not enable the paid channel.

### Paid vs stop denominator lock
- **Value:** High
- **Effort:** S
- **What:** A test that scores only the paid, non-stop subset and asserts recall/precision denominators equal that subset's length, not the raw constructed list.
- **Why it helps the user:** Like-for-like denominators are the measurement doctrine, and a mixed paid/stop list was already a real reporting-bug class. Today every case hands `metrics.score` a pre-filtered list (`truth_paid`), so a change in the paid/stop filter never moves an assert.
- **How:** Extend the `JudgedFinding` list built in `test_known_counts` through `truth.valid_findings`, keep rows `truth.PAID` accepts, drop `truth.STOP`, and pass only that list as the truth argument to `metrics.score`. Assert `m["recall"]` and `m["matched"]` against the filtered length. Leave `test_zero_division_guards` as the empty-input case.

### title_key / synonym identity check
- **Value:** Med
- **Effort:** S
- **What:** A test that the titles already used here have a stable `title_key`, and that synonym groups collapse to one key while unrelated titles do not.
- **Why it helps the user:** S5 dedups on `title_key` before matching, but dup_acc is measured from raw titles via `match.count_duplicate_claims`. If synonym folding and the dup counter disagree, union counts and dup_acc tell different stories about the same findings.
- **How:** New test calling `truth.norm_tokens` and `truth.title_key` on the titles in `test_oracle_scores_perfect` and `test_duplicate_claims_measured`. Walk `match.SYNONYMS` and assert one key per synonym group and distinct keys across groups. Do not add a new duplicate counter; keep using `match.count_duplicate_claims`.

## Nice-to-haves
- Drive `scanner.StubScanner.scan` the same way `test_oracle_scores_perfect` drives `OracleScanner.scan`, and assert the empty fail-soft tier hits the 0.0 guards in `test_zero_division_guards`.
- On the perfect-oracle and empty cases, assert `metrics.score` still returns the contamination field (it must render; do not pin a rate).
- Parameterize the single High→Medium miss in `test_known_counts` across `truth.SEVERITIES` so `severity_acc` is not proven for only one pair.

- ACCEPT v2/v3 score locks kept apart (adjudicator=None, separate expected tables) - VERIFIED: the file drives only match_findings v1 (zero v2/v3 refs); published figures come from v2/v3.
- ACCEPT paid-vs-stop denominator lock (pre-filtered truth_paid today means a filter change never moves an assert).
- ACCEPT title_key/synonym identity check (S5 dedup key vs dup_acc counter coherence).
- DEFER 3 nice-to-haves (StubScanner empty-tier drive, contamination field assert, severity parameterization).
