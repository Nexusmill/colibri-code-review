<!-- colibri review
source: src/surfaces/BundlesSurface.test.tsx
reviewer: glm-5.3 (ZCode session, colibri v0.2.0 protocol)
sha256: c9023f7292acb5c63427dfa5fdfa2926ccd3e555db19988f60426b21e4d781b6
date: 2026-09-06
mode: bug
context: E-6 wave (bundles idiom+copy, graph restore-by-timestamp+drift, palette verbs+legend, docview code+find); the stale-dist incident and its healing
-->

## Verdict
Shippable. The remove test now walks arm-then-fire with the store count asserted between presses - the exact regression the wave exists for.
