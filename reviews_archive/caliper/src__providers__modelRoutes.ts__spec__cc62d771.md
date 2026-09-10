# Spec review — src/providers/modelRoutes.ts

- Source: `src/providers/modelRoutes.ts` (87 lines) · Reviewer: ZCode in-session (GLM-5.3) · sha256: `cc62d7711f1abdaca0d111a004d983e505f2ec3de65d14cf1f87f145bcdc4544` · 2026-08-31 · mode: **spec** · registry: `spec/generate.json`
- Context pack: full read; profile/route model cross-checked against FEATURES generate-source-select (owner spec 2026-08-22); persistence and write paths located elsewhere (routesStore, src/api/modelRoutes.ts).

## Verdict
Conforms as the pure routing core — no divergences. `validateRoute` enforces cloud-only profile law and shelf/service/model completeness; `resolveRoute` implements "local when the shelf has candidates and the profile allows, else cloud"; `cloudRunnable: false` on the llm type is honest capability (the picker never offers a route the engine can't run).

## Divergences
None. (Staleness note, non-spec: the Route comment "cloud: \"replicate\" today; eachlabs/xai come with their adapters" is stale — OpenRouter and EachLabs adapters are live per FEATURES. Comment-only; no behavioral divergence.)

## UNJUDGEABLE HERE
- GEN-SOURCE-SELECT persistence-across-reloads — routesStore.ts.
- GEN-CLOUD-SCHEMA-SEAT "SET AS DEFAULT writes the route" — src/api/modelRoutes.ts + picker UI.
