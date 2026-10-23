# colibri feature review - colibri-bounty/colibri_bounty/match.py

- source: `colibri-bounty/colibri_bounty/match.py`
- model: grok-4.7 via api.x.ai (external second opinion, OFF-LADDER - does not count toward the three-model lock)
- sha256: `cc21d631bae61f6faebad911b5e404dc70f7673470ba2cf5b9f32c1130a8c209`
- date: 2026-10-21
- mode: feature (the SUGGEST pass - owner standing order 2026-10-13)
- context pack: module role + consumers + deliberate-decisions list (MATCHER_V3.md, gate EV-241/EV-245 lineage) + already-planned exclusions (FUNNEL_PLAN S1/S2v2/W6) + RSI ruleset (0 active) + remediation manifest (p2_llm slug pin)
- prompt: colibri/feature@2 (langfuse)
- cost: ~$0.0450 (in=5565 out=5637)

## grok-4.7 output (verbatim)

## What this module does

This is the offline matcher that pairs scanner findings with judged findings so replay can score precision and recall before any live-contest spend. v1 greedily locks title-token Jaccard pairs (`exact` on normalized-title equality, otherwise `fuzzy` at 0.34); v2 keeps those locks and only fills the remainder via folded stems and mechanism identifiers, and only when the title band still holds; v3 optionally sends the unmatched `[0.10, 0.34)` band to an injected adjudicator (`None` leaves v3 identical to v2). `count_duplicate_claims` counts scan findings that cleared the base threshold against a truth an earlier finding already claimed.

## Suggested add-ons

**Pair-channel explainer**
Value: High
Effort: S
What: A public read of one scan/truth pair: base Jaccard, folded Jaccard, shared mechanism tokens, mechanism Jaccard, and which v2 guardrail would accept or block it.
Why it helps the user: `MatchRecord` keeps only the winning score, so the failure cases called out in this file (title Jaccard in the low band, 0–2 shared identifiers) cannot be audited without re-deriving the channels by hand. Replay debugging and the next measured calibration both need that breakdown, without any change to who gets matched.
How: Extract the inner arithmetic in `match_findings_v2` (`base`, `folded`, `shared_m`, `mech_j`, and the `max(base, folded) >= threshold` / `len(shared_m) >= 2 and max(base, folded) >= band_floor` branches) into something like `_channel_scores`. Call it from `match_findings_v2` and from a new `explain_pair`. Leave thresholds, greedy lock order, and the title-band requirement untouched.

**Duplicate claims on the channels actually scored**
Value: High
Effort: M
What: A v2-aligned duplicate counter so a second scan finding that only clears the folded or mechanism channel against an already-claimed truth shows up in the double-report metric.
Why it helps the user: `count_duplicate_claims` only sees title Jaccard at `threshold`. `funnel_metrics` scores with v2/v3, so a scanner that double-reports one root cause through folding or shared identifiers never increments the metric this file exists to provide.
How: Add `count_duplicate_claims_v2` beside `count_duplicate_claims`. Run `match_findings_v2`’s lock-first pass (`used_s` by scan title, `used_t` by `issue_number`), then walk the same `supp` candidate list and count a remainder finding that would claim an already-used truth. Keep the v1 function’s threshold-only contract for existing tests. Keep twin handling as title-equality; do not revive a multiset.

**Unmatched-band export and adjudication yield**
Value: High
Effort: S
What: A deterministic dump of v2-unmatched title-band pairs (honest lexical score plus shared mechanism tokens), and a spend/yield tally for the paid channel: eligible, dropped by `max_pairs`, sent, promoted, fail-closed.
Why it helps the user: Thresholds here are measured, not tuned by feel, and the next calibration needs the pairs v2 left behind. `match_findings_v3` already builds that band, then discards every non-YES pair and never records how much of the `max_pairs` cap was used.
How: Lift the `band` loop in `match_findings_v3` (`llm_floor <= score < threshold`, sort, `band[:max_pairs]`) into `unmatched_title_band`. Add an optional `stats: dict | None = None` sink on `match_findings_v3`, filled after the slice and after the `zip(band, verdicts)` loop. Keep the default return as `list[MatchRecord]`. Keep promotion `score` as `round(max(base, folded), 4)` — do not invent a score.

## Nice-to-haves

- Optional synonym map argument defaulting to `SYNONYMS`, threaded through `_fold_stems` and `_folded_tokens`, so a contest vocabulary can be A/B measured without editing the calibrated default.
- A frozenset of method tags (`exact`, `fuzzy`, `folded`, `mechanism`, `llm`) next to `MatchRecord` so `metrics.py` and the match tests share one vocabulary.
- A sibling of `count_duplicate_claims` that also returns the claimed `truth_number`, so the honest table can name the double-reported issue rather than only an integer.
- If `adjudicator` raises, `match_findings_v3` treats it as an empty verdict list (all NO) so a paid-transport blip does not drop the deterministic v2 result.

### Triage (in-session GLM, verified against current bytes)
- ACCEPT pair-channel explainer (`_channel_scores`/`explain_pair`) - the arithmetic and both guardrail branches live inside `match_findings_v2` exactly as described; extraction changes no matching behavior.
- ACCEPT `count_duplicate_claims_v2` - VERIFIED: the v1 counter is threshold-only while funnel scoring runs v2/v3 channels; double-reporting through folded/mechanism channels is invisible to the metric.
- ACCEPT unmatched-band export + adjudication yield stats - VERIFIED in `match_findings_v3`: the band is built, sorted, sliced `[:max_pairs]` and discarded; eligible/capped/sent/promoted counts do not exist anywhere.
- REJECT "adjudicator raises -> treat as empty verdicts (all NO)" - contradicts the deliberate fail-closed contract (transport errors PROPAGATE so an incomplete measurement is visible; MATCHER_V3.md + gate EV-245 lineage). Also contradicted the context pack explicitly; suggested anyway.
- DEFER synonym-map arg, method-tag frozenset, dup-claims-with-truth-number.
