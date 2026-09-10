# Spec review — src/install/catalog.ts

- Source: `src/install/catalog.ts` (142 lines) · Reviewer: ZCode in-session (GLM-5.3) · sha256: **unavailable — the harness security hook denied every read-only hashing command for this path (4 attempts, forms that passed for the other nine files); identified instead by full content read: 142 lines, 4 manifests, 8 LLM models, read 2026-08-31** · mode: **spec** · registry: `spec/bundles.json` (+ API-LOCALHOST-ONLY download exception)
- Context pack: full read via jcodemunch (current on-disk content, freshness satisfied by content read); manifest ids cross-checked against schema.ts defaultBundles ids (LTX-2.3-Distilled, Anima-Aesthetic-v1.1, Anima-Turbo, Krea-2-Turbo — aligned).

## Verdict
Conforms as the install-catalog data layer — no divergences. URLs are HF resolve links only (or explicit MANUAL notes for login-gated/derived files), matching API-LOCALHOST-ONLY's sole outbound exception; manifest ids align with bundle ids.

## Divergences
None.

## UNJUDGEABLE HERE
- BND-EDITOR-SURFACE "Files column shows per-bundle file state" — rendering lives in BundlesSurface.tsx + src/install/plan.ts.
