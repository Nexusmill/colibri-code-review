# Colibri review - atlas/agent_factory_legacy.py (bug, lead Phase-3 verification of the 2026-09-10 fork; DOCKET disposition)

- source: `C:\Users\User\source\repos\fleet\atlas\agent_factory_legacy.py`
- model: claude-opus-5 (in-session lead; the 2026-09-10 fork report `_external_raw/atlas__agent_factory_legacy.py__fork-2026-09-10.md` is INPUT)
- sha256 reviewed: `8b28eadb79dbb5f68512e06f07a22665426b16aa6fef9d709070b5d59085b787` (identical to the bytes the fork reviewed on 2026-09-10 - every fork line citation still holds)
- date: 2026-09-15
- mode: bug (Phase 3 lead pass; retirement test applied - fix now only if the defect costs data/money/secrets or blocks the pipeline BEFORE the code retires or is rewritten in Phase 3; otherwise docket with the call recorded)
- context pack: `get_file_outline` (10 symbols); `get_symbol_source` create_deep_agent.agent_node (258-281); `find_importers`: only `atlas/agent_factory.py`, which routes to it for Replicate-routed chat models (line 85) and as the fallback when the prebuilt ReAct agent fails to build (line 105); rows: FLEET-P0-TRANSITIONAL-MODULES; fork probe re-run today: RED (2 FAIL).

## Verdict
Both findings hold: the legacy factory launders a model 'validation error' into a plain `AIMessage` that `should_continue` then treats as the final answer (line 270-280), and `bind_tools()` failure falls back to a tool-less model silently (line 241). The module is TRANSITIONAL and the Phase 3 provider factory replaces both code paths - docketed, not fixed.

## Bugs & vulnerabilities (Phase 3 verdicts)

### [HIGH] `agent_node` returns a 'System Error: Tool Binding Failed' AIMessage as the agent's answer - CONFIRMED (probe RED), DOCKETED - `line 270-280`
- Trigger: any exception whose text contains 'validation error' (the Gemini `GenerateContentRequest` schema failures the comment anticipates). Impact: the graph ENDS with an error string in the assistant slot; a caller that saves or acts on the last message treats a failure as output.
### [MEDIUM] `create_deep_agent` swallows `bind_tools()` failure and continues tool-less - CONFIRMED (probe RED), DOCKETED - `line 241`
- Disposition (both): deferred row `FLEET-P0-LEGACY-FACTORY-ERROR-LAUNDERING`.

## Adversarial pass
- Reachability: `atlas/agent_factory.py` calls this factory for every Replicate-routed chat model (line 85) and as the fallback when the prebuilt ReAct agent fails to build (line 105) - so the laundering IS on a reachable path in today's GUI - but the retirement test still says docket: the factory is the first Phase 3 deliverable and the fix there is 'raise', not a patch to code being deleted.
