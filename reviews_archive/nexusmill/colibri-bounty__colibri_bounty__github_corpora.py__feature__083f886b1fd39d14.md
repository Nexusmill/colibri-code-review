# colibri feature review - colibri-bounty/colibri_bounty/github_corpora.py

- source: `colibri-bounty/colibri_bounty/github_corpora.py`
- model: grok-4.7 via api.x.ai (external second opinion, OFF-LADDER - does not count toward the three-model lock)
- sha256: `083f886b1fd39d14481a59ec5c94920f3c8379ddd66d4c19978fea1edefc4325`
- date: 2026-10-21
- mode: feature (the SUGGEST pass - owner standing order 2026-10-13)
- context pack: shared funnel/doctrine pack + AST-derived symbols + consumers + coverage gaps (tests) + live deferred/remediation manifest rows + run-1 backlog injected as already-planned + RSI ruleset (0 active)
- prompt: colibri/feature@2 (langfuse)
- cost: ~$0.0447 (in=4136 out=6074)

## grok-4.7 output (verbatim)

## What this module does

It acquires the offline contest corpus: list a GitHub org via `gh`, download codeload tarballs, and (when asked) dump non-PR issues, then upsert `github_repos`. Skip logic treats `pushed_at` plus an on-disk tarball as "code unchanged," but never treats that as "issues unchanged." `sync_org` is fail-soft and returns only counts.

## Suggested add-ons

**1. Name the incomplete set, not just the error count**
- Value: High
- Effort: S
- What: Put failed `org/name` identities (and the exception class) on the dict `sync_org` already returns, alongside `errors`.
- Why it helps the user: A replay denominator is wrong if some contests never landed. Today that fact is a counter plus an optional `progress` print, so a caller that persists only the stats dict cannot see which contests are missing.
- How: In `sync_org`'s `except`, append to `stats["failed"]` before the existing `progress(...)` line. Do not change the fail-soft continue, and do not write a row on issues failure (that guard stays).

**2. Fingerprint artifacts, and report issue drift without skipping the re-fetch**
- Value: High
- Effort: M
- What: Write a stdlib SHA-256 sidecar next to each tarball and issues dump. After the mandatory issues re-fetch, count `issues_changed` vs `issues_unchanged` against the previous file.
- Why it helps the user: Sherlock issue files mutate upstream and are always re-fetched on purpose. Without a snapshot id, a precision move between runs cannot be separated from findings-corpus drift. Sidecars avoid a schema change.
- How: Hash in `fetch_tarball` inside the existing `iter_content` loop; write `{dest}.sha256` only after `tmp.replace(dest)`. In `fetch_issues`, hash the existing `dest` before `write_text`, hash the new payload, return both. `sync_org` increments the two stats when `with_issues` is set. Never skip `fetch_issues` because the hash matched.

**3. Make `limit` a reproducible contest slice, and disclose the pre-slice census**
- Value: High
- Effort: S
- What: Sort the `list_org_repos` result by `RepoInfo.name` before `repos[:limit]`, and add `listed` (pre-slice), `limited_out`, and `archived` to `stats`.
- Why it helps the user: `stats["repos"]` is the post-limit length, and list order is whatever `gh` returned, so two capped syncs are not a like-for-like contest set. Name order matches the documented `YYYY-MM-sponsor[-name]` identity and makes a budget mean the same repos next run. This is acquisition accounting, not contest scoring or S2 target selection.
- How: In `sync_org`, after `list_org_repos` and before the limit slice, `repos.sort(key=lambda r: r.name)` and fill the extra stats keys from the pre-slice list (`RepoInfo.archived` is already parsed in `parse_repos`). Keep `limit=0` as "sync nothing."

## Nice-to-haves

- `sync_org(..., dry_run=True)`: run the existing `tarball_current` predicate and return would-fetch / would-skip names without calling `fetch_tarball` or `fetch_issues`.
- `corpus_status(conn)` beside `sync_org`: replay-eligible rows where `tarball_path` is a real file and, when `has_issues_dump` is required, the issues JSON exists — read-only, same columns the skip guard already uses.
- Naming-pattern mismatch count from the module docstring's `YYYY-MM-sponsor[-name]` rule, reported on the stats dict, not used as a sync gate.
- Optional `name_prefix` on `sync_org` (applied after the sort, before `limit`) with an `outside_window` count — a download window, not a scoring target.

- ACCEPT failed org/name identities on stats - VERIFIED: except block counts errors + progress-prints only; a persisted stats dict cannot name missing contests.
- ACCEPT sha256 sidecars + issues_changed/unchanged (never skip re-fetch) - hooks exact (fetch_tarball iter_content/tmp.replace; fetch_issues write_text); honors the always-re-fetch doctrine.
- ACCEPT deterministic limit slice (sort by name pre-slice + listed/limited_out/archived census) - VERIFIED: repos[:limit] unsorted, stats["repos"] post-limit.
- DEFER 4 nice-to-haves (dry_run, corpus_status, naming-mismatch count, name_prefix window).
