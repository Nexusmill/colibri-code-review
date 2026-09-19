# Colibri review - atlas/CommercialAgents/confidence_agent/agent.py (bug, lead Phase-3 verification of the 2026-09-10 fork; DOCKET disposition)

- source: `C:\Users\User\source\repos\fleet\atlas\CommercialAgents\confidence_agent\agent.py`
- model: claude-opus-5 (in-session lead; the 2026-09-10 fork report `_external_raw/atlas__CommercialAgents__confidence_agent__agent.py__fork-2026-09-10.md` is INPUT)
- sha256 reviewed: `91b062679078d45254f64bf66ef76d0ed2e18eb0b16e364cbaade204f831db11` (identical to the bytes the fork reviewed on 2026-09-10 - every fork line citation still holds)
- date: 2026-09-15
- mode: bug (Phase 3 lead pass; retirement test applied - fix now only if the defect costs data/money/secrets or blocks the pipeline BEFORE the code retires or is rewritten in Phase 3; otherwise docket with the call recorded)
- context pack: `get_file_outline` (5 symbols); `get_symbol_source` run_confidence_audit (lines 123-234, read in full); `search_text` for callers: run_confidence_audit is called from `atlas/gui/agent_runner.py:598` (the GUI confidence path) and `__main__`; `find_importers` 3 (research tools, agency_graph, agent_runner); deferred rows naming this file: FLEET-P0-DIRECTOR-MODEL twin, FLEET-P0-RESEARCH-CONFIDENCE-RECURSION, FLEET-P0-DEGOOGLE-PATHS-UMBRELLA; fork probe re-run today: RED (1 of 4 checks).

## Verdict
The fork's MEDIUM holds on current bytes: `run_confidence_audit` builds a SECOND, fresh `ChatGoogleGenerativeAI(model="gemini-2.0-flash-001", vertexai=True)` (line 182) after the audit agent's own call(s), gated only by `if final_report:` - no cap, no ledger row, no price, purely to reformat the report as a Markdown table. Reachable from the GUI (`agent_runner.py:598`). NOT fixed: it is a hard Vertex Gemini path that retires under FLEET-P0-DEGOOGLE-PATHS-UMBRELLA, nothing runs the fleet until Damien picks OpenRouter models (no spend today), and any replacement dashboard call must go through the Phase 3 spend ledger + cap rather than a per-call guard patched into retiring code.

## Bugs & vulnerabilities (Phase 3 verdicts)

### [MEDIUM] second uncapped LLM call per successful audit ('Argus Fact Dashboard') - CONFIRMED (probe RED today), DOCKETED - `line 182`
- What: `dash_llm = ChatGoogleGenerativeAI(...)`; `dash_llm.invoke(dash_prompt)` inside `if final_report:`; failure only logs a warning.
- Trigger: any audit that produces a report. Impact: a doubled, unaccounted paid call per audit once Google credentials exist; a reader of the FLEET-P0-* rows would not know to look for it.
- Disposition: deferred row `FLEET-P0-CONFIDENCE-DASHBOARD-SECOND-CALL` (retirement test: no cost before Phase 3 - Google unused; the path is deleted by the de-Google).

## Adversarial pass
- Re-checked the deferred rows the fork re-verified: `create_confidence_agent` default `provider="Google"` / `gemini-2.0-flash-001` (line 57, the DIRECTOR-MODEL twin) and `consult_research_agent` (lines 45-54, RESEARCH-CONFIDENCE-RECURSION) are present and already docketed - not re-flagged.
- The `save_text_document(subdir="Audits")` call passes a literal - the unit-4 `subdir` note stands, no new exposure.
