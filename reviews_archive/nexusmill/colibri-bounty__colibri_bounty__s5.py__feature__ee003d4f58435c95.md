# colibri feature review - colibri-bounty/colibri_bounty/s5.py

- source: `colibri-bounty/colibri_bounty/s5.py`
- model: grok-4.7 via api.x.ai (external second opinion, OFF-LADDER - does not count toward the three-model lock)
- sha256: `ee003d4f58435c956a5b25f4962d7215e54102bd4db7ea502e67151c82fb462e`
- date: 2026-10-21
- mode: feature (the SUGGEST pass - owner standing order 2026-10-13)
- context pack: module role + consumers + deliberate-decisions list (MATCHER_V3.md, gate EV-241/EV-245 lineage) + already-planned exclusions (FUNNEL_PLAN S1/S2v2/W6) + RSI ruleset (0 active) + remediation manifest (p2_llm slug pin)
- prompt: colibri/feature@2 (langfuse)
- cost: ~$0.0510 (in=3223 out=7433)

## grok-4.7 output (verbatim)

## What this module does
S5 is the offline replay scorer: it loads per-tier finding dumps, unions them under a fixed owner priority (`agent` > `t5` > `poc` > `inv`) with `title_key` dedup, and scores that union through the v3 matcher (paid adjudicator only when injected). `honest_table` renders per-contest precision/recall against judging truth, always showing the contamination flag and keeping agent-tier cells separate from the union denominator.

## Suggested add-ons
1. **Owning-tier incremental true positives**
   - Value: High
   - Effort: M
   - What: Of union matches, count distinct truths by the tier that won the `title_key`, as a separate breakdown from per-tier and union precision.
   - Why it helps the user: The spend question is what `t5` / `poc` / `inv` still add after a higher tier already claimed the root cause. Per-tier `matched` double-counts; union precision hides which tier paid for the hit.
   - How: `union_findings` already stamps `"tier"` on kept findings; `funnel_metrics` drops it when building `ScanFinding`. Keep an owners list aligned with `scan` (same order as `union`) and, after `matchm.match_findings_v3`, bucket distinct `r.truth_number` by that owner. Return it as its own key (do not fold into agent or union P/R). Render it in `honest_table` as extra columns, leaving `TIER_PRIORITY` unchanged.

2. **Labeled clean-subset vs all-contest rollup**
   - Value: High
   - Effort: S
   - What: Aggregate the table into two explicitly labeled summaries — all contests, and `contamination` clean-only — each with its own matched/scan and matched/truths denominators. Emit agent-tier and union rollups as separate figures, never one blended precision.
   - Why it helps the user: Live reads already quote those subsets (union ~27% vs clean ~35.5%), but `honest_table` only prints rows, so every consumer re-sums and can recreate the merged-denominator bug. A rollup next to the flag column makes the pre-spend number reproducible.
   - How: Add a function beside `honest_table` that takes the same `results` and `contamination` dicts. Split on `contamination.get(name)` (still render every contest in the table). Micro-average within each split from `union.matched`, `union.scan_findings` / `union.n`, and `union.truth_findings`; repeat independently for `tiers.agent`. Label each line with which denominator it used.

3. **One scoring entry point for the table contract**
   - Value: High
   - Effort: M
   - What: A single call that loads every tier, scores each tier alone, unions, scores the union, and returns the dict shape `honest_table` already reads (`tiers[k].n/matched` plus `union`), including `poc` and `inv`.
   - Why it helps the user: Nothing in this file builds that shape, yet the table hardcodes only `agent` and `t5` while `FINDINGS_FILES` / `TIER_PRIORITY` already include S2 and S4. Callers will drift, and landed `inv` stays invisible in the only consumer-facing artifact.
   - How: New function composing `load_tier` over `TIER_PRIORITY`, `funnel_metrics` per tier (own denominator, `adjudicator=None` unless passed), then `union_findings` + `funnel_metrics` on the union. Extend `honest_table`'s header and `tier_cell` to walk `TIER_PRIORITY` instead of the two hardcoded keys. Do not merge those cells into the union P/R columns.

## Nice-to-haves
- `load_tier` treats a missing dump as `[]`; add a presence check over `FINDINGS_FILES` and show absent vs empty in the tier cell so a skipped tier is not read as zero recall.
- `union_findings` already returns `dups` and keeps `keyless` findings; surface dup count and keyless count on the table — they inflate the precision denominator and are not deduped.
- Return the `records` `funnel_metrics` already builds (it currently reduces them to `methods` counts) so replay scripts can trend channel mix without re-matching.
- Sibling to `honest_table`: the same row fields as dicts, so run-over-run diffs do not parse markdown.

### Triage (in-session GLM, verified against current bytes)
- ACCEPT owning-tier incremental TPs - VERIFIED: `union_findings` stamps `tier` on every kept finding; `funnel_metrics` drops it in the `ScanFinding` comprehension. Hook exact.
- ACCEPT labeled clean-vs-all rollups - VERIFIED: `honest_table` prints per-contest rows only; every consumer re-sums by hand (the merged-denominator bug class is real history).
- ACCEPT tier-generic table + single scoring entry point - VERIFIED against fresh bytes: `FINDINGS_FILES`/`TIER_PRIORITY` carry agent/t5/poc/inv (4 tiers) while `honest_table` hardcodes agent+t5 columns; the inv tier (W4 S2 v1, landed 2026-10-20) is invisible in the only consumer-facing artifact. Strongest suggestion of the batch.
- DEFER all four nice-to-haves (presence check, dups/keyless surfaced, records exposure, dict sibling) - kept in deferred_manifest.
