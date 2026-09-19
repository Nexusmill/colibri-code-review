<!-- source: src/install/catalog.ts | reviewer: zcode-glm-5.3 | sha256: a3dd0c50685410d5a8460a0121722c37289746f22ea32ab083b9e093795e12e4 | date: 2026-09-15 | mode: bug -->
<!-- context: post adversarial-gate remediation (KV clamp 32k, all download paths verify, batched WMI). Evidence: tsc 0, vitest 508/508, tier 77/0/7, live node 1.2.1. -->

## Verdict
Shippable - the gate's KV-arithmetic catch is fixed: the clamp is now what the card can HOLD, not a token-count guess.

## Fixed since last review (this delta, per the adversarial gate)
- **[HIGH|FIXED] the 131,072 clamp would have killed the default brain at spawn** - ~144 KiB/token of GQA KV cache means ~19 GiB of cache alone at 131k on the 16 GB card. serveCtx now clamps to 32,768 (~4.6 GiB cache + 2.4 GB weights; the sidecar spawns VRAM-purged and never runs beside a render); the test that had pinned the broken 131072 now pins 32768 with the arithmetic in-line - the gate's finding WAS the red.

## Bugs & vulnerabilities (delta)
- None beyond the prior notes. Grounded pins unchanged.
