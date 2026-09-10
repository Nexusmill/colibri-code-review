# Spec review — src/bundles/constraints.ts

- Source: `src/bundles/constraints.ts` (62 lines) · Reviewer: ZCode in-session (GLM-5.3) · sha256: `01434323ac30cc230bbcddd58c6ddedacdd6462b9b3f79d4227ff93c6b266169` · 2026-08-31 · mode: **spec** · registry: `spec/bundles.json`
- Context pack: full read; ScrubInput.settle (the snap caller) cross-checked via outline; parseDetent consumed by schema.ts validation (verified there).

## Verdict
Conforms — no divergences. `snapToDetent` + `snapMessage` implement BND-FRAME-DETENT-SNAP's observable: the correction message names both the detent expression and the settled value ("Frames must be 8n+1. Snapped to 97." shape). `violations()` is null-safe on unparseable detents (det === null skips the check — no crash), and unparseable detents are already refused upstream at schema validation.

## Divergences
None.

## UNJUDGEABLE HERE
- The typing flow itself (typed value → snap → message shown) — lives in ScrubInput.tsx / GenerateSurface.
