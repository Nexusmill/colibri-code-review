# colibri feature review - colibri-bounty/tests/test_match.py

- source: `colibri-bounty/tests/test_match.py`
- model: grok-4.7 via api.x.ai (external second opinion, OFF-LADDER - does not count toward the three-model lock)
- sha256: `9cfda15e799654eb6390450daf93598dc8467cd1491255b0fe7f01eeebd80a90`
- date: 2026-10-21
- mode: feature (the SUGGEST pass - owner standing order 2026-10-13)
- context pack: shared funnel/doctrine pack + AST-derived symbols + consumers + coverage gaps (tests) + live deferred/remediation manifest rows + run-1 backlog injected as already-planned + RSI ruleset (0 active)
- prompt: colibri/feature@2 (langfuse)
- cost: ~$0.0601 (in=2664 out=9123)

## grok-4.7 output (verbatim)

## What this module does

This suite locks v1 `match.match_findings` on hand-built `scanner.ScanFinding` / `truth.JudgedFinding` pairs: identical titles score 1.0 with `method == "exact"`, a fuzzy hit above threshold is kept and a sub-threshold title is omitted, and greedy assignment lets only one scan finding claim a given truth. Total misses return `[]`; severity, paid/valid flags, synonyms, v2/v3, and the scanner baselines are never exercised.

## Suggested add-ons

**Version-separated matcher delta**
Value: High
Effort: M
What: A free, offline report that runs one shared fixture set through `match.match_findings`, `match.match_findings_v2`, and `match.match_findings_v3` and lists per-version `MatchRecord` score/method deltas.
Why it helps the user: Live figures already disagree across versions and denominators (v3 agent-tier 16/60 vs v2-era union 13/48). This shows whether a precision move came from matcher logic, without adding those rows together.
How: Add a helper beside `match.match_findings` that calls all three with `adjudicator=None` and emits three separate result lists keyed by `MatchRecord.method` / `MatchRecord.score` / `MatchRecord.truth_number`. Lock it with the same `sf`/`jf` pairs this file already uses. Do not sum into one precision.

**Paid-severity denominator slice**
Value: High
Effort: S
What: Precision/recall grouped by paid severity, as extra rows next to the all-findings denominator.
Why it helps the user: Every fixture here is `sev="High"` and the paid flag is hardcoded `False`, so a title hit on an unpaid or low issue counts the same as a paid High. Spend decisions need the paid band kept like-for-like, with the contamination column still rendered.
How: Filter truths with `truth.valid_findings` and `truth.PAID`, band with `truth.SEVERITIES`, then join on `MatchRecord.truth_number`. Keep the unfiltered `match.match_findings` result as its own row; do not drop contamination or merge agent-tier with union.

**Oracle ceiling / stub floor**
Value: Med
Effort: S
What: Two offline baselines through the same matcher path: known-truth emissions vs an empty scan.
Why it helps the user: This file only matches hand-written titles, so a recall miss cannot be split into "scanner never emitted it" vs "matcher refused credit." A ceiling and a floor stop matcher tuning when the gap is upstream.
How: Run `scanner.OracleScanner` and `scanner.StubScanner` outputs through `match.match_findings` against `truth.load_truth`. Report each baseline separately beside the real scanner row. No live-contest calls; `adjudicator=None`.

## Nice-to-haves

- Stamp `truth.title_key` of the claimed title onto `MatchRecord` so S5 dedup and matcher claims share one key.
- When `match.SYNONYMS` supplies the overlap, set a distinct `MatchRecord.method` without emitting sub-threshold pairs.
- Round-trip one judging snippet through `truth.parse_judging_issues` into `match.match_findings` so `jf()`'s field order cannot drift from the parser.

- ACCEPT version-separated matcher delta report (v1/v2/v3 on shared fixtures) - hooks real (three matcher versions; the 16/60 vs 13/48 version-drift question is live).
- ACCEPT paid-severity denominator slice - VERIFIED: every fixture defaults sev="High" and none pass through truth.valid_findings; unpaid/low never exercised. (Prose correction: the hardcoded False in jf() is has_duplicates, not a "paid flag" - JudgedFinding carries no paid field.)
- ACCEPT oracle-ceiling / stub-floor baselines through the matcher - VERIFIED: scanner.OracleScanner and scanner.StubScanner both exist with exactly those names; test_replay_runner pins the oracle P/R=1.0 plumbing, but no matcher-side ceiling/floor rows exist.
- DEFER 3 nice-to-haves (title_key stamp on MatchRecord, distinct SYNONYMS method tag, parse_judging_issues round-trip fixture).
