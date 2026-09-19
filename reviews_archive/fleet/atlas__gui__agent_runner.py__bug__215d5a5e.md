# Colibri review - atlas/gui/agent_runner.py (bug, lead Phase-3 verification + remediation)

- source: `C:\Users\User\source\repos\fleet\atlas\gui\agent_runner.py`
- model: claude-opus-5 (in-session lead; the 2026-09-10 fork report under `_external_raw/` is INPUT)
- sha256 reviewed: `215d5a5e405d953bb560617d81bd0ad1f08af27cfada4842519dec7b5fcc7e4d` (784 lines, CRLF; identical to the bytes the fork reviewed)
- sha256 after remediation: `cbf637e87d17ade442acea47584a43880494da5e4bf0052fb61ae8297a61607d`
- date: 2026-09-15
- mode: bug (Phase 3 lead pass over the 2026-09-10 re-audit's claims, then TDD remediation in the same tranche)
- context pack: `stream_agency_graph` (48-332) read in full incl. `poll_agent_comms`, `run_loop`, the sync-to-async bridge; `_run_agent_async` (334-344, a `pass`-bodied dead helper) and `stream_director` (346+, which DOES pass the checkpointer into `create_director_agent`) to confirm the import stays live; `search_text` for every `get_postgres_checkpointer` use (3 in this file, the def in `atlas/persistence.py`, a commented-out one in `roundtable_facilitator.py`); `find_importers` -> only `tests/test_agent_runner_cinematographer.py`; `docs/AGENT_STATE.md` ("LangSmith / Postgres are OPTIONAL for the fleet by design"); deferred rows FLEET-P0-CHECKPOINTER (wire a checkpointer into `compile()`, Phase 3) and FLEET-P0-RUNNER-POLL-THREAD-LEAK; the fork's review + RED probe.

## Verdict
The fork's HIGH held exactly: the Studio Graph run - the fleet's stated first end-to-end goal - was wrapped in a Postgres checkpointer acquisition it never used, so it could not run on any machine without a reachable Postgres while the repo's own doctrine calls Postgres optional. Fixed by removing the dead acquisition (structural dedent, no logic change). The fork's refutation (`run_editor_merge` KeyError) re-checked and stands; its PLAUSIBLE LOW is the existing deferred FLEET-P0-RUNNER-POLL-THREAD-LEAK, not a new finding. Retirement test: the runner is rebuilt in Phase 3, but this blocks the pipeline today on the owner's workstation - fix.

## Bugs & vulnerabilities (Phase 3 verdicts)

### [HIGH] `stream_agency_graph` requires a live Postgres for a checkpointer it never uses - CONFIRMED, FIXED - `line 121-131` (pre-fix)
- What: `async with get_postgres_checkpointer() as checkpointer:` wrapped the whole `run_loop`; the bound name appears nowhere else in the function - `studio_graph.astream({...}, config=config)` takes no checkpointer, and `studio_graph` is `agency_graph.app`, compiled without one (FLEET-P0-CHECKPOINTER). The carried comments inside the block said as much ("For now, we run it as is").
- Trigger (traced): `get_postgres_checkpointer` (`persistence.py:33`) opens an `AsyncConnectionPool` on entry; with no server (or, since FLEET-P0-PG-PASSWORD-FALLBACK, no `POSTGRES_PASSWORD`) `__aenter__` raises; `run_loop`'s `except Exception` turns that into a `("System", "error", "Graph Error: ...")` event and the Director never runs. Reproduced RED on the pre-fix bytes: `tests/test_agent_runner_studio_graph_no_postgres.py` - graph called 0 times, one System error event.
- Impact: the GUI pipeline is unusable without Postgres, contradicting `docs/AGENT_STATE.md`; a connection attempt with a timeout also delays every run when the server is merely slow.
- Fix applied: the `async with` and its nine explanatory comment lines removed; the 140-line body dedented one level (verified with `git diff -w`: the only non-whitespace change is the removed block and a six-line replacement comment). `from atlas.persistence import get_postgres_checkpointer` stays - `stream_director` uses it for real (`create_director_agent(..., checkpointer=checkpointer)`), as does the dead `_run_agent_async`.
- Tests: 2 cases (both RED before): with Postgres unreachable the stubbed graph runs once and its Director output reaches the event stream with no System error; the GUI `agency_config` still lands in the graph's `configurable` (thread id, cinematographer/composer keys). Suite 53 passed.
- Manifest: remediation `FLEET-RUNNER-POSTGRES-GATE`.

### [LOW, PLAUSIBLE per the fork] non-daemon worker threads never joined on an abandoned generator - EXISTING DEFERRED ROW
FLEET-P0-RUNNER-POLL-THREAD-LEAK (deferred 2026-09-08, gate A2 r5) already records the abandoned-generator case (`GeneratorExit` at `yield item` skips `stop_polling.set()`); the fork's observation is the same mechanism seen from the `start_loop` thread. Re-verified present, not re-docketed.

## Adversarial pass - refutation that stands (re-checked)
`run_editor_merge`'s `a["asset_type"]` over `list_assets()` results: every `.json` sidecar writer in `atlas/asset_manager.py` that `list_assets()` reads writes `asset_type`; `save_text_document` writes no sidecar. No current path yields a sidecar without the key. Stands.

## Observation (no action)
`_run_agent_async` (334-344) is a dead helper: it acquires the checkpointer and does nothing (`pass`). Left in place - pre-existing dead code, not this unit's finding; it disappears with the Phase 3 runner rewrite.

## Files
- `atlas/gui/agent_runner.py` (136+/141-, all but 6 lines re-indentation), `tests/test_agent_runner_studio_graph_no_postgres.py` (new), `docs/remediation_manifest.json` (+1 row, +1 source), this record + `_external_raw/atlas__gui__agent_runner.py__fork-2026-09-10.md`.
