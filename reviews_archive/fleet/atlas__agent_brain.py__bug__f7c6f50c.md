# Colibri review - atlas/agent_brain.py (bug, lead Phase-3 verification of the 2026-09-10 fork; DOCKET disposition)

- source: `C:\Users\User\source\repos\fleet\atlas\agent_brain.py`
- model: claude-opus-5 (in-session lead; the 2026-09-10 fork report `_external_raw/atlas__agent_brain.py__fork-2026-09-10.md` is INPUT)
- sha256 reviewed: `f7c6f50c074228349efe07348d98ba54bf9d528b0843877d11159ac1255a8626` (identical to the bytes the fork reviewed on 2026-09-10 - every fork line citation still holds)
- date: 2026-09-15
- mode: bug (Phase 3 lead pass; retirement test applied - fix now only if the defect costs data/money/secrets or blocks the pipeline BEFORE the code retires or is rewritten in Phase 3; otherwise docket with the call recorded)
- context pack: `get_file_outline` (21 symbols); `get_symbol_source` AgentComms.get_all_recent_messages (299-342) + AgentMemory.memorize (83-111); `search_text` callers: get_all_recent_messages has ONE caller, `atlas/roundtable_facilitator.py:89` passing `limit=100, since=since`; `find_importers` 8 (every CommercialAgent, agency_graph, agent_runner, roundtable_facilitator); rows: FLEET-P0-TRANSITIONAL-MODULES (this module retires), FLEET-P0-IMPORT-TIME-EMBEDDER; fork probes re-run today: RED (2 FAIL + 1 FAIL).

## Verdict
Both fork findings hold on current bytes, neither costs anything before the module retires (FLEET-P0-TRANSITIONAL-MODULES: agent_brain.py goes with the repo-memory borrowings). Docketed with the exact semantics recorded so the rewrite does not re-derive them.

## Bugs & vulnerabilities (Phase 3 verdicts)

### [HIGH -> LOW in context] `get_all_recent_messages` orders `timestamp ASC` under `LIMIT` in BOTH branches - CONFIRMED (probe RED: ids 1..50 returned for 'latest 50'), DOCKETED - `line 315-324`
- What: the docstring says "Get latest messages"; with `since=None` the query returns the OLDEST `limit` rows ever written; with `since=` it returns the oldest `limit` rows after the cut-off (a session window read forward).
- Call-site reality (why the severity drops): the only caller (`roundtable_facilitator.py:89`) passes `since=` = the session start and `limit=100`, so it reads a session forward in order - the semantics the facilitator wants. The docstring is what is wrong today; the `since=None` branch is a latent trap for any dashboard caller.
- Disposition: deferred row `FLEET-P0-AGENT-BRAIN-RECENT-MESSAGES-ORDER`.

### [MEDIUM] `memorize` computes the embedding OUTSIDE its try - CONFIRMED (probe RED: RuntimeError escaped), DOCKETED - `line 92`
- What: `vec = EMBEDDER.embed_query(text)` runs before the `try:` that guards `table.add`; an embedder outage raises out of `memorize` while `recall` swallows the same class. Every CommercialAgent calls `memorize` at the end of a task (e.g. the tail of `run_confidence_audit`) unguarded.
- Disposition: deferred row `FLEET-P0-AGENT-BRAIN-MEMORIZE-EMBED-RAISES` (the Google embedder is itself retiring: FLEET-P0-IMPORT-TIME-EMBEDDER / DEGOOGLE umbrella).

## Adversarial pass
- Tried to refute the ORDER finding via the caller: with `since=` the forward read is correct for a session window, so the practical defect is the docstring plus the unused default branch - recorded as such, not as a live HIGH.
