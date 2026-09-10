# Colibri spec review — vite.agent.ts

- Source: E:\AI\Caliper\vite.agent.ts (391 lines)
- Registry: E:\AI\Caliper\spec\optimizer.json (5 controls, all PROVISIONAL)
- Reviewer: ZCode fresh-context subagent
- SHA-256: 663172ab8c6e2b84e496768dc9a570c91435f71734368c2b29fee6bf2d04d263 (matches the 2026-08-25 bug review's sha — file unchanged since; this is the first SPEC review of it)
- Date: 2026-08-31
- Mode: spec (optimizer registry only)
- Context: vite.agent.ts implements the optimizer agent's three routes (chat / apply / analyze) mounted at vite.caliper.ts:527-529 (`/api/agent/chat`, `/api/agent/apply`, `/api/agent/analyze`). Evidence read in full: src/llm/tools.ts (FLAG_ALLOWLIST, validateToolCall, filterNoopProposals, parseFlagTokens), vite.caliper.ts:477-529 (mounts, sidecarUp probe), docs/FEATURES.md rows optimizer-console / optimizer-cloud-brain / optimizer-apply, and repo-wide searches (caliper.config.json referenced ONLY in vite.agent.ts; filterNoopProposals called ONLY at vite.agent.ts:335 and :360 — no client-side filter exists).

## Verdict

PASS WITH DIVERGENCES. The load-bearing quiet clauses hold where they bite hardest: the single write path is real (applyProposal is called only from `apply`, mounted only at `/api/agent/apply`; no other TS file touches caliper.config.json), the allowlist is enforced at BOTH the proposal and apply doors (validateToolCall), and every actual WRITE on apply reports live-server truth via activeServerFlags() with the restart note or already-active verdict said out loud. One CONFIRMED divergence: the deterministic no-op filter is unreachable on the dominant chat flow (model proposes, then answers in prose), so no-op proposals ARE surfaced as actions — the exact behavior the OPT-FLAG-ALLOWLIST boundary forbids. Four further PLAUSIBLE divergences (bench state mutation on the answer path, an "Already set" refusal that can contradict the running argv, a bench call laundered into a proposal by the nudge path, local-brain answers missing model+tokens).

## Divergences

### D1 — no-op proposals are NOT filtered on the normal chat exit (CONFIRMED)

- Clause (OPT-FLAG-ALLOWLIST, boundaries), verbatim: "a no-op proposal (flags already matching current config) is filtered, not surfaced as an action."
- Trigger: model emits a valid `set_flag`/`set_param` whose value already matches current state (config flags, or the running server's flags — currentState() merges both) in round 0, receives the QUEUED tool ack, then returns a final no-tool-call turn. Loop round 1 hits `if (calls.length === 0)` (vite.agent.ts:252) and returns via `await respondWith(out.content, citations, proposals)` (line 253) — the RAW proposals array.
- Behavior: `filterNoopProposals` runs only at line 335, AFTER the `for` loop exhausts MAX_TOOL_ROUNDS (4) — i.e., only when the model spends every round on tool calls and never finishes in prose. The standard propose→ack→answer flow (2 rounds) bypasses it entirely. The code comment at lines 332-333 ("no-op and already-active proposals die here regardless of what the model emitted") is contradicted by the early return. Verified no compensating filter exists anywhere else: `filterNoopProposals` has exactly two call sites (vite.agent.ts:335, :360) and src/llm/client.ts ships the server's proposals array to the console as-is. Mitigation that keeps this at the "surfaced" tier rather than a write: the apply pre-check (line 360) still blocks the no-op write and answers "Already set to that value - nothing changed."
- Fix: funnel both exits through one filtered respond — compute `currentState()` and run `filterNoopProposals(proposals, ...)` before the line-253 respondWith (or hoist the filter into `respondWith` itself).
- CONFIRMED (guard absent on the traced path; call-site evidence: only :335/:360 invoke the filter; no client-side filter).

### D2 — the answer path can mutate state on its own via bench outside the opening analysis (PLAUSIBLE)

- Clause (OPT-HUMAN-CLICK-WRITES, side_effects), verbatim: "no proposal path, drafting path, or answer path writes config, launches flags, or mutates state on its own."
- Trigger: any normal chat turn whose last user message does NOT start with "SYSTEM SNAPSHOT:" (the sole deterministic guard, vite.agent.ts:276-279) where the model emits a valid `bench` call — lines 281-299 then execute `runBench` (loads model gigabytes, multi-minute renders on the shared 16 GB card) and `appendMeasured` (appends to knowledge/measured-results.md) with no human click. "The user asks for it explicitly" is enforced only by the SYSTEM_PROMPT (src/llm/tools.ts:230), a prompt-level rule a small model can violate.
- Behavior: model-initiated GPU work and knowledge-store mutation inside the answer path.
- Why PLAUSIBLE, not CONFIRMED: the registry's authority (AGENTS.md; tools.ts:36-38) sanctions bench as "a measurement, not a mutation: settings only change through the human-gated proposal path" and AGENTS.md sanctions measured-results appends — so the clause's "state" arguably scopes to settings/config, which bench never touches. The divergence is the letter ("mutates state on its own") versus the heuristic enforcement of "the human asks": deterministic only for the analysis turn.
- Fix if held to the letter: gate runBench behind explicit human consent (an user message naming a measurement, or a click), mirroring the apply gate.
- PLAUSIBLE.

### D3 — "Already set" refusal can fire while the RUNNING server's argv disagrees (PLAUSIBLE)

- Clause (OPT-APPLY-HONESTY, expected), verbatim: "Applying a proposal reports what the running server actually shows: the applied flag activates the next ComfyUI start (said out loud), and a flag already present in the running server's own argv is reported as already active - never as newly applied."
- Trigger: config flag already at the proposed value while the RUNNING server's argv carries a different value (stale start). currentState() merges `{ ...await activeServerFlags(), ...flags }` (vite.agent.ts:139) — config SHADOWS the live argv — so the apply pre-check (lines 359-364) sees a no-op and answers "Already set to that value - nothing changed." without naming the server's live value or the restart needed to activate it. Reachable in composition with D1: the chat-time filter (had it run) would also have seen the merged no-op, but on the normal path the proposal is surfaced anyway; e.g. config=4 / server argv=2 / proposal 4 → surfaced (D1) → clicked → "Already set… nothing changed," while the server actually shows 2.
- Behavior: a refusal answered from config-only truth in a corner where the clause demands the running server's truth. No write occurs, and the message is literally true of the config.
- Why PLAUSIBLE, not CONFIRMED: both enumerated duties ARE satisfied on every WRITE path — applyProposal (lines 54-62) consults activeServerFlags() directly and returns the restart note ("the running server still has X; restart the backend to activate it") or "already active on the running server" or "takes effect the next time the launcher starts ComfyUI". This corner is the pre-check short-circuiting before the argv comparison; it needs a stale proposal plus diverged config/server state.
- Fix: when the pre-check refuses, also read activeServerFlags(); if the live value differs from the proposed one, append it plus the restart note.
- PLAUSIBLE.

### D4 — the nudge path can launder a bench tool call into a proposal (PLAUSIBLE)

- Clause (OPT-FLAG-ALLOWLIST, expected), verbatim: "Optimizer proposals are limited to the launch-flag allowlist; anything outside it is filtered before a proposal can carry it."
- Trigger: analysis turn (last user message starts "SYSTEM SNAPSHOT:"), 4 rounds exhausted with zero proposals, and the nudge turn (vite.agent.ts:321) emits a valid `bench` call. Line 325 skips only `read_kb`; `describeProposal` (lines 30-43) then falls into the set_param branch and titles it `Change <bundle> default: steps → undefined`, and the object is pushed with `call.name === "bench"` (line 327). If clicked, apply validates bench OK (validateToolCall allows it), the no-op pre-check keeps it (filterNoopProposals returns true for unknown names, tools.ts:153), and applyProposal falls through both branches to "unknown action" — no write.
- Behavior: a nonsense proposal card carrying a non-proposal tool; harmless to disk, but a proposal carries something outside the allowlist.
- Why PLAUSIBLE: requires the nudge model to emit bench despite the explicit "Emit the set_flag / set_param tool calls" instruction, and the write path is inert ("unknown action"). The deterministic code path exists; the clause letter says a proposal can never carry it.
- Fix: in the nudge loop accept only `set_flag`/`set_param`; additionally have `apply` 400 on any name outside {set_flag, set_param} instead of reaching applyProposal's fall-through.
- PLAUSIBLE.

### D5 — local-brain answers report neither model nor tokens (PLAUSIBLE)

- Clause (OPT-BRAIN-REGISTRY, expected), verbatim: "a question's answer reports the answering model and true per-question tokens - cost where the provider publishes pricing."
- Trigger: `gate.brain === "local"` — respondWith builds `meta = { brain: gate.brain }` (vite.agent.ts:211) and adds model/tokens only inside `if (gate.brain !== "local")` (lines 212-219). The sidecar branch (lines 196-205) parses only `choices` from llama-server's response and discards the `usage` object it returns.
- Behavior: a local question's answer meta carries no answering model and no token counts, though the provider (llama-server) accounts them.
- Why PLAUSIBLE: FEATURES.md row optimizer-cloud-brain acceptance says "a live question answers with model + tokens", and the control's title centers the cloud registry with the local sidecar named only as "fallback" — the clause may scope to cloud brains, for which it is fully satisfied here (meta.model = servedModel ?? gate.model, meta.tokens = accumulated provider usage across all rounds, costUsd priced on the model that actually answered — fetchPricing is even keyed to servedModel, and the 429 fallback names the substitute via meta.note). If local is in scope, tokens are available and dropped.
- Fix: read `usage` from the sidecar response and set meta.model/meta.tokens for the local brain too (cost stays cloud-only).
- PLAUSIBLE.

## UNJUDGEABLE HERE

- Console UX of proposals/apply/meta (rendering of proposal cards, the human click, display of model/tokens/cost) — owners: src/components (console surfaces) and src/llm/client.ts (agentChat / agentApply / agentAnalyzeTask fetch wrappers).
- "the brain picker lists every brain live" and the cloud→local fallback selection — owners: src/providers/brainProviders.ts (BRAIN_ENDPOINTS registry), vite.llm.ts (brainGate source), console UI. Note: within THIS file, cloud brains ride one transport as required (openRouterChat with per-brain endpoint override) and there is no local fallback on cloud failure (non-429 errors → 502) — whether a local fallback exists at the gate/picker level is owned there.
- Sidecar lifecycle ("AI ON spawns nothing"; spawn only when a local-brain question needs it; /free VRAM purge first; killed after the session) — owner: vite.llm.ts (llmRoutes, mounted at /api/llm/*); vite.caliper.ts:488-495 supplies `sidecarUp` as a read-only health probe that this file only reads (chat/analyze 503 when local brain is down — consistent with spawning nothing, but the spawn/kill behavior itself is not here).
- readKb/BM25 store behavior (vite.kb.ts) and runBench internals (vite.bench.ts) — called here, owned there.
- The `analyze` task text's directive strength ("Do NOT call bench") is prompt material; its deterministic enforcement is the D2 guard and was judged there.
