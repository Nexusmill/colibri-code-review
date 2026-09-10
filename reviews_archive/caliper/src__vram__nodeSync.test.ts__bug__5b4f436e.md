<!-- colibri review
source: src/vram/nodeSync.test.ts
reviewer: glm-5.3 (ZCode session, colibri v0.2.0 protocol)
sha256: 5b4f436ee5d98c7170af5676e44727f5fb062474598375e76dee0054fd3bcd6f
date: 2026-09-06
mode: bug
context: E-1 wave (node self-identification); live-verified through :4173 + backend 8188 this session; prior reviews consulted via _manifest.json (delta reviews)
-->

## Verdict
Shippable. Covers all four verdict branches plus the same-version-different-bytes drift (the sha-is-truth case).
