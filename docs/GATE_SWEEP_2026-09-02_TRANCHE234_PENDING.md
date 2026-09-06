# Post-gate audit — per-file sweeps, tranches 2-4 (2026-09-02) — PENDING remediation

24 reviews of jcodemunch-mcp + deepagents-quickstarts cores, run as background external
reviews (~30% GLM-5.3-flash / ~70% Grok, the standing cadence). Raw outputs preserved under
each repo's `.colibri_reviews/_external_raw/` (19 jcm, 5 deepagents).

**STATUS 2026-09-05 — ALL 24 PHASE-3 GATED (in-session, claude-fable-5-1), NOT YET REMEDIATED.**
Gated records + manifests committed and notarized: jcodemunch-mcp `e6d8eb0` (19 records,
gate BLOCK 220745 → CLEAR 220915) and deepagents-quickstarts `407cab3` (5 records, gate BLOCK
220638 → CLEAR 220944); both BLOCKs were the reviewer-scope false positive (EV-036, third
occurrence of the EV-027 class). All 24 files were byte-identical to the raws at dispatch.
Kept after tracing: **8 HIGH** — jcm (5): `sqlite_store.load_index` torn cold load cached as
fresh; `index_folder` no-change runs write the BRANCH head into the BASE index (worse than
reported); `plan_refactoring` TS overload rename swallows the implementation line (corrupts the
file); `search_symbols` narrowing drops identity matches; `deletion_safety` classes entry-point
files dead. deepagents (3): `agency_graph.composer_node` unbound `audio_path`/`result` +
duplicate asset; `agent_runner.run_cinematographer` runs the paid generation TWICE;
`schema_service` file-keyword heuristic misrenders its own first-party schemas. Plus ~16 MEDIUM
(config `_strip_jsonc` comma corruption probe-confirmed on 2 of the 4 claimed shapes; project
`trusted_folders` absolute entries; sqlite unchunked `IN` lists; Rust `use` dedup; index_repo
silent fetch-failure symbol deletion; token_tracker first-path binding with a live mixed caller
(winnow_symbols); security.py project overrides inert for two keys; `cli/init.py` rewriting an
invalid client config — downgraded from HIGH because a `.bak` is written; plan_refactoring's
unguarded `repo.split`; deletion_safety's cluster override + unchecked text-sweep error;
composer lyrics sent as ACE-Step tags; app.py gs:// regex + console link + Stop (plausible);
…) and ~30 LOW. **Refuted with line evidence (never re-fix): 18 external claims** — the
`search_ast` `child.text` HIGH plus its two MEDIUMs (the other HIGH narrowed to a LOW), the
`_call_graph` HIGH (`_symbol_index` always built) and its depth-0 MEDIUM (callers clamp), both
`check_delete_safe` findings (`scip_reference_files` cannot raise), the two `should_exclude_file`
findings (NO caller in src — dead code) plus the string half of the secret-pattern finding,
`index_folder`'s parser-upgrade MEDIUM + coverage LOW (deliberate), watcher's crash/leak claims
(WatcherManager restarts; IndexStore holds no handle), get_blast_radius's private-access +
cross-repo-except findings (style/design), audit_agent_config's partial-load LOW, app.py's
CRITICAL import (resolves via sys.path + `__init__` files) and its non-3-tuple event. One
external FIX was itself wrong: the Haskell node is `type_synomym` (grammar probe), not
`type_synonym`.
Per-file verdicts: each repo's `.colibri_reviews/<path>__bug__<sha8>.md`. Next: remediation
tranches, worst-first, TDD, own gated commits.

Original triage below is kept verbatim as the pre-gate record (colibri-review law 3: verify each
finding against current bytes before docketing/fixing; refuted ones → verified-stale, never
re-fixed).

Triaged apparent findings (from the raw reviews — UNVERIFIED, verify before acting):

**jcodemunch-mcp (phantom-man/jcodemunch-mcp):**
- `storage/sqlite_store.py` (grok-4.6): HIGH — `load_index` torn snapshot + cache poison under concurrent write (no BEGIN read-txn; caches torn CodeIndex under new mtime). Fix: wrap the 3 reads in one BEGIN, re-stat after.
- `config.py` (GLM): MEDIUM — `_strip_jsonc` strips required commas adjacent to comments → valid JSONC unparseable → whole user config silently reverts to DEFAULTS.
- `tools/search_symbols.py` (GLM): HIGH — inverted-index candidate narrowing drops identity-channel (prefix/segment) matches before scoring.
- `tools/index_folder.py` (grok): 2 HIGH — branch-delta vs base-index save divergence on git-head-advance / mtime-only paths (stale branch symbols).
- `tools/plan_refactoring.py` (grok): HIGH `repo.split("/",1)` unpack ValueError on malformed repo; HIGH TS-overload collection corrupts the real definition.
- `storage/token_tracker.py` (grok): HIGH `_ensure_loaded` binds first base_path only → later stores mix/lose savings.
- `watcher.py` (grok): MEDIUM `relative_to` ValueError kills the watch task (symlink/WSL events); MEDIUM awatch exception escapes uncaught.
- `parser/languages.py`, `parser/imports.py`, `storage/index_store.py`, `tools/search_ast.py`, `security.py`, `cli/init.py`, `tools/audit_agent_config.py`, `investigator/deletion_safety.py`, `tools/check_delete_safe.py`, `tools/_call_graph.py`, `tools/index_repo.py`, `tools/get_blast_radius.py` — see raws; mix of MEDIUM/LOW (several terse/clean).

**deepagents-quickstarts (Nexusmill/deepagents-quickstarts):**
- `services/schema_service.py` (GLM): HIGH — `_infer_control_type` file-keyword heuristic misclassifies non-string params (a boolean `generate_audio` → audio file picker; `number_of_images` int → image upload) for first-party models.
- `graphs/agency_graph.py` (grok): HIGH — `composer_node` UnboundLocalError on `result`/`audio_path` + duplicate assets append.
- `CommercialAgents/composer_agent/agent.py` (grok): MEDIUM — ACE-Step tags fallback emits full input_text (lyrics) as tags; LOW temp-file leak on validation failure.
- `gui/app.py`, `gui/agent_runner.py` — see raws.

**Cross-cutting (recurs across jcm):** unguarded `relative_to`/`split` on external input; first-call path/config binding that later calls can't change; missing read-transaction around multi-statement SQLite reads.

Remediation cadence ([[colibri-review-run-cadence]] memory): gate each finding in-session, commit
the gated reviews per repo, fix confirmed defects immediately after (TDD, own gated commit),
refuted → verified-stale. jcm is a large fork (257 py files) — this is an ongoing multi-session
campaign; the biggest un-swept files (server.py 517KB, extractor.py 443KB) still need a chunked
review lane.
