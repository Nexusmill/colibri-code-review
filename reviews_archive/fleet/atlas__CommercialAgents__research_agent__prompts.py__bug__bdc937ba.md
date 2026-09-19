# Colibri review - atlas/CommercialAgents/research_agent/prompts.py (bug, lead Phase-3 verification of the 2026-09-10 fork; DOCKET disposition)

- source: `C:\Users\User\source\repos\fleet\atlas\CommercialAgents\research_agent\prompts.py`
- model: claude-opus-5 (in-session lead; the 2026-09-10 fork report `_external_raw/atlas__CommercialAgents__research_agent__prompts.py__fork-2026-09-10.md` is INPUT)
- sha256 reviewed: `bdc937ba5df2c943eda9f441e8c2aede5f8a6004cda240183f167300a5e1425b` (identical to the bytes the fork reviewed on 2026-09-10 - every fork line citation still holds)
- date: 2026-09-15
- mode: bug (Phase 3 lead pass; retirement test applied - fix now only if the defect costs data/money/secrets or blocks the pipeline BEFORE the code retires or is rewritten in Phase 3; otherwise docket with the call recorded)
- context pack: reviewed with research_agent/agent.py (the fork grouped them); the tavily sentence is at line 26.

## Verdict
The local default prompt names `tavily_search` (line 26); the bound tool list does not include it. See the agent.py record; `FLEET-P0-PROMPTS-NAME-UNBOUND-TOOLS`.
