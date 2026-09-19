<!-- source: src/install/catalog.test.ts | reviewer: zcode-glm-5.3 | sha256: da143b77ec40a280b8c674227820f243f7a150e68a648c399125f37b3ef6137b | date: 2026-09-15 | mode: bug -->
<!-- context: post adversarial-gate remediation (KV clamp 32k, all download paths verify, batched WMI). Evidence: tsc 0, vitest 508/508, tier 77/0/7, live node 1.2.1. -->

## Verdict
Shippable.

## Bugs & vulnerabilities (delta)
- None. serveCtx's clamp test flipped from the broken 131072 to the arithmetic-honest 32768 (the gate finding as the red).
