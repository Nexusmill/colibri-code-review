# Spec review — src/api/client.ts

- Source: `src/api/client.ts` (207 lines) · Reviewer: ZCode in-session (GLM-5.3) · sha256: `9f5e8b48e71cf315960bfc0c870fa88f1340d6fd4834707be4c77ef718792258` · 2026-08-31 · mode: **spec** · registries: `spec/generate.json`, `spec/api-network.json`, `spec/power-vram.json`
- Context pack: full read; the /free proxy-404 incident (AGENTS.md) checked against freeVram's error path; queue endpoints cross-checked with FEATURES queue-surface.

## Verdict
Conforms — no divergences. Notably: `freeVram()` THROWS on `!res.ok` with the route status (client.ts:120-129) — the /free silent-404 hole is explicitly defended here, satisfying API-PROXY-COMPLETENESS's error_paths at the client end; `getCaliperVram()` likewise throws rather than returning a fake ok; `clearQueue()` clears through the server (`POST /queue {clear:true}` + interrupt), satisfying GEN-QUEUE-SURFACE-TRUTH's "through the server, not by hiding rows"; `queuePrompt` returns structured rejections with node errors (GEN-RENDER-LIFECYCLE's honest-failure path).

## Divergences
None.

## UNJUDGEABLE HERE
- GEN-RENDER-GUARD disabled_state (button) — GenerateSurface.tsx.
- API-LOCALHOST-ONLY websocket-direct clause — src/api/ws.ts.
- PWR-CONFIRM-ARMING / restart-walk observables — power UI component + vite.power.ts.
