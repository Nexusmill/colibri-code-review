# colibri feature review - colibri-bounty/colibri_bounty/db.py

- source: `colibri-bounty/colibri_bounty/db.py`
- model: grok-4.7 via api.x.ai (external second opinion, OFF-LADDER - does not count toward the three-model lock)
- sha256: `a0748c3e76ca3fe7fc15c77103d67b314ffd6bb2af286edd88295a50394b5bb8`
- date: 2026-10-21
- mode: feature (the SUGGEST pass - owner standing order 2026-10-13)
- context pack: shared funnel/doctrine pack + AST-derived symbols + consumers + coverage gaps (tests) + live deferred/remediation manifest rows + run-1 backlog injected as already-planned + RSI ruleset (0 active)
- prompt: colibri/feature@2 (langfuse)
- cost: ~$0.0438 (in=2562 out=6451)

## grok-4.7 output (verbatim)

## What this module does

`db.py` is the corpus SQLite opener: `connect()` ensures the parent directory, opens a `sqlite3.Connection` with `Row` factory, WAL, and foreign keys, then applies `SCHEMA`. The schema is three rebuildable tables — `solodit_findings` (issue cache plus impact/protocol/firm/date indexes), `github_repos`, and `sync_runs` (per-source fetch cursor) — with no query API and no migration path.

## Suggested add-ons

1. **Value:** High. **Effort:** S. **What:** A `readonly` open on `connect` that does not create a database. **Why it helps the user:** Every caller currently `mkdir`s and `executescript`s, so a status or replay read of a missing path becomes a zero-row corpus indistinguishable from a finished sync with no findings; a measurement against that file looks like an empty result rather than a missing cache. **How:** Extend `connect(db, *, readonly=False)`. When `readonly`, use `sqlite3.connect(f"file:{db}?mode=ro", uri=True)`, set `row_factory`, and skip `mkdir` plus `SCHEMA`. Write path stays as it is. `tests/test_status.py` and any solodit read path should pass `readonly=True`.

2. **Value:** High. **Effort:** S. **What:** A schema-shape check that fails closed with “delete and refetch”, not a migrator. **Why it helps the user:** `CREATE TABLE IF NOT EXISTS` will not add columns or indexes to an existing disposable file, so a rebuilt `SCHEMA` is silently ignored until a later query in `solodit.py` breaks or drops fields; recovery is already defined as delete-and-refetch, but nothing at open time says so. **How:** After `conn.executescript(SCHEMA)` in `connect`, compare `PRAGMA table_info` / `PRAGMA index_list` for `solodit_findings`, `github_repos`, and `sync_runs` to the columns and indexes declared in `SCHEMA` (and set `PRAGMA application_id` to a constant next to `SCHEMA`). On mismatch raise a dedicated error and do not `ALTER`.

3. **Value:** Med. **Effort:** S. **What:** One owner for the `sync_runs` resume cursor. **Why it helps the user:** `pages_done`, `next_page`, `status`, `started_at`, `finished_at`, `total_results`, and `message` already encode a resumable fetch, but no symbol owns the transitions, so an interrupted solodit sync can reset the cursor and force a full refetch of a cache that was meant to resume. **How:** Add `sync_start`, `sync_advance`, and `sync_finish` beside `connect`, each an `INSERT`/`UPDATE` on `sync_runs` keyed by `source`. Call them from `colibri_bounty/solodit.py` instead of ad hoc SQL; keep the table disposable (no history, no migration).

## Nice-to-haves

- Set `PRAGMA busy_timeout` in `connect` so a readonly measurement waits out a short refetch lock instead of erroring.
- Add a closing context manager around `connect` — the 3.13 connection CM commits but does not close, so `-wal`/`-shm` sidecars linger next to a disposable cache.
- Add a non-unique index on `solodit_findings(slug)` (and `source_link` if that is the lookup key) the same way impact/protocol/firm/date are already indexed.

- ACCEPT readonly connect (mode=ro URI, skip mkdir+SCHEMA) - VERIFIED: connect() always mkdirs + executescripts; a read of a missing cache is an empty db. One How-detail corrected in triage: tests/test_status.py INSERTS fixture rows, so it needs write mode - the readonly flag serves status/replay readers, not that test.
- ACCEPT schema-shape check failing closed (no ALTER, delete-and-refetch doctrine) - VERIFIED: CREATE TABLE IF NOT EXISTS never alters an existing disposable file; matches the deliberate no-migration design (enforces it, does not reverse it).
- ACCEPT sync_runs cursor owner (sync_start/advance/finish) - VERIFIED: solodit.py scatters INSERT/UPDATE over sync_runs at lines 141-178; columns as described.
- DEFER 3 nice-to-haves (busy_timeout, closing CM [sqlite3 CM commits-not-closes - true], slug index).
