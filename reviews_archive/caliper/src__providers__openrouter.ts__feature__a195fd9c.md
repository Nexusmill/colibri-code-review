# Colibri review — src/providers/openrouter.ts (feature)

- **Source:** `src/providers/openrouter.ts` · **sha256:** a195fd9c
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** the optimizer's cloud transport (one chat shape across brains); pricing cached an hour; costUsd sums tokens across ALL loop rounds; verified: OPENROUTER_DEFAULT_MODEL ("z-ai/glm-5.2:free") is referenced NOWHERE else — dead stale data (the live default is BRAIN_OPTIONS[0] glm-5.3 + brain.json); last touch af12a90 (2026-08-22).

## What this module does

112 lines: `openRouterChat` (the shared transport with the x-title header and 120s timeout — also the transport for SpaceX AI/Groq via the endpoint override), `parseChatCompletion`, `fetchPricing` (live catalog, 1h cache per model), `costUsd` (true per-question cost across every tool round), `fmtCost` (4 decimals under a dime), and the OPENROUTER_PICKS shortlist.

## Suggested add-ons

**Delete or refresh the dead default** — Value Low · Effort S (a cleanup, flagged here for the record)
- `OPENROUTER_DEFAULT_MODEL` says glm-5.2:free and has zero consumers (verified by search) — the defaulting path moved to BRAIN_OPTIONS + the persisted brain.json in Eras 35/36. A stale "default" constant in the transport file is exactly the class of drift the price-truth doctrine warns about; remove it or derive it from BRAIN_OPTIONS.

**Cache the catalog response, not per-model lookups** — Value Low · Effort S
- `fetchPricing` fetches the WHOLE /models list and caches per model id — a second model within the hour refetches the entire list. Cache the parsed list once (map id→pricing) and the per-model reads become free.

**Streamed brain answers (cross-file theme)** — Value High · Effort M — filed for the synthesis
- This file is the optimizer console's transport; the wizard's draft phases (askBrain in vite.film) and the agent loop both answer in one blocking blob, minutes long. SSE streaming with progressive display is the live-progress owner rule applied to the brain; the transport shape (chat/completions) supports it. The work spans this file + askBrain + the wizard's status line — one theme, three hooks.

## Nice-to-haves

- Usage may carry cached/prompt-cache token fields on OpenRouter; costUsd ignores them (conservative — fine).
