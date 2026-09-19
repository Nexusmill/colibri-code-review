# Colibri review - atlas/graphs/agency_graph.py (bug, lead Phase-3 verification + remediation)

- source: `C:\Users\User\source\repos\fleet\atlas\graphs\agency_graph.py`
- model: claude-opus-5 (in-session lead; the 2026-09-10 fork report under `_external_raw/` is INPUT, not this record)
- sha256 reviewed: `41643a5398b539a30cad6ba8c268f7eaa7d3fac58fa834b5df997e3880ff0b36` (49,922 bytes, CRLF, fleet `6185466`; identical to the bytes the 09-10 fork reviewed - no drift)
- sha256 after remediation: `bc65f5e11bc2fc5aef96cafbb6d61479c66633d6a7c91f145c6776765b473af0`
- date: 2026-09-15
- mode: bug (Phase 3 lead pass over the 2026-09-10 re-audit's claims, then TDD remediation in the same tranche)
- context pack: `get_file_outline` (14 functions, 2 TypedDicts); `get_symbol_source` on `_parse_validation_output`, `validator_node`, `_route_from_handoffs`, `cinematographer_node` (690-894), `editor_node`, and the downstream `atlas/editor_tools.py::merge_video_audio_logic` + `download_if_url`; the Confidence Agent's contract `confidence_agent/prompts.py` (JSON `status` ACCEPTED|REJECTED, passing score > 0.8); `find_importers`/`search_text` for `validation_status` (agency_graph + `gui/agent_runner.py:257` display only); `docs/deferred_manifest.json` (48 FLEET-P0 rows, 4 naming this file), `docs/remediation_manifest.json` (no row for this file), `docs/AGENT_STATE.md` (Phase 3 rewrite pending; Google/Vertex surface retiring); the fork's review/summary/two RED probes.

## Verdict
Two of the fork's three CONFIRMED findings held against the current bytes and are fixed in this tranche; the third (LOW) held and is docketed. One impact claim was **corrected**: the scraped-path defect could not execute arbitrary paths (the editor exists-checks every path before ffmpeg) - its real cost was a lost final cut after paid generation. Both fork refutations (HANDOFF hijack, Director self-loop) re-checked and stand. Retirement test (owner rule, 2026-09-13): the validator parser and the cinematographer scrape are provider-neutral graph logic that spends money today - fixed; the async-blocking call is Phase-3 node-body territory - deferred.

## Deferred rows re-verified PRESENT on these bytes (not re-fixed)
FLEET-P0-DIRECTOR-MODEL (`director_node` binds `sys_model`, never uses it; `create_director_agent(provider=provider)` without `model_name`), FLEET-P0-CHECKPOINTER (`workflow.compile()` bare, no `recursion_limit`), FLEET-P0-HUB-HARD-DEP (import-time `get_or_push_prompt` via the prompts modules - the new `tests/conftest.py` stubs it for tests only), FLEET-P0-REGEX-PATH-SCRAPE (`composer_node`'s two `re.search` sites - amended to name the cinematographer twin, see below).

## Bugs & vulnerabilities (Phase 3 verdicts)

### [HIGH] `_parse_validation_output` fails OPEN in front of paid production - CONFIRMED, FIXED - `line 539-546` (pre-fix)
- What: text fallback `if "ACCEPTED" in upper_con or "APPROVED" in upper_con: status = "APPROVED"` - a bare substring test; JSON branch `status = data.get("status", "REJECTED").upper()` with no whitelist.
- Trigger (traced): `validator_node` line 621 routes ONLY `status == "REJECTED"` back to the Director; every other string proceeds to `_get_production_target()` = cinematographer/composer. So "NOT APPROVED", "cannot be approved", "unapproved", "disapproved" (all contain APPROVED), and any off-contract JSON status ("NEEDS_REVISION") reach production. The fallback branch is exactly the case the JSON mandate was disobeyed.
- Impact: real Replicate/Vertex spend on a rejected plan, and the revision loop (`max_revisions`) skipped.
- Fix applied (fail-closed): approval iff JSON status in {ACCEPTED, APPROVED}; malformed JSON / off-contract status / no JSON -> REJECTED + warning; prose heuristic removed. Chosen over the fork's negation-regex because negation is whack-a-mole ("unapproved"/"disapproved" already slipped its pattern) and the money gate must not depend on English.
- Tests: `tests/test_validator_verdict_parsing.py` - 17 cases (7 RED before the fix, 8 contract pins, 2 routing cases driving `validator_node` with a stubbed Confidence Agent: prose -> `goto="director"`, JSON ACCEPTED -> `goto="cinematographer"`).
- Manifest: remediation `FLEET-VALIDATOR-FAIL-OPEN`.

### [MEDIUM] `cinematographer_node` accepts text-scraped paths unchecked - CONFIRMED, IMPACT CORRECTED, FIXED - `line 796-805` (multi-clip), `847-870` (single-clip + raw fallback), pre-fix
- What: `re.findall` path matches appended to `video_assets` with no existence check (the `source_mode == "file"` branch at 707 does check); single-clip fallback `if "Artifacts" in result or "C:" in result or "http" in result: assets = [result]` stores the whole prose as one "path".
- Fork claim "handed to ffmpeg on those paths" - **refuted as stated**: `merge_video_audio_logic` step 1 (`editor_tools.py`) returns `Error: File not found` on the first missing path, before any ffmpeg call. **Corrected impact**: one hallucinated/quoted path - or the prose itself via the fallback - poisons `video_assets` and the editor refuses the WHOLE merge; the paid clips are lost from the final cut. URL matches additionally trigger `download_if_url` (an unauthenticated fetch of a model-emitted URL) - noted, not changed here; the editor's exists check still bounds it.
- Fix applied: `os.path.exists` gate at both scrape sites (mirrors the file branch); the raw fallback accepts `result.strip()` only if it exists (its legitimate purpose: a bare path with spaces the regex cannot span); dropped matches are logged. URLs unchanged.
- Tests: `tests/test_cinematographer_asset_scrape.py` - 5 cases (4 RED before the fix; URL pass-through pinned). The RED run also exposed a latent pre-fix defect: a bare path WITH SPACES was truncated at the first space by the regex and stored truncated (the fallback never ran because `assets` was non-empty) - the exists gate + fallback now return the full path.
- Manifest: remediation `FLEET-CINE-SCRAPED-PATHS-UNCHECKED`; deferred `FLEET-P0-REGEX-PATH-SCRAPE` amended (cinematographer site mitigated; composer's two sites still text-scraped; structured returns cover all four).

### [LOW] `researcher_node` blocks the event loop - CONFIRMED (static), DEFERRED - `line 492`
`async def researcher_node` calls the synchronous, network-bound `def run_research_task` with no `await`/`to_thread`. Not fixed here: `run_research_task`'s thread-safety (module-level `AgentComms`/psycopg2) is unverified and Phase 3 rewrites the node bodies. Deferred `FLEET-P0-RESEARCHER-NODE-BLOCKS-LOOP`.

## Observation docketed (design, owner ruling)
`validator_node` never consults `validation_score` against the rubric's passing threshold (> 0.8), and after `max_revisions` it logs "Forcing proceed" and sends a REJECTED plan to paid production. Deferred `FLEET-P0-VALIDATOR-SCORE-AND-FORCED-PROCEED` - a spend-policy question, not a parser defect.

## Adversarial pass - refutations that stand (re-checked)
- HANDOFF hijack via tool content: the only `HANDOFF:` constructors are the seven `inter_agent_comms.py` wrappers with the target hard-coded at position 0; `re.search` is leftmost-first. Stands.
- Director self-loop via `"director" in targets`: `DIRECTOR_TOOLS` has no `delegate_to_director`; the branch is reachable only from deterministic literal tuples in the production nodes. Stands (the backstop gap is FLEET-P0-CHECKPOINTER's missing `recursion_limit`).

## Missing safeguards (unchanged, acknowledged Phase 3)
No step cap, no checkpointer, no spend ledger; every provider call reachable from this graph is uncapped and unlogged (FLEET-P0-NO-SPEND-LEDGER / CHECKPOINTER). The two fixes above close the two code-visible fail-open paths INTO that uncapped production, they do not cap it.

## Test infrastructure added (same commit)
`tests/conftest.py`: the atlas package could not be imported in tests without a provider key (import-time Google embedder) and a LangSmith workspace (import-time Hub pull) - Phase 0 recorded 2 collection errors. The conftest scrubs every provider/tracing variable, gives the embedder a placeholder value (construction only checks presence), and binds `hub_manager.get_or_push_prompt` to the local default before any prompts module imports. Result: the 3 carried tests went from 2 collection errors to 15 passed; suite now 35 passed under `deepagents-quickstarts\.venv` (Python 3.13.7), no network.

## Files
- `atlas/graphs/agency_graph.py` (37+/15-), `tests/conftest.py` (new), `tests/test_validator_verdict_parsing.py` (new), `tests/test_cinematographer_asset_scrape.py` (new), `docs/remediation_manifest.json` (+2 rows, +1 source), `docs/deferred_manifest.json` (1 amended, +2 rows), this record + `_external_raw/atlas__graphs__agency_graph.py__fork-2026-09-10.md` (the fork's raw report, input evidence).
