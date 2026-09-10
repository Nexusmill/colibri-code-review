# Spec review — src/bundles/schema.ts

- Source: `src/bundles/schema.ts` (172 lines) · Reviewer: ZCode in-session (GLM-5.3) · sha256: `0c73be86e4efc2ef0933e8d7d231e9f4b72572d4d9b314996468e8bf9a56041a` · 2026-08-31 · mode: **spec** · registry: `spec/bundles.json`
- Context pack: jcodemunch outline (rank 1 of 212 by import PageRank, in-degree 18); validateBundles/withIds read end-to-end; parseDetent cross-checked in constraints.ts; contract sources = spec/bundles.json + AGENTS.md schema note.

## Verdict
Conforms at the validation layer — no divergences. `validateBundles` enforces exactly BND-VALIDATE-LOAD-AND-SAVE's validation half: ids required AND duplicate-checked (both id and name), and `constraints.frames` is refused unless `parseDetent` accepts it (schema.ts:100-104), which also satisfies BND-FRAME-DETENT's boundary clause at the schema. `withIds` migrates missing ids uniquely without slugging.

## Divergences
None.

## UNJUDGEABLE HERE
- BND-VALIDATE-LOAD-AND-SAVE error_paths ("save surfaces the message and writes nothing") — save flow lives in BundlesSurface.tsx / vite.caliper.ts.
- Visible-message rendering — UI layer.
