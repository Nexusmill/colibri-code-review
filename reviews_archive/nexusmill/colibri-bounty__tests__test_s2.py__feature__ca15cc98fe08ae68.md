# colibri feature review - colibri-bounty/tests/test_s2.py

- source: `colibri-bounty/tests/test_s2.py`
- model: grok-4.7 via api.x.ai (external second opinion, OFF-LADDER - does not count toward the three-model lock)
- sha256: `ca15cc98fe08ae68daf808cc49ab0ed5b61ecc6dbbebc19011974f6f3bc29231`
- date: 2026-10-21
- mode: feature (the SUGGEST pass - owner standing order 2026-10-13)
- context pack: shared funnel/doctrine pack + AST-derived symbols + consumers + coverage gaps (tests) + live deferred/remediation manifest rows + run-1 backlog injected as already-planned + RSI ruleset (0 active)
- prompt: colibri/feature@2 (langfuse)
- cost: ~$0.0534 (in=2704 out=7994)

## grok-4.7 output (verbatim)

## What this module does

This suite locks the S2 invariant dump contract and its S5 wiring: `s2.dump_findings` writes `scan_findings_s2_inv.json`, and `s5.load_tier(..., "inv")` reads that list back, including the empty list. It also pins `inv` as the lowest `s5.TIER_PRIORITY` entry and checks that `s5.union_findings` lets an agent finding own a shared title while recording the inv row in `info["dups"]`.

## Suggested add-ons

**1. Non-scoring inv corroboration on the union winner**
Value: High
Effort: S
What: When `s5.union_findings` drops an inv row as a title dup, copy that row’s `detail` and `path` onto the surviving finding under a non-scoring field, and leave `info["dups"]` and winner `tier` unchanged.
Why it helps the user: These tests show inv’s only extra signal is execution-grounded detail (`test/S2Invariants.t.sol`). Priority correctly keeps agent as owner, but that trace is then invisible to whatever consumes the union, so a replay already paid for never shows up in the measurement.
How: Extend `s5.union_findings`. Lock it in `test_union_agent_wins_over_inv_same_root_cause`: winner `tier` stays `"agent"`, `info["dups"]` stays `[("inv", "peg insolvency on scale rise")]`, and the new field carries the inv `detail`/`path`. Do not feed that field into scoring, and do not merge agent-tier and union figures.

**2. Dump provenance sidecar that does not touch the findings list**
Value: Med
Effort: S
What: `s2.dump_findings` also writes a sibling stdlib JSON manifest (findings written, source filename, whether the caller passed a list) next to `scan_findings_s2_inv.json`.
Why it helps the user: `test_dump_empty_is_loadable_empty` makes `[]` the only empty signal `s5.load_tier` can return. A later denominator cannot tell “dump ran, nothing violated” from “this contest never produced an inv file,” which breaks like-for-like replay accounting. A sibling file keeps the existing equality roundtrip intact.
How: Extend `s2.dump_findings`; add a reader beside `s5.load_tier` (do not change `load_tier`’s return value, or `test_dump_and_load_roundtrip` / `test_dump_empty_is_loadable_empty` break). Assert the sidecar from those two tests. This is not a clean-vs-all rollup and does not change `s5.honest_table`.

## Nice-to-haves

- Add the unique-title case next to `test_union_agent_wins_over_inv_same_root_cause` so an inv-only root cause survives union with `tier == "inv"`.
- In that same dup test, assert the winner keeps agent `severity` `"High"` rather than inv’s `"Medium"`.
- Pin full `s5.TIER_PRIORITY` order `agent > t5 > poc > inv` in `test_inv_tier_exists_in_priority_after_poc` (today only `[-1]` and set equality are locked).
- Assert the roundtrip finding keeps `title` / `severity` / `detail` / `path` as the dump schema, still via `s2.dump_findings` and `s5.load_tier`.

- ACCEPT non-scoring inv corroboration on the union winner - VERIFIED: union_findings drops the inv row's execution-grounded detail/path when agent owns the root cause (the tier's only extra signal); proposed field stays out of scoring, tier/dups assertions unchanged.
- ACCEPT dump provenance sidecar + reader (load_tier return untouched) - test-side twin of the s2.py ledger suggestion; empty-dump-vs-never-ran stays ambiguous today.
- DEFER 4 nice-to-haves (inv-only survivor case, winner-severity assert, FULL TIER_PRIORITY order pin [today only [-1]+set are locked], roundtrip schema assert).
