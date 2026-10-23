# colibri feature review - colibri-bounty/colibri_bounty/truth.py

- source: `colibri-bounty/colibri_bounty/truth.py`
- model: grok-4.7 via api.x.ai (external second opinion, OFF-LADDER - does not count toward the three-model lock)
- sha256: `ab21090a197344d0481dc10b9643b7453454367a8739b60da5e97a8f8bdb4f83`
- date: 2026-10-21
- mode: feature (the SUGGEST pass - owner standing order 2026-10-13)
- context pack: shared funnel/doctrine pack + AST-derived symbols + consumers + coverage gaps (tests) + live deferred/remediation manifest rows + run-1 backlog injected as already-planned + RSI ruleset (0 active)
- prompt: colibri/feature@2 (langfuse)
- cost: ~$0.0526 (in=3591 out=7565)

## grok-4.7 output (verbatim)

## What this module does
`truth.py` is the paid-finding denominator behind every precision/recall figure: `load_truth` / `parse_judging_issues` turn a Sherlock `-judging` dump into `JudgedFinding` rows, and `valid_findings` keeps `PAID` severities and collapses same-`title_key` reports to one root cause. `select_contests` then picks a deterministic, year-balanced sample of contests that have both a code tarball and an in-range paid count.

## Suggested add-ons
1. Value: High. Effort: M. What: union duplicate clusters by in-dump issue cross-references, not only identical `title_key`. Why it helps the user: `valid_findings` already documents that distinct bugs sharing a title collapse, and the same bug under two titles does not; both errors change the one-to-one denominator the matcher is scored against. `has_duplicates` is parsed and then unused in grouping. How: add `_duplicate_refs(body: str) -> set[int]` (stdlib `re`, same style as `norm_tokens`) and call it from `valid_findings` after the `groups` dict is built. Union member lists when `has_duplicates` is set and a body cites another row's `issue_number` in the same dump. Keep the existing representative rule (`members.sort` by `issue_number`, other wardens into `also_reported_by`). Do not change `title_key` or `norm_tokens`. Record title-only merges vs link-merges on a new defaulted field of `JudgedFinding` so the honest table can keep disclosing the v1 approximation.

2. Value: High. Effort: S. What: an opt-in sponsor-label slice of the paid set, with drop counts disclosed, default unchanged. Why it helps the user: `parse_judging_issues` already stores `sponsor_labels`, but `valid_findings` treats every High/Medium as oracle truth. A sponsor-disputed subset and a judge-severity subset are different denominators; publishing one number for both is the same reporting failure mode as conflating agent-tier and union. How: add a kw-only `sponsor_pred=None` on `valid_findings` (or a thin wrapper `slice_findings` that `valid_findings` calls before the `title_key` group step). `None` means today's `PAID` behavior so `tests/test_truth.py` stays green. The predicate reads `JudgedFinding.sponsor_labels` only — do not hardcode verdict vocabulary in this module. Return the kept list as now, plus a small counts mapping (`kept`, `dropped_severity`, `dropped_sponsor`) from that same loop so the table can render the slice the way it always renders contamination.

3. Value: Med. Effort: S. What: a stable digest of the collapsed denominator. Why it helps the user: headline figures (16/60, 13/48, the clean-contest subset) are only comparable if you can see whether truth moved or the scanner moved. This module owns the canonical fields; callers should not re-derive identity. How: add `truth_digest(fs: list[JudgedFinding]) -> str` using stdlib `hashlib` over sorted `(issue_number, severity, sorted(title_key(title)), also_reported_by)`. Feed it the list `valid_findings` returns, not the raw `load_truth` list, so the digest matches the denominator actually scored.

## Nice-to-haves
- Kw-only `severities=PAID` on `valid_findings` so High-only and Medium-only denominators do not need a second collapse path.
- A `selection_frame` helper beside `select_contests` that tallies skips already taken in that loop (no tarball, `JSONDecodeError`/`OSError`, below `min_valid`, above `max_valid`) while `select_contests` keeps returning `list[tuple[str, int]]`.
- Set a duplicate-width int on the representative when `valid_findings` fills `also_reported_by`, so later tables can split unique vs widely reported without re-scanning.
- Have `parse_judging_issues` also return how many issues were dropped for lacking a `SEVERITIES` label (process notes), for the same disclosure column.

- ACCEPT duplicate-cluster union via in-dump cross-references - VERIFIED STRONG: has_duplicates is parsed onto JudgedFinding and never read; grouping is title_key-only; the docstring itself records the title-collision approximation. Adds a defaulted field so the v1 approximation stays disclosed.
- ACCEPT opt-in sponsor-label slice with drop counts (default PAID unchanged) - sponsor_labels stored, never used; disputed vs judge-severity are different denominators (the agent/union conflation class).
- ACCEPT truth_digest over the collapsed denominator (complements replay_runner's file-level truth_sha256).
- DEFER 4 nice-to-haves (severities kwarg, selection_frame tally, duplicate-width int, unlabeled-drop count).
