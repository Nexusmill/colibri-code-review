# colibri feature review - colibri-bounty/tests/test_solodit.py

- source: `colibri-bounty/tests/test_solodit.py`
- model: grok-4.7 via api.x.ai (external second opinion, OFF-LADDER - does not count toward the three-model lock)
- sha256: `bb0bcf1a67f9a84fe22cf0d658cbd96d44de1875a2fbd4a468fd9cf61d71baae`
- date: 2026-10-21
- mode: feature (the SUGGEST pass - owner standing order 2026-10-13)
- context pack: shared funnel/doctrine pack + AST-derived symbols + consumers + coverage gaps (tests) + live deferred/remediation manifest rows + run-1 backlog injected as already-planned + RSI ruleset (0 active)
- prompt: colibri/feature@2 (langfuse)
- cost: ~$0.0584 (in=4297 out=8302)

## grok-4.7 output (verbatim)

## What this module does
This suite locks the Solodit offline mirror: `SoloditClient.fetch_page` posts an authenticated, filtered page to `FINDINGS_URL` and retries HTTP 429 once through the injected sleep hook. `upsert_findings` last-write-wins rows into `solodit_findings` (wardens/tags JSON; present-but-null joins dropped, not fatal). `sync_findings` resumes from `sync_runs.next_page`, applies `max_pages` only to this invocation, and `reset_run` rewinds that checkpoint — a bounded corpus pull, not live-contest spend.

## Suggested add-ons
### 1. Filter-scoped checkpoint
- **Value:** High
- **Effort:** M
- **What:** Plumb `filters` (and page size) through the resumable sync and bind the checkpoint to that query, not only to `source` / `next_page`.
- **Why it helps the user:** `fetch_page` already accepts `filters` (impact and the rest of the body the auth test asserts), but every `sync_findings` call in this suite is an unfiltered firehose. Resuming page N after a filter change mixes two result sets into one `solodit_findings` table — the same unlike-denominator class this project already refuses to merge. A contest-shaped slice (protocol, impact) is also the only way `--max-pages` stays useful against Solodit’s full catalog.
- **How:** Add a `filters` argument on `sync_findings` and pass it straight into `SoloditClient.fetch_page`. Persist a fingerprint of `filters` + `pageSize` on the `sync_runs` row in `db.SCHEMA`. On resume, a mismatch raises `ValueError` (same fail-closed posture as `test_max_pages_must_be_positive`) until `reset_run` clears the row. Keep comparing `max_pages` to pages fetched this invocation only — do not revive the cumulative `pages_done` check `test_max_pages_bounds_this_invocation_not_checkpoint` forbids.

### 2. SyncReport rate and rewrite accounting
- **Value:** High
- **Effort:** S
- **What:** Fill `SyncReport` with the rate budget the page payload already carries, retry count, and insert-vs-rewrite counts.
- **Why it helps the user:** `page_payload` includes `rateLimit.limit/remaining`, and `RATE_WINDOW_S`, `RATE_MAX`, and `retry_after_s` already exist, but the suite only asserts `pages_fetched`, `next_page`, and `status`. `upsert_findings` returns `1` for both the first write and the title rewrite (`"first"` → `"second"`), so a re-sync can change measurement inputs with an `"ok"` report. Operators need that spend and that drift disclosed; they do not need a new client.
- **How:** Extend `SyncReport` as populated by `sync_findings`: `rate_limit` / `rate_remaining` from the JSON `fetch_page` already returns, `retries` from the 429 path that calls `retry_after_s`, and `inserted` / `rewritten` from `upsert_findings`. Distinguish rewrite inside the existing `UPSERT` (pre-select on id, or `changes()` plus a title/tags compare) without changing last-write-wins. Compare `remaining` to `RATE_MAX` only to record it on the report.

### 3. Proactive pace inside the existing sleep hook
- **Value:** Med
- **Effort:** S
- **What:** Before the next `post`, if `rateLimit.remaining` is exhausted, sleep through the injected hook instead of waiting for a 429.
- **Why it helps the user:** The only network spend in this module is the paged pull, and a `max_pages` run is supposed to be capped and boring. Today pacing is reactive (`test_fetch_page_retries_429_once` sleeps only after 429). Using the `rateLimit` object already on every successful page keeps a bounded sync inside `RATE_WINDOW_S` / `RATE_MAX` without a second HTTP stack or a new dependency.
- **How:** In `SoloditClient.fetch_page`, after a successful JSON body, if `remaining` is 0, call the same `sleep` the 429 path uses, with a delay from `retry_after_s` clamped by `RATE_WINDOW_S`. Count that sleep on `SyncReport` (add-on 2). Do not add retries beyond the one 429 already specified, and do not let pacing advance `sync_runs.next_page`.

## Nice-to-haves
- Call `load_api_key` at the start of `sync_findings`, before any `sync_runs` write, so a missing key cannot leave a half-advanced checkpoint that only `reset_run` can unwind.
- Copy `metadata.totalPages` (already parsed by `fetch_page`) onto `SyncReport` so a bounded run can show “page 51/60” without a second request.
- Once the filter fingerprint exists, `reset_run` should clear it in the same update that sets `next_page=1` and `pages_done=0`.
- The `progress` callback `sync_findings` already accepts (`progress=None` in these tests) should receive page index plus `rate_remaining`, so a CLI can print mid-run without waiting for the final report.
- Add a `protocol_name` / `impact` index in `db.SCHEMA` when filtered sync lands, so offline slices of `solodit_findings` do not scan the full mirror.

- ACCEPT filter-scoped checkpoint (filters+pageSize fingerprint on sync_runs; mismatch raises until reset) - fail-closed, consistent doctrine; fetch_page already accepts filters while sync_findings is firehose-only.
- ACCEPT SyncReport rate/rewrite accounting (rateLimit payload fields, retries, inserted vs rewritten) - upsert returns 1 for first write AND rewrite today.
- ACCEPT proactive pace via the existing sleep hook when rateLimit.remaining == 0.
- DEFER nice-to-haves per file.
