<!-- colibri review
source: src/power/state.ts
reviewer: glm-5.3 (ZCode session, colibri v0.2.0 protocol)
sha256: 0ae69c27d2efa25314e1a862968d6b9167b1ecc3d46c2b5600b962df9539e392
date: 2026-09-06
mode: bug
context: E-3 wave (POWER ON); live e2e through the rig (stop -> START seat -> 15s return with flags); delta reviews
-->

## Verdict
Shippable. The start key's words: START / CONFIRM? / STARTING...; the confirm line never says RENDER DIES for a start (nothing runs); the tooltip names the launcher's own start script and the flags truth. Pure, test-pinned.
