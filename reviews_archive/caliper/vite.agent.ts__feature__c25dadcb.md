# Colibri review — vite.agent.ts (feature)

- **Source:** `vite.agent.ts` · **sha256:** c25dadcb
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** the optimizer agent's server: tools contract from src/llm/tools.ts (FLAG_ALLOWLIST, no-op filter), one transport over every brain (local sidecar OpenAI-compatible or cloud via openRouterChat with free-tier 429 fallback), systemSnapshot/currentState (live server argv truth), describeProposal, the human-clicked apply, and the proactive analyze task; FEATURES.md `optimizer-*`; last touch c9bb3bb (2026-09-05).

## What this module does

The model-proposes/human-applies loop: read_kb executes inline with citations; benches refuse during the opening analysis and run as real measured renders when explicitly asked; set_flag/set_param return as plain-English PROPOSALS; apply re-validates from the allowlist, refuses no-ops BEFORE writing, serializes behind one chain, and reports the live-server truth (restart note / already-active). Every answer carries brain/model/tokens and — for OpenRouter — true cost. The no-op filter owns every exit path, and a small model narrating instead of proposing gets one demanded re-emit.

## Suggested add-ons

**Proposal diff in the card (current → new)** — Value Med · Effort S
- What: `describeProposal` (lines 31-44) prints only the TARGET value ("Set launch flag --x 8"); include the CURRENT value in the card ("now 4 → 8").
- Why: the human click is the write gate, and its card omits the one fact that makes the change legible — what it changes FROM. `currentState()` already fetches exactly this for the no-op filter; the data is one scope away.
- How: describeProposal gains an optional current-state param, threaded from the chat loop's `currentState()` call.

**An applied-proposals ledger** — Value Med · Effort S
- What: append every applied proposal (ts, tool call, prior value, result line) to a gitignored ledger file — or the knowledge store as a measured-results class entry.
- Why: the optimizer's premise is measured tuning over time, yet applies leave no record beyond the changed config value itself; "what did the optimizer change and when did it change it" is unanswerable after the console closes. The KB append machinery (`appendMeasured`) is already imported here for benches.
- How: one append inside `applyProposal` after each successful write.

**UNDO on an applied proposal** — Value Med · Effort S-M
- What: the console's applied row gains UNDO restoring the prior value through the same validated apply path (the ledger's prior-value field from the add-on above makes it one click).
- Why: proposals are small reversible writes (a flag number, a bundle default); today a wrong apply is corrected by finding the old value by hand — the card that wrote it should be the card that unwrites it. Stays inside the human-clicks-only doctrine (undo is also a human click).

## Nice-to-haves

- The bench-during-analysis refusal keys on the user message starting with "SYSTEM SNAPSHOT:" — a magic-prefix contract between vite.agent and the console; a structured flag would be sturdier (note; bug-mode owns the detail).
