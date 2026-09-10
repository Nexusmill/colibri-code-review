# Colibri review — src/llm/tools.ts (feature)

- **Source:** `src/llm/tools.ts` · **sha256:** 84daa792
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** the optimizer's deterministic core (AGENTS.md names it specially: "the model proposes; only a human click writes"); consumed by vite.agent (chat loop, apply re-validation) and tests; verified: bench accepts steps|cfg only, one flag in the allowlist, no read_vram tool; unchanged since 9b95dac (2026-08-20).

## What this module does

The tool contract: FLAG_ALLOWLIST (today: vram-headroom alone, with plain-English and a KB citation each), PARAM_ALLOWLIST (six bundle defaults), `validateBenchArgs` (exactly two values of steps|cfg, fixed seed, 1-2 repeats — a measurement, never a mutation), `validateToolCall` (the gate every proposal and every APPLY re-passes), `parseFlagTokens` (argv → flags map for live-server truth), `filterNoopProposals` (the deterministic counter-signal on every exit path), the TOOLS schemas, and the SYSTEM_PROMPT with its turbo-quality and bench-discipline hard rules.

## Suggested add-ons

**Widen the bench param surface** — Value Med · Effort S
- What: bench validates `steps` and `cfg` only (line 43); PARAM_ALLOWLIST already trusts six params. A width/resolution A/B (768 vs 512) is a real question the bench refuses — and timedRender in vite.bench applies any param generically, so the refusal lives only here.
- Why: "settle speed questions with measurements" is the prompt's own doctrine; resolution is the biggest speed/quality lever on the card and the optimizer cannot measure it.

**More proven flags in the allowlist** — Value Med · Effort S
- One flag is a thin surface for a flag-driven backend; each entry needs plain+cite (the design), and the knowledge corpus holds measured flag effects to mine. Owner-curated growth is the file's own pattern — the add-on is the mining pass, not a schema change.

**A read_vram tool** — Value Low-Med · Effort S
- The analysis snapshot includes VRAM once at open; a read_vram tool (the /caliper/vram payload, read-only) lets the brain ground residency claims mid-conversation ("is the LTX still resident?"). Fits the every-number-cited rule.

## Nice-to-haves

- SYSTEM_PROMPT's turbo rules hardcode Anima-Aesthetic as the quality preset; if bundles change, the guardrail text drifts — deriving from bundle data would self-maintain. Low.
