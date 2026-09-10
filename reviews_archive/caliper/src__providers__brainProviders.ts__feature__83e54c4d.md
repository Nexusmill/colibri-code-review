# Colibri review — src/providers/brainProviders.ts (feature)

- **Source:** `src/providers/brainProviders.ts` · **sha256:** 83e54c4d
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** the brain registry (glm-5.3 the owner-persisted default, ruling 26; the grok/groq relabeling); consumed by vite.llm (gate/endpoints), ScreenStage's picker, vite.agent; unchanged since 836c6e7 (2026-08-27).

## What this module does

53 lines: nine BRAIN_OPTIONS across openrouter (glm-5.3 family, deepseek family, the free tier), spacexai (grok 4.6/4.5), groq (free gpt-oss-120b), and the local sidecar — each with priced hints — the BRAIN_ENDPOINTS map (OpenAI-compatible base URLs with their settings keys), `isBrainId`, and `parseBrainValue` for the picker's `provider|model` strings.

## Suggested add-ons

**"More models" from the live catalog** — Value Med · Effort S-M
- What: a final picker row ("other OpenRouter models…") reading the live /models list (fetchPricing already pulls it hourly) so ANY model can be the brain, priced on selection.
- Why: the shortlist is curated and stale-prone by nature (the hints hardcode per-M rates); the registry's own design already separates option from endpoint, so the dynamic rows slot straight in. The persisted brain.json honors any pick.

**Context-length metadata as data** — Value Low · Effort S
- The glm-5.3 hint says "1M context" in prose; a `contextTokens` field would let long-draft calls (the storyboard JSON) check fit instead of discovering truncation (the token-ceiling degeneration class is in the defect ledger).

**Per-endpoint liveness** — cross-ref the R2 key-liveness TEST add-on: the registry is the natural map of which cheap authenticated call answers per provider (whoami for groq/x.ai, models for openrouter).

## Nice-to-haves

- The local option's empty model string is a shape wart (`parseBrainValue` requires non-empty model, so "local|" rows bypass it) — a `local` sentinel would be cleaner; cosmetic.
