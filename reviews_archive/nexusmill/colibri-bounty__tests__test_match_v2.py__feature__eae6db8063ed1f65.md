# colibri feature review - colibri-bounty/tests/test_match_v2.py

- source: `colibri-bounty/tests/test_match_v2.py`
- model: grok-4.7 via api.x.ai (external second opinion, OFF-LADDER - does not count toward the three-model lock)
- sha256: `eae6db8063ed1f652ffc6933a77c756720cb38a37c1d8bcdcf12addc06c54b30`
- date: 2026-10-21
- mode: feature (the SUGGEST pass - owner standing order 2026-10-13)
- context pack: shared funnel/doctrine pack + AST-derived symbols + consumers + coverage gaps (tests) + live deferred/remediation manifest rows + run-1 backlog injected as already-planned + RSI ruleset (0 active)
- prompt: colibri/feature@2 (langfuse) [effort medium - degenerate-retry regime]
- cost: ~$0.0548 (in=4942 out=7491)

## grok-4.7 output (verbatim)

## What this module does
This pytest module locks matcher v2’s supplementary channels (synonym fold, plural-stem fold, mechanism-identifier band) on top of the calibrated base matcher. It checks that known blocked-true pairs recover, adjudicated cold pairs stay unmatched, base hits are preserved, and `match_findings_v2` never covers fewer truths than `match_findings`. It also pins `explain_pair` channel arithmetic, `count_duplicate_claims_v2` on folded and mechanism twins, and `_fold_stems` plural-family behavior, all on in-file `ScanFinding` / `JudgedFinding` fixtures.

## Suggested add-ons
- Value: High. Effort: S. What: a deterministic v2⊆v3 coverage gate on the same fixtures this file already uses. Why it helps the user: published precision is the v3 figure, while the only structural “supplements never drop a base hit” lock (`test_v2_never_matches_fewer_truths_than_base`) stops at v2, so a v3 regression of a synonym or mechanism recovery would not fail this suite. How: add a sibling of `test_v2_never_matches_fewer_truths_than_base` that calls `match.match_findings_v3` on those scan/truth lists with the paid adjudicator left unset, and assert the v3 `truth_number` set is a superset of the v2 set. Do not merge agent-tier and union denominators; do not pass a live adjudicator.

- Value: High. Effort: S. What: a synonym-table recovery gate driven by `match.SYNONYMS`, not only the circumvent/bypass pair in `test_v2_recovers_synonym_blocked_match`. Why it helps the user: recall of every shipped synonym family is part of the measurement, but a table edit can drop a family while the three hand-written recovery tests stay green. How: parametrize titles from each `match.SYNONYMS` entry through `match_findings` (expect no link) and `match_findings_v2` (expect the fixture `truth_number`); pair each entry with one unrelated title in the style of `test_v2_keeps_cold_pairs_cold` so a wider table cannot mint a cold hit.

- Value: Med. Effort: S. What: a title-key coherence check on pairs this file already treats as one bug. Why it helps the user: S5 dedups with `truth.title_key` before matching; a v2 hit whose scan and truth titles do not share a key can still be counted as two denominator rows, which breaks like-for-like recall. How: in `test_v2_recovers_synonym_blocked_match`, `test_v2_recovers_plural_fold_and_mechanism_match`, `test_v2_recovers_mechanism_band_match`, and `test_v2_preserves_base_matches`, call `truth.title_key` on both titles and assert one key (or record the split next to the existing `truth_number` assert). Keep using the in-file fixtures; do not read the corpus drive.

## Nice-to-haves
- Let `_jf` take severity from `truth.SEVERITIES` and add one non-High truth that still matches, pinning that severity is not a match key.
- On `test_v2_preserves_base_matches`, assert the `MatchRecord` score/method fields already returned, not only `truth_number`, so a threshold edit fails here.
- Hoist the setCurvePoint `ScanFinding` / `JudgedFinding` shared by `test_v2_recovers_mechanism_band_match` and `test_count_duplicate_claims_v2_sees_the_mechanism_channel` so those two gates cannot drift.
- Pass `has_duplicates=True` through `_jf` once and assert `match_findings_v2` still returns the same `truth_number`.
- Add one non-member of `match.SYNONYMS` to `test_v2_keeps_cold_pairs_cold` so synonym-table growth cannot create a cross-family hit.

(no triage recorded)
