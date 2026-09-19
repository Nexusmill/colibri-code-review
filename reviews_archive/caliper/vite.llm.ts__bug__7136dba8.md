<!-- source: vite.llm.ts | reviewer: zcode-glm-5.3 | sha256: 7136dba8db6c63de76751840fcd4ba0c14e85cdcc0f090f848200780ce2d6b79 | date: 2026-09-15 | mode: bug -->
<!-- context: post adversarial-gate remediation (KV clamp 32k, all download paths verify, batched WMI). Evidence: tsc 0, vitest 508/508, tier 77/0/7, live node 1.2.1. -->

## Verdict
Shippable - all three download paths now verify.

## Fixed since last review (this delta, per the adversarial gate)
- **[MEDIUM|FIXED] the provision and shelf get-it paths skipped verification** - llmStream's signature carries the optional pin and both internal call sites pass it (the factory brain's catalog entry; the shelf entry's bytes + sha when present). The .part rename alone never caught a cleanly-terminated short transfer - the pin does.

## Bugs & vulnerabilities (delta)
- None. The serveCtx clamp + status ctxSize unchanged in shape.
