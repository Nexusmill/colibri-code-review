# colibri feature review - colibri-bounty/tests/test_match_v3.py

- source: `colibri-bounty/tests/test_match_v3.py`
- model: grok-4.7 via api.x.ai (external second opinion, OFF-LADDER - does not count toward the three-model lock)
- sha256: `a3e1fddb4888745408f4fe94dcc2cb4ec3f5ebc215d635b2368a71a3db5cf21d`
- date: 2026-10-21
- mode: feature (the SUGGEST pass - owner standing order 2026-10-13)
- context pack: shared funnel/doctrine pack + AST-derived symbols + consumers + coverage gaps (tests) + live deferred/remediation manifest rows + run-1 backlog injected as already-planned + RSI ruleset (0 active)
- prompt: colibri/feature@2 (langfuse) [effort medium - degenerate-retry regime]
- cost: ~$0.0528 (in=6365 out=6675)

## grok-4.7 output (verbatim)

## What this module does
This suite freezes matcher v3 in `match.match_findings_v3`: `adjudicator=None` is identical to `match_findings_v2`; an injected adjudicator may promote only unmatched pairs inside the title-score window (`method='llm'`), fail-closed on a short verdict list, never below the floor, never past a deterministic `max_pairs` cap, and never fewer truths than v2. It also locks greedy one-to-one, same-title over-exclusion, and the pending band-export / yield-stats surface (`unmatched_title_band`, `stats` keys). The frankendao, mover, and ajna shapes are the calibration set for pairs v2 leaves at 0.12–0.20 Jaccard.

## Suggested add-ons
- Value: High. Effort: S. What: Add `ScanFinding.detail`, `JudgedFinding.body`, both severities, and shared mechanism tokens to each pair dict sent to the adjudicator, beside the `score` / `scan_title` / `truth_title` keys these tests already lock. Why it helps the user: the measured misses are mechanism mismatches, not title matches; a paid opt-in judge that only sees titles cannot recover the pairs this suite exists to measure, so replay spend does not test the failure mode. How: extend the pair builder inside `match.match_findings_v3` (the dict read in `test_v3_frankendao_uint24_band_pair_converts`). Leave the `adjudicator=None` path identical to `match.match_findings_v2`.
- Value: High. Effort: M. What: A suppressed-promotion ledger of band pairs that were eligible or YES but not emitted, with a reason: lost greedy one-to-one, or skipped because a same-title twin was already consumed by v2. Why it helps the user: precision figures (16/60, 13/48) cannot tell a cold adjudicator from a promotion the matcher threw away, so `max_pairs` and window retunes are blind. How: append a list on the `stats` dict already accepted by `match.match_findings_v3`, at the assignment covered by `test_v3_greedy_one_to_one_on_llm_channel` and the title-equality skip in `test_v3_same_title_twin_never_double_matched`. Export only — do not adjudicate same-title twins and do not relax one-to-one.
- Value: Med. Effort: S. What: Stamp each `match.MatchRecord` with whether the truth severity is in `truth.PAID` / `truth.SEVERITIES` and whether `ScanFinding.severity` agrees. Do not filter or reorder matches. Why it helps the user: judging-truth recall used to gate live-contest spend mixes paid and non-paid severities; `_jf` forces High, so the honest table has no paid-eligible bit to slice. How: fill the stamp in both `match.match_findings_v2` and `match.match_findings_v3` from `truth.PAID` and `truth.SEVERITIES`. Contamination column and tier priority stay as they are.

## Nice-to-haves
- Publish the window bounds (0.10 floor, ~0.34 v2 threshold) as named constants beside `match.SYNONYMS` so replay tables and these tests share one denominator instead of literals.
- Echo `scan_idx` and `truth_idx` on the adjudicator pair dict (already on `unmatched_title_band` rows) so a verdict list joins back without title-string equality.
- Put a `band_rank` on each sent pair so a `max_pairs=1` run can be diffed against full `unmatched_title_band` order without re-sorting.

(no triage recorded)
