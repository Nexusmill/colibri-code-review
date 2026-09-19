<!-- source: vite.caliper.ts | reviewer: zcode-glm-5.3 | sha256: 8c1e43050a46eb82fc76f4d8ff403e350a48849361e987ea58dbdf639d0631c3 | date: 2026-09-15 | mode: bug -->
<!-- context: post adversarial-gate remediation (KV clamp 32k, all download paths verify, batched WMI). Evidence: tsc 0, vitest 508/508, tier 77/0/7, live node 1.2.1. -->

## Verdict
Shippable.

## Bugs & vulnerabilities (delta)
- **[LOW|noted] sha verification of multi-GB artifacts adds ~30-60s with no distinct progress line** (unchanged note). llmStream now forwards expect; the single enforcement point serves every path.
