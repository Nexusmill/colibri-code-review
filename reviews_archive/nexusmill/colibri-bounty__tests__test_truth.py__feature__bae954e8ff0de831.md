# colibri feature review - colibri-bounty/tests/test_truth.py

- source: `colibri-bounty/tests/test_truth.py`
- model: grok-4.7 via api.x.ai (external second opinion, OFF-LADDER - does not count toward the three-model lock)
- sha256: `bae954e8ff0de831a07f7dbe639c841ada3a89c0124cdb61c0aa20f23b7ba7a6`
- date: 2026-10-21
- mode: feature (the SUGGEST pass - owner standing order 2026-10-13)
- context pack: shared funnel/doctrine pack + AST-derived symbols + consumers + coverage gaps (tests) + live deferred/remediation manifest rows + run-1 backlog injected as already-planned + RSI ruleset (0 active)
- prompt: colibri/feature@2 (langfuse) [effort medium - degenerate-retry regime]
- cost: ~$0.0301 (in=2899 out=4044)

## grok-4.7 output (verbatim)

## What this module does
This suite locks the judging-oracle contract in `truth`: `parse_judging_issues` turns contest issue JSON into `JudgedFinding` rows (warden, title, severity, sponsor labels, duplicate flag) and drops unjudged issues. `valid_findings` keeps paid severities only and collapses same-title reports to one root cause (lowest `issue_number`, `also_reported_by` filled). `load_truth` reads that JSON back from disk for offline replay.

## Suggested add-ons
- Value: High. Effort: S. What: On duplicate collapse, keep today’s representative rule but record the cluster’s severity set and sponsor-label union on the surviving `JudgedFinding`. Why it helps the user: the duplicate fixture already has High and Medium on one root cause, and only the lowest issue number is kept — S5 precision against that oracle cannot tell a clean paid hit from a judge disagreement unless the cluster is disclosed. How: in `valid_findings`, after grouping with `title_key` / `norm_tokens`, set new fields on the min-`issue_number` `JudgedFinding` (do not change which row wins).
- Value: High. Effort: M. What: Make `select_contests` the measurement stratum: contests with a loadable judging file and a non-empty `valid_findings` set, plus an explicit skip list (missing file, zero paid findings, unreadable JSON). Why it helps the user: clean-contest vs full-union figures are already different denominators; that split should come from truth selection with skips visible, not an ad hoc path filter. How: `select_contests` calls `load_truth` per judging file and returns `(selected, skips)` — corpus skips stay disclosed; do not swallow them into an empty success.
- Value: Med. Effort: S. What: Drive inclusion from `PAID` / `SEVERITIES` (optional per-contest override) instead of an implicit High/Medium cut, and record which classes were excluded. Why it helps the user: `test_valid_findings_are_paid_classes_only` drops Low and Informational while sponsor labels are parsed and unused — contests that pay a different set cannot change the denominator without breaking like-for-like reporting. How: `valid_findings(fs, paid=PAID)` defaults to today’s classes; `select_contests` / `load_truth` may attach a contest policy. Default path stays High+Medium so current asserts hold.

## Nice-to-haves
- Stamp the collapse key from `title_key` onto `JudgedFinding` at parse time so later tiers reuse one root-cause id.
- Have `parse_judging_issues` return a dropped-count for `STOP` / unjudged labels (the Needs Triage case) for the contamination column.
- Let `load_truth` accept an already-decoded issue list so corpus walks can reuse the same parser without a temp file.

- ACCEPT cluster disclosure on the collapse survivor (severity set + sponsor-label union; representative rule unchanged) - the High/Medium one-root-cause fixture exists; cited test name verified.
- ACCEPT select_contests as measurement stratum returning (selected, skips) - skips stay disclosed, never empty-success.
- ACCEPT PAID/SEVERITIES-driven inclusion with excluded-class record (default High+Medium unchanged).
- DEFER 3 nice-to-haves (title_key stamp at parse, dropped-count, decoded-list input).
