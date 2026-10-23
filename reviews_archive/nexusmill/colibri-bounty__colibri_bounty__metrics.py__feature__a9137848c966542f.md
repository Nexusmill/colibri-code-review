# colibri feature review - colibri-bounty/colibri_bounty/metrics.py

- source: `colibri-bounty/colibri_bounty/metrics.py`
- model: grok-4.7 via api.x.ai (external second opinion, OFF-LADDER - does not count toward the three-model lock)
- sha256: `a9137848c966542f9d393e95e70cf244f5a7a3f02e2a2980ffa5561ec8422e0e`
- date: 2026-10-21
- mode: feature (the SUGGEST pass - owner standing order 2026-10-13)
- context pack: shared funnel/doctrine pack + AST-derived symbols + consumers + coverage gaps (tests) + live deferred/remediation manifest rows + run-1 backlog injected as already-planned + RSI ruleset (0 active)
- prompt: colibri/feature@2 (langfuse)
- cost: ~$0.0720 (in=2577 out=11134)

## grok-4.7 output (verbatim)

## What this module does

`score()` is the replay scorecard: it turns one scan list, one paid-truth list, a `list[MatchRecord]`, a caller-supplied `dup_claims` count, and `elapsed_s` into the ratios the funnel reports. Precision is `len(matches) / len(scan)`; recall is distinct `MatchRecord.truth_number` over `len(truth_paid)`; severity accuracy is exact `scan_severity` vs judged `severity` on those pairs; duplicate accuracy is `1 - dup_claims / n_scan` (1.0 if the scan is empty). `_r()` rounds every ratio to 4 decimals, and a zero denominator becomes 0.0 for precision, recall, and severity accuracy.

## Suggested add-ons

**1. Numerator ledger on the score dict**
Value: High. Effort: S.
What: Return the counts `score()` already computes and then drops: `distinct_truths`, `sev_ok`, unmatched scan rows (`n_scan - matched`), unmatched paid truths (`n_truth - distinct_truths`), and the `dup_claims` that went into `dup_acc`.
Why it helps the user: A saved score dict is what the honest table and any later audit see. Today recall’s numerator and severity accuracy’s numerator disappear, so a stored run cannot be checked against the module’s own “computable from the counts” rule, and like-for-like denominators are easy to mis-copy (match-record count vs distinct truths).
How: Extend the dict `score()` returns. Keep every existing key and the current 0.0-on-empty numeric contract so `tests/test_metrics.py` stays valid. Leave `_r()` as the only rounding path.

**2. Zero-denominator visibility, additive**
Value: High. Effort: S.
What: An extra `undefined` list naming which ratios had a zero denominator (`precision` when `n_scan == 0`, `recall` when `n_truth == 0`, `severity_acc` when `matched == 0`, `dup_acc` when `n_scan == 0`).
Why it helps the user: Fail-soft tiers and contests with no paid truths both hit this function. A 0.0 precision on an empty scan is indistinguishable from “findings emitted, none matched,” and a 0.0 recall on an empty truth set reads as failure rather than vacuous. Incomplete measurements are supposed to stay visible; this is that rule for denominators. Do not blend clean vs all, and do not merge agent-tier with union.
How: Set the list inside `score()` next to the existing empty branches. Do not change the current floats (precision/recall/severity_acc stay 0.0; empty-scan `dup_acc` stays 1.0) so the deterministic, adjudicator-free contract holds.

**3. Judged-severity slice, not folded into the headline**
Value: High. Effort: M.
What: Recall and severity agreement broken out by judged severity, as a separate dict.
Why it helps the user: The spend decision is whether High/Medium paid truths are in the matched set. A single 26.7% can be informational hits only. The slice uses only data this function already walks, and it is a different cut from clean-vs-all (those stay side by side, never blended).
How: New `score_by_severity(truth_paid, matches)` beside `score()`, built from the same `sev_by_truth` map (`t.issue_number` → `t.severity`) and the `sev_ok` loop over `m.truth_number` / `m.scan_severity`. Per judged severity: distinct matched truth numbers over truths of that severity, plus exact-severity hits over matches of that severity. Do not write these into top-level `precision` / `recall`. Precision by emitted severity is not available today — `score()` only reads `len(scan)` — so do not invent a scan-item schema.

## Nice-to-haves

- `pool(rows)` beside `score()` that sums the ledger counts and recomputes via `_r()`, never averages rounded ratios; refuse mixed agent-tier and union rows, and never blend clean with all.
- `side_by_side` that calls `score()` twice and returns `{all, clean}` with no blended key, encoding the file’s side-by-side rule.
- Extra key for the match-derived double-report rate from `matched` and `distinct_truths` (formula already in the module docstring), leaving caller-supplied `dup_claims` / `dup_acc` unchanged.
- Optional binomial Wilson band in stdlib `math` on the exposed precision and recall counts, labeled count-level not contest-clustered, so 26.7 vs 27.1 is not over-read.

- ACCEPT numerator ledger on score dict - VERIFIED: returned dict drops distinct_truths/sev_ok/dup_claims while the module docstring promises "computable from MatchRecords alone"; saved runs unauditable.
- ACCEPT zero-denominator `undefined` list - VERIFIED: 0.0 fallbacks exist for precision/recall/severity_acc and 1.0 for empty-scan dup_acc (grok's How preserves that contract exactly).
- ACCEPT score_by_severity slice (separate dict, never folded) - hooks (sev_by_truth, sev_ok loop) exact; honestly notes precision-by-emitted-severity is unavailable (score only len()s scan).
- DEFER 4 nice-to-haves (pool, side_by_side, match-derived dup rate, Wilson band).
