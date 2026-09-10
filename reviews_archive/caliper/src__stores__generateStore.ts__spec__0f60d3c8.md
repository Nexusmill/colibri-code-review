# Colibri spec-conformance review — src/stores/generateStore.ts

- source: E:\AI\Caliper\src\stores\generateStore.ts
- reviewer: ZCode fresh-context subagent
- sha256: 0f60d3c8fea9d85b0650a437cfb58a41245c6c7dd44e3508c342075b2dc665e1 (0f60d3c8)
- date: 2026-08-31
- mode: spec — E:\AI\Caliper\spec\bundles.json (BND-TOUCHED-ONLY-PERSISTENCE, BND-PROMPT-PER-BUNDLE, BND-FILE-DEFAULTS-SHOWN data layer, BND-FRAME-DETENT-SNAP where the store participates)
- context: 35-line zustand+persist store for Screen 4's LOCAL|CLOUD source selection (mode, cloudType, cloudService, cloudModel), persisted under `caliper.generate`. Consumers: src/components/DeckControls.tsx (SourceSelect), src/surfaces/GenerateSurface.tsx (cloudSeat). Verified via jcodemunch find_references + search_text on repo local/Caliper.

## Verdict

PASS — no divergence between this file and the cited clauses. The store does not participate in any of the four clause behaviors: it holds no bundle parameters, no prompt text, no frame/detent state, and no bundle identity. All clause-governed data lives in src/stores/bundlesStore.ts.

Quiet-clause audit (BND-TOUCHED-ONLY-PERSISTENCE side_effects, "UI persistence lives under the storage key caliper.bundles-ui and nowhere else"): this store persists under `caliper.generate`, not `caliper.bundles-ui`. Adjudicated NOT a divergence: the clause pins where the touched-params feature persists; a repo-wide literal reading would equally condemn `caliper.screen`, which the same cited authority (AGENTS.md persistence keys) sanctions — so the literal reading is refuted. No clause-governed state (params, paramEdits, prompts, selected) leaks into `caliper.generate`; the partialize list is exactly mode/cloudType/cloudService/cloudModel (generateStore.ts:34). Refuted candidate finding deleted per protocol.

## Divergences

None.

## UNJUDGEABLE HERE

- BND-TOUCHED-ONLY-PERSISTENCE (expected + boundaries: touched fields survive reload, untouched follow the file, v1 full-map migration) — owned by src/stores/bundlesStore.ts: `paramEdits` touched-only map (lines 20-23, 233-237), `migratePersisted` v1→v2 (lines 64-80), load overlay `params: { ...fresh[name], ...paramEdits[name] }` (line ~125), persist name `caliper.bundles-ui` (line 255). Reviewed only as ownership evidence; that file needs its own review.
- BND-PROMPT-PER-BUNDLE — owned by src/stores/bundlesStore.ts (`prompts: Record<string, string>`, `setPrompt`). generateStore has no prompt field.
- BND-FILE-DEFAULTS-SHOWN data layer — owned by src/stores/bundlesStore.ts (`initParams` seeding from `b.defaults.*`, authoritative-file-defaults overlay on load). The stepper rendering itself is the Generate surface/DeckControls; the correction-message toast display likewise lives in UI code.
- BND-FRAME-DETENT-SNAP — owned by src/stores/bundlesStore.ts `setParam` (snapToDetent/snapMessage imported from src/bundles/constraints.ts; post-snap values recorded as touched; `lastSnap` in state). generateStore contains no frames field and does not participate.
