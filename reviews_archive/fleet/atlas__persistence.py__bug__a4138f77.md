# Colibri review - atlas/persistence.py (bug, lead Phase-3 verification of the 2026-09-10 fork; DOCKET disposition)

- source: `C:\Users\User\source\repos\fleet\atlas\persistence.py`
- model: claude-opus-5 (in-session lead; the 2026-09-10 fork report `_external_raw/group__grouped_small__fork-2026-09-10.md` is INPUT)
- sha256 reviewed: `a4138f77ebfc8ce880055ee4d9c5efc137fe1fa129afe0e4cb31bf5bd09280e0` (identical to the bytes the fork reviewed on 2026-09-10 - every fork line citation still holds)
- date: 2026-09-15
- mode: bug (Phase 3 lead pass; retirement test applied - fix now only if the defect costs data/money/secrets or blocks the pipeline BEFORE the code retires or is rewritten in Phase 3; otherwise docket with the call recorded)
- context pack: `get_symbol_source` get_connection_string (21-29); `find_importers`: agent_runner (get_postgres_checkpointer, used by stream_director); remediation row FLEET-P0-PG-PASSWORD-FALLBACK made the password env-only at carry; fork: 1 LOW PLAUSIBLE (grouped record review_fleet_grouped_small.md).

## Verdict
CONFIRMED by reading the bytes (the fork left it PLAUSIBLE): with `POSTGRES_PASSWORD` unset, `get_connection_string` interpolates the literal string `None` into the DSN (`postgresql://postgres:None@...`) instead of raising - the checkpointer then fails authentication with a misleading error. No data/money/secret cost (Postgres is optional; unit 3 removed the one gratuitous dependency). Docketed as `FLEET-P0-PERSISTENCE-DSN-NONE-PASSWORD` for the Phase 3 'wire the checkpointer' item (raise a clear error when the password is unset and Postgres is requested).
