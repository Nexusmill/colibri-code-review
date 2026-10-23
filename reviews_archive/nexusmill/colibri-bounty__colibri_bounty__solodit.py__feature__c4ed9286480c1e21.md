# colibri feature review - colibri-bounty/colibri_bounty/solodit.py

- source: `colibri-bounty/colibri_bounty/solodit.py`
- model: grok-4.7 via api.x.ai (external second opinion, OFF-LADDER - does not count toward the three-model lock)
- sha256: `c4ed9286480c1e21d778d650584892d6cab9e73e9bd9a761bccd6371fc52c616`
- date: 2026-10-21
- mode: feature (the SUGGEST pass - owner standing order 2026-10-13)
- context pack: shared funnel/doctrine pack + AST-derived symbols + consumers + coverage gaps (tests) + live deferred/remediation manifest rows + run-1 backlog injected as already-planned + RSI ruleset (0 active)
- prompt: colibri/feature@2 (langfuse)
- cost: ~$0.0599 (in=4515 out=8479)

## grok-4.7 output (verbatim)

## What this module does

It is the Solodit write path into `corpus.db`: `SoloditClient.fetch_page` posts the documented findings contract (rate limit, one 429 retry), and `sync_findings` resumes from `sync_runs.next_page`, checkpointing after each page. `upsert_findings` idempotently stores `FIELDS` plus JSON from `_wardens` / `_tags`; `reset_run` rewinds the cursor; `load_api_key` only loads a key. The live API is owner-disabled, so this file does not read the cache back — there is no protocol lookup, coverage snapshot, or contract check against a saved payload.

## Suggested add-ons

### Protocol known-issue lookup (pre-scan)
- **Value:** High
- **Effort:** S
- **What:** `findings_for_protocol(conn, protocol_name, *, known_before=None, impacts=None, min_quality=None)` returning the rows already written by `UPSERT` (title, summary, impact, quality_score, report_date, firm_name, source_link, wardens, tags, fetched_at).
- **Why it helps the user:** Duplicate doctrine is a per-protocol check before any scan, and this module never exposes the cache. Callers otherwise invent SQL, and they cannot apply an as-of cutoff on `report_date`, so issues published after contest open get mixed into the known set (or the check is skipped and paid replay spends on public bugs).
- **How:** New function beside `upsert_findings`. Query `solodit_findings` on `lower(trim(protocol_name))` (free text from upstream, not a stable id). Optional `report_date < known_before`, `impact` in the caller list, and `quality_score >= min_quality` — columns already in `FIELDS`. Leave competitor pre-check out; that is not knowable here. Do not auto-match titles; S5 owns matching and those denominators stay separate.

### Cache disclosure for an empty hit list
- **Value:** Med
- **Effort:** S
- **What:** `cache_status(conn, protocol_name=None)` with `sync_runs` status / `next_page` / `pages_done` / `message` / `finished_at`, plus `COUNT(*)`, `COUNT(DISTINCT protocol_name)`, and `MAX(fetched_at)` on `solodit_findings` (and the same count scoped to one protocol when given).
- **Why it helps the user:** With the API offline, a zero-row pre-check is ambiguous: mirror never loaded, last `sync_findings` ended `error`, or the protocol truly has no Solodit issues. Honest measurement needs that denominator next to the lookup, not a silent empty list.
- **How:** Read `sync_runs` the same way `sync_findings` and `reset_run` do (`WHERE source=?`, `SOURCE`). Aggregates only; do not infer “clean” inside this function — return the counts and let the caller disclose them.

### Offline contract re-check (no network)
- **Value:** Med
- **Effort:** S
- **What:** `contract_gaps(payload) -> list[str]` over one findings-page dict: missing `FIELDS` keys, absent `metadata.totalPages` / `totalResults`, and nested paths `_wardens` / `_tags` already walk (`issues_issue_finders` → `wardens_warden.handle`, `issues_issuetagscore` → `tags_tag.title`).
- **Why it helps the user:** The module docstring requires the contract to be re-verified against live bytes before the first pull, but nothing in code does that. A pure checker can be pointed at a saved page or mirror sample the day the API returns, so drift shows up before `sync_findings` writes a half-shaped corpus.
- **How:** Pure function over the dict `SoloditClient.fetch_page` already returns. Compare to `FIELDS` and the key paths in `_wardens` and `_tags`. Do not call the transport; do not enable the deferred client.

## Nice-to-haves

- Batch helper `findings_for_protocols(conn, names, known_before=None)` as one `IN` query returning `{protocol: rows}` plus a `cache_status` blob, so a contest’s protocol list is one pre-check.
- `upsert_findings` count of skipped rows (`id` missing) surfaced on `SyncReport`, so a mirror load can see dropped records without changing the upsert.
- Full-snapshot replace beside `upsert_findings` (upsert, then delete ids not in the set) for a complete mirror reload only — do not hook it to `sync_findings`, whose page cursor is additive on purpose.
- When the API is actually back, thread `fetch_page`’s existing `filters` through `sync_findings` only with a distinct `sync_runs` key, so a filtered cursor cannot resume the unfiltered one.

- ACCEPT findings_for_protocol lookup (as-of report_date cutoff) - VERIFIED STRONG: the module has NO read path on solodit_findings at all; the duplicate doctrine (per-protocol pre-scan check) has no executable hook. API-offline ruling respected (pure cache read).
- ACCEPT cache_status disclosure (sync_runs state + counts beside any lookup) - hooks exact.
- ACCEPT contract_gaps offline re-check - the docstring's own "MUST re-verify against live bytes" has no code form; pure function, no transport.
- DEFER 4 nice-to-haves (batch IN helper, skipped-row count, snapshot replace, filtered-cursor key).
