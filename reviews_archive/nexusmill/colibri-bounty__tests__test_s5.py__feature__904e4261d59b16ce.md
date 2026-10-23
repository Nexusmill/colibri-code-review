# colibri feature review - colibri-bounty/tests/test_s5.py

- source: `colibri-bounty/tests/test_s5.py`
- model: grok-4.7 via api.x.ai (external second opinion, OFF-LADDER - does not count toward the three-model lock)
- sha256: `904e4261d59b16ce2027f17103e8caf900dbe72a465ee819cb1a0ef7d9b51f68`
- date: 2026-10-21
- mode: feature (the SUGGEST pass - owner standing order 2026-10-13)
- context pack: shared funnel/doctrine pack + AST-derived symbols + consumers + coverage gaps (tests) + live deferred/remediation manifest rows + run-1 backlog injected as already-planned + RSI ruleset (0 active)
- prompt: colibri/feature@2 (langfuse)
- cost: ~$0.0808 (in=5672 out=11573)

## grok-4.7 output (verbatim)

## What this module does
This pytest suite pins the S5 synthesis contract: `load_tier` reads per-tier JSON dumps (a missing file is an empty list), `union_findings` keeps one survivor per exact title-key under fixed tier priority, and leaves morphological variants and keyless findings uncollapsed. `funnel_metrics` scores that union with the offline replay matcher, forwarding an adjudicator only when the caller opts in, and attributes `owner_tps` to the tier that won the key. `score_contest`, `honest_table`, and `honest_rollup` render per-tier and union figures with the contamination column and a labeled clean-vs-all split, without merging agent-tier and union denominators.

## Suggested add-ons
**Missing dump vs true zero**
Value: High
Effort: S
What: Record whether each tier dump was absent or present-and-empty, and show that on the table without treating both as `n=0`.
Why it helps the user: A contest that never ran inv/poc currently renders the same `0 (0)` as a tier that ran and found nothing, so a pre-spend read can credit a tier that did not execute.
How: Keep `s5.load_tier` returning `[]` for a missing `s5.FINDINGS_FILES` entry (still fail-soft, no raise). Add a presence probe on that same lookup; have `s5.score_contest` store `missing` vs `empty` on each tier dict it already builds for `s5.TIER_PRIORITY`. Extend `s5.honest_table` to render not-run beside the existing `n (matched)` cell. Do not drop or gate the contamination column.

**Channel-partitioned rollup**
Value: High
Effort: S
What: Stop summing deterministic matcher matches and opt-in llm matches into one precision/recall.
Why it helps the user: The same pair moves from `matched=0` to `matched=1` solely when an adjudicator is passed, and `methods` already records `llm`. `honest_rollup` today adds `matched`/`scan_findings`/`truth_findings` across contests with no channel label, which is the same denominator-conflation class as blending agent-tier and union figures.
How: Extend `s5.honest_rollup` to partition the existing `all` and `clean` blocks by whether each contest's `funnel_metrics` `methods` contains `llm` (absent or empty means deterministic). Extend the rollup lines `s5.honest_table` already appends with that partition label and its own matched/scan and matched/truth denominators. Leave `adjudicator=None` as the free deterministic path; do not default the paid channel on, and do not add llm matches into the deterministic precision.

**Severity-sliced precision and recall**
Value: High
Effort: M
What: Report precision/recall per severity, with each slice carrying its own scan and truth denominators, beside the unweighted union figure.
Why it helps the user: Every finding and `JudgedFinding` already carries `severity`, and union priority even prefers a High survivor over a Medium duplicate, but `funnel_metrics` publishes one unweighted precision. The pre-spend number is not interpretable if High and low-severity claims share a denominator.
How: In `s5.funnel_metrics`, bucket `matched`, `scan_findings`, and `truth_findings` by `truth.SEVERITIES` using the severity already on union entries and on `JudgedFinding`. Have `s5.score_contest` pass those buckets through on both per-tier and union results. Render them in `s5.honest_table` and `s5.honest_rollup` as extra labeled rows, not folded into the headline union precision/recall. Do not change title-key dedup or `s5.TIER_PRIORITY`.

## Nice-to-haves
- Corpus walker that calls `truth.select_contests` and `truth.load_truth`, then `s5.score_contest` and `s5.honest_rollup`, letting matcher transport errors propagate rather than becoming all-NO.
- Second, labeled recall in `s5.funnel_metrics` over `truth.valid_findings`, kept apart from the all-judged truth denominator.
- Print `s5.union_findings` `info["dups"]` and `info["counts"]` on the `s5.honest_table` row next to `owner_tps` so priority wins are visible, not only the surviving owner.
- Count keyless survivors in `s5.funnel_metrics` and show that count in `s5.honest_table` so empty titles cannot silently inflate `scan_findings`.
- Stamp the title-key derived via `truth.norm_tokens` onto `s5.union_findings` survivors so a dedup decision can be audited without collapsing morphological variants.

(no triage recorded)
