# Colibri review - atlas/CommercialAgents/director_agent/prompts.py (bug, lead Phase-3 verification of the 2026-09-10 fork; DOCKET disposition)

- source: `C:\Users\User\source\repos\fleet\atlas\CommercialAgents\director_agent\prompts.py`
- model: claude-opus-5 (in-session lead; the 2026-09-10 fork report `_external_raw/atlas__CommercialAgents__director_agent__prompts.py__fork-2026-09-10.md` is INPUT)
- sha256 reviewed: `96d52fdd691f31ebd0d689470879e7b1662882a836945761d4c64c24fa139d42` (identical to the bytes the fork reviewed on 2026-09-10 - every fork line citation still holds)
- date: 2026-09-15
- mode: bug (Phase 3 lead pass; retirement test applied - fix now only if the defect costs data/money/secrets or blocks the pipeline BEFORE the code retires or is rewritten in Phase 3; otherwise docket with the call recorded)
- context pack: fork probe re-run today: RED (`DIRECTOR_TOOLS` = discover_agents, delegate_to_researcher/confidence/composer/cinematographer/editor, signal_task_complete - never assemble_final_cut); the runtime prompt is pulled from the LangSmith Hub (FLEET-P0-HUB-HARD-DEP) - this file is the local default only.

## Verdict
Fork LOW holds: the prompt tells the Director to call `assemble_final_cut`, which `agent.py` defines but never binds (`DIRECTOR_TOOLS`). Two facts make this a docket item, not a code fix: (1) the prompt the model actually sees comes from the LangSmith Hub at runtime - editing this local default changes nothing until Phase 3 makes prompts in-repo (FLEET-P0-HUB-HARD-DEP); (2) whether the tool should be bound or the sentence removed is a design call for the Director rewrite. Docketed with the research-prompt twin under `FLEET-P0-PROMPTS-NAME-UNBOUND-TOOLS` (owner item: the Hub copy).
