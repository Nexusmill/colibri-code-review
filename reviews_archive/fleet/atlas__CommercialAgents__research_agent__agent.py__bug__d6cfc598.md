# Colibri review - atlas/CommercialAgents/research_agent/agent.py (bug, lead Phase-3 verification of the 2026-09-10 fork; DOCKET disposition)

- source: `C:\Users\User\source\repos\fleet\atlas\CommercialAgents\research_agent\agent.py`
- model: claude-opus-5 (in-session lead; the 2026-09-10 fork report `_external_raw/atlas__CommercialAgents__research_agent__agent.py__fork-2026-09-10.md` is INPUT)
- sha256 reviewed: `d6cfc598888037a43d01a5662dce884ad378373b35aa5e65208054dd6b3e1765` (identical to the bytes the fork reviewed on 2026-09-10 - every fork line citation still holds)
- date: 2026-09-15
- mode: bug (Phase 3 lead pass; retirement test applied - fix now only if the defect costs data/money/secrets or blocks the pipeline BEFORE the code retires or is rewritten in Phase 3; otherwise docket with the call recorded)
- context pack: fork probe re-run today: RED (`agent_tools` = scrape_webpage, arxiv_search, submit_finding_for_review - no `tavily_search`, while the system prompt instructs its use); existing rows re-verified by the fork: FLEET-P0-DIRECTOR-MODEL twin (line 42), FLEET-P0-RESEARCH-RECURSION-LIMIT-DEAD; the prompt itself lives in prompts.py + the Hub.

## Verdict
Fork MEDIUM holds: the system prompt documents a `tavily_search` tool that is never bound (`agent_tools`, line ~90) - the model is told to call a tool it does not have and will either hallucinate a call or fall back to `scrape_webpage` on a guessed URL (the SSRF surface unit 2 guarded). Same disposition as the Director prompt: the runtime prompt is the Hub copy; the Phase 3 research-agent rebuild (Tavily/Exa search per the packet) decides bind-or-remove. Docketed under `FLEET-P0-PROMPTS-NAME-UNBOUND-TOOLS`. The fork's PLAUSIBLE about `save_text_document` public-visibility defaults belongs to asset_manager.py (unit 4 recorded the URL/GCS branch as a Phase 3 provider-adapter item).
