<!-- colibri review
source: src/vram/preflight.ts
reviewer: glm-5.3 (ZCode session, colibri v0.2.0 protocol)
sha256: 71a04a5a9fa62f1bc0d6cbf2349d56e029da0080bfd222a6e3ea664907786e29
date: 2026-09-06
mode: bug
context: E-4 wave (queue/deck quality batch); copy-diagnostics verified live with clipboard result; etaMs live null-with-basis
-->

## Verdict
Shippable. parseBenchEta shares parseBenchFootprint's newest-entry-wins discipline; the median regex cannot catch the warmup's cold-load sentence ("Cold load (warmup render): Nms" has no 'median' before ms - pinned by test); etaMs rides all five verdict paths.
