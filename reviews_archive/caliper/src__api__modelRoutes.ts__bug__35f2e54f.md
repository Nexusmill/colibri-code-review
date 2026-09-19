<!-- source: src/api/modelRoutes.ts | reviewer: zcode-glm-5.3 | sha256: 35f2e54fd3d8b7ee8db17daa8814a3fc9dbaa9bf5056781834e75de7ee2f1add | date: 2026-09-15 | mode: bug -->
<!-- context: Wave 6 FINAL delta review (post design-adversary remediation). Call sites traced live (curl through :4173, harness PASS 75/0/8, vitest 499/499, tsc 0); FEATURES row `route-intelligence` + docs/reviews/route-intelligence-2026-09-15.md are the contract. -->

## Verdict
Shippable - clean delta; no findings.

## Bugs & vulnerabilities (delta: health/presets types + normalization + routePreset with replaced)
- None. Normalization defaults never leak undefined (pinned by the api test); routePreset surfaces the server's own error words on !ok and passes `replaced` through untouched (pinned).
