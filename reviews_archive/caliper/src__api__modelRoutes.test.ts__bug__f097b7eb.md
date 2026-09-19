<!-- source: src/api/modelRoutes.test.ts | reviewer: zcode-glm-5.3 | sha256: f097b7ebf69253614512d80178ecbf612f2cd24906bfc63cfadea85266baa614 | date: 2026-09-15 | mode: bug -->
<!-- context: Wave 6 FINAL delta review (post design-adversary remediation). Call sites traced live (curl through :4173, harness PASS 75/0/8, vitest 499/499, tsc 0); FEATURES row `route-intelligence` + docs/reviews/route-intelligence-2026-09-15.md are the contract. -->

## Verdict
Shippable - fresh file, no findings.

## Bugs & vulnerabilities
- None. The fetch stub pins the POST shape, the presets round-trip, the replaced flag both ways, empty-shape normalization, and the server-error words surfacing through the thrown message.
