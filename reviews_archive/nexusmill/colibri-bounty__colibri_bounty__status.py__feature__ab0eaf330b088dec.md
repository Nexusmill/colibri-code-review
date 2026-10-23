# colibri feature review - colibri-bounty/colibri_bounty/status.py

- source: `colibri-bounty/colibri_bounty/status.py`
- model: grok-4.7 via api.x.ai (external second opinion, OFF-LADDER - does not count toward the three-model lock)
- sha256: `ab0eaf330b088decebf8383f234a7cd275fe7bd2645f0de54e9713b3b3fc2af9`
- date: 2026-10-21
- mode: feature (the SUGGEST pass - owner standing order 2026-10-13)
- context pack: shared funnel/doctrine pack + AST-derived symbols + consumers + coverage gaps (tests) + live deferred/remediation manifest rows + run-1 backlog injected as already-planned + RSI ruleset (0 active)
- prompt: colibri/feature@2 (langfuse)
- cost: ~$0.0403 (in=2945 out=5729)

## grok-4.7 output (verbatim)

## What this module does

`status.py` is the operator's pre-run corpus sanity view. `corpus_status` counts Solodit findings, loads the latest `sync_runs` row for `source='solodit'`, aggregates `github_repos` by kind (repos, issues dumps, tarballs as independent sums), and marks each name in `MIRRORS` present or absent by whether `root/mirrors/<name>/.git` is a directory. `render_md` turns that dict into tracked `CORPORA_STATUS.md`; `write_status_md` stamps UTC time and writes it. It does not derive replay readiness, sync drift, or mirror age.

## Suggested add-ons

**1. Replay-ready intersection per kind**
Value: High
Effort: S
What: Count repos that have both a tarball and an issues dump (and the complement), not only the two independent sums.
Why it helps the user: A measurement run can only replay contests that have both artifacts. `with_tarball` and `with_issues` cannot be intersected, so "40 / 40" can still mean zero replayable repos — the denominator this view exists to show before any run.
How: In the `GROUP BY kind` query inside `corpus_status`, add `SUM(CASE WHEN tarball_path IS NOT NULL AND has_issues_dump THEN 1 ELSE 0 END)` (both columns are already in that statement) onto each `kinds[kind]` dict. Add a column for it in the table loop in `render_md`.

**2. Solodit sync-gap line**
Value: High
Effort: S
What: One derived line: no `sync_runs` row versus a run exists, plus the numeric gap between findings `count` and `total_results`, beside the stored `status` (do not invent a new success enum or treat the gap as proof the crawl is short — rows and `totalResults` may not be 1:1).
Why it helps the user: The Solodit section is four raw bullets. A missing run or a large count/`total_results` gap is the pre-run signal that the corpus denominator changed, and today the operator has to compute it by hand. Doctrine wants that gap disclosed, not inferred.
How: Compute it in `corpus_status` from `sol` and `run` (fields `render_md` already reads: `total_results`, `status`, and the findings count) into `st["solodit"]`, and emit one line at the top of the Solodit section in `render_md`.

**3. Mirror age, not just presence**
Value: Med
Effort: S
What: Replace the binary present/absent string with absent, or present plus a freshness hint from git metadata mtime.
Why it helps the user: The module contract is synced / present / stale, but `mirror_states` only checks `.git` is a directory. A mirror cloned once and never updated still reads `present`, so a replay can run against a frozen tree without the status file saying so.
How: Extend the `mirror_states` comprehension in `corpus_status` with `Path.stat` on `.git/FETCH_HEAD`, falling back to `.git/HEAD` (stdlib only; if stat fails, keep `present`). `render_md` already prints `state` verbatim.

## Nice-to-haves

- In `write_status_md`, skip the write when the existing file matches the new render aside from the `generated_at` line, so tracked `CORPORA_STATUS.md` does not churn on timestamp-only refreshes.
- In `render_md`, emit an explicit "none" row when `st["kinds"]` or `st["mirrors"]` is empty so a blank section is not ambiguous.
- In `corpus_status`, attach `corpus.db` size and mtime via `Path.stat` and print them next to `db_path` in `render_md`.

- ACCEPT replay-ready intersection per kind - VERIFIED: with_tarball and with_issues are independent SUMs; "40/40" can still mean zero replayable contests.
- ACCEPT solodit sync-gap derived line (count vs total_results, missing-run case).
- ACCEPT mirror freshness hint (FETCH_HEAD mtime) over binary present/absent.
- DEFER 3 nice-to-haves (timestamp-only churn guard, explicit none rows, db size/mtime).
