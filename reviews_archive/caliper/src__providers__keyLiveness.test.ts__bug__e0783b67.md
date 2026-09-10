<!-- colibri review
source: src/providers/keyLiveness.test.ts
reviewer: glm-5.3 (ZCode session, colibri v0.2.0 protocol)
sha256: e0783b67dcd8e33990153144ad781ecc1493dc3e43414dd2c78d1756359b4dfb
date: 2026-09-06
mode: bug
context: E-2 wave (key liveness + stale routes); live-verified through :4173 (three real probes, stale flag + restore); delta reviews vs prior shas
-->

## Verdict
Shippable. Covers all five verdict branches, the unreachable constant, probe-table totality, and the account extractors against real response shapes including the key-label guard (sk-or- prefixed labels never display).
