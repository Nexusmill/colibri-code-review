# Post-gate audit — per-file sweeps, tranches 2-4 (2026-09-02) — PENDING remediation

24 reviews of jcodemunch-mcp + deepagents-quickstarts cores, run as background external
reviews (~30% GLM-5.3-flash / ~70% Grok, the standing cadence). Raw outputs preserved under
each repo's `.colibri_reviews/_external_raw/` (19 jcm, 5 deepagents). **NONE Phase-3 gated or
remediated yet** — that is the next tranche (colibri-review law 3: verify each finding against
current bytes before docketing/fixing; refuted ones → verified-stale, never re-fixed).

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
