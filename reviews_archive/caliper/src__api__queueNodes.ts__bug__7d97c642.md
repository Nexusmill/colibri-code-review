<!-- colibri review
source: src/api/queueNodes.ts
reviewer: glm-5.3 (ZCode session, colibri v0.2.0 protocol)
sha256: 7d97c64277e892b03ce1779d88155369b5b7996f0030042bd6b0f0a442f0b063
date: 2026-09-06
mode: bug
context: E-4 wave (queue/deck quality batch); copy-diagnostics verified live with clipboard result; etaMs live null-with-basis
-->

## Verdict
Shippable. Pure decode of the queue blob's class_type values + one spoken line; malformed shapes return [] never throw (pinned).
