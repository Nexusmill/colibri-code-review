# colibri feature review - colibri-bounty/tests/test_github_corpora.py

- source: `colibri-bounty/tests/test_github_corpora.py`
- model: grok-4.7 via api.x.ai (external second opinion, OFF-LADDER - does not count toward the three-model lock)
- sha256: `9f78529f92e2ef6d47bd4522ecfa8e26b87cea6ae1f2c65bd722b0b7e73e7cda`
- date: 2026-10-21
- mode: feature (the SUGGEST pass - owner standing order 2026-10-13)
- context pack: shared funnel/doctrine pack + AST-derived symbols + consumers + coverage gaps (tests) + live deferred/remediation manifest rows + run-1 backlog injected as already-planned + RSI ruleset (0 active)
- prompt: colibri/feature@2 (langfuse)
- cost: ~$0.0591 (in=4674 out=8294)

## grok-4.7 output (verbatim)

## What this module does

This suite locks the offline GitHub corpus sync: `sync_org` lists an org through `gh`, maps pages with `parse_repos`, and downloads a tarball only when `pushed_at` changed or the file is missing on disk. A `pushed_at` match skips the tarball only — issues are still refreshed, with pull requests stripped — and a failed issues fetch records no row, so the skip guard cannot block a retry. `limit=0` considers zero repos; a negative limit raises.

## Suggested add-ons

### Resume cursor after a rate-limited issues fetch
- **Value:** High
- **Effort:** S
- **What:** Opt-in `start_after` so a rerun continues at the first repo that was not recorded, instead of walking the org from the top.
- **Why it helps the user:** A secondary rate limit leaves no row (`stats["errors"]`, `fetched == 0`). The next full sync still re-fetches issues for every earlier repo, because a tarball skip must not skip issues. On a large org that is the expensive prefix `limit` exists to avoid, paid in `gh` calls before any scanner spend.
- **How:** Keep listing order stable in `gc.list_org_repos`. In `gc.sync_org`, if `start_after` is set, skip `RepoInfo.name` values at or before that cursor before the tarball/issues decision. A call without the cursor keeps today's always-refresh-issues behavior. On the existing issues-failure branch, still insert nothing and return the failed name as `stats["resume_after"]`.

### Durable issues outcome that cannot poison the skip guard
- **Value:** High
- **Effort:** M
- **What:** Persist a completed dump's issue count, and a failed fetch's error text, without writing `pushed_at` / `has_issues_dump` on failure.
- **Why it helps the user:** The row the rest of the funnel can see is only a boolean `has_issues_dump`. That cannot tell "N non-PR findings", "legitimate empty dump", and "gh exited 1" apart, so a later precision denominator can silently drop contests. Failure must stay unrecorded on `github_repos` or the `pushed_at` skip blocks every retry.
- **How:** Extend `db.SCHEMA` with a side table (org, name, kind, issues_count, issues_error, recorded_at), not new skip columns on `github_repos`. Write the count from the list `gc.fetch_issues` already returns (PRs removed) only on success inside `gc.sync_org`. On the failure path covered by `test_sync_org_issues_failure_not_recorded`, insert the stderr snippet into the side table and leave `github_repos` empty.

### Dry-run of the same skip predicate
- **Value:** Med
- **Effort:** S
- **What:** `sync_org(..., dry_run=True)` returns the usual stats plus a per-repo action: fetch tarball, skip tarball, refresh issues, or stopped by limit — with no `getter` call and no issues `gh` call.
- **Why it helps the user:** Before a long org walk the operator needs to see that a matching `pushed_at` still means an issues refresh, and that a missing tarball path counts as a fetch. `limit` is a budget, but today the only way to see the plan is to spend the calls.
- **How:** Branch in `gc.sync_org` on the predicate already locked by `test_sync_org_skips_unchanged_repo` and `test_skip_guard_requires_tarball_on_disk` (`pushed_at` match and `tarball_path` is an existing file). Do not call `gc.fetch_tarball` or the injected getter. Keep `limit=0` as zero repos and `limit<0` as `ValueError`.

## Nice-to-haves

- Store tarball size and a stdlib `hashlib.sha256` from `gc.fetch_tarball` on the existing row so two replays can show they measured the same artifact.
- Add `stats["archived"]` from `RepoInfo.archived` without dropping archived contest repos from the corpus.
- Have `parse_repos` set a contest slug on `RepoInfo` from `name` (the `2026-02-jupiter` shape) for later joins — selection policy stays elsewhere.
- Include `split_concat_json` page count in `sync_org` stats so a truncated `gh` pagination is visible in the run summary.

- ACCEPT start_after resume cursor (skips recorded prefix; issues-always-refresh behavior untouched) - the expensive-prefix-after-rate-limit problem is real (failed fetch records no row by design).
- ACCEPT durable issues-outcome side table (count on success, error text on failure; never skip-columns on github_repos) - has_issues_dump boolean cannot distinguish N-findings/empty/gh-error.
- ACCEPT dry-run over the locked skip predicate (no getter/gh calls).
- DEFER 4 nice-to-haves (tarball size+sha on row, archived count, RepoInfo slug, pagination page count).
