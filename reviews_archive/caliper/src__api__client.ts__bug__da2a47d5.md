<!-- colibri review
source: src/api/client.ts
reviewer: glm-5.3 (ZCode session, colibri v0.2.0 protocol)
sha256: da2a47d52054aec1b7a508071490ec99d0eb34c00b4b662b78f6de28211f943a
date: 2026-09-06
mode: bug
context: E-3 wave (POWER ON); live e2e through the rig (stop -> START seat -> 15s return with flags); delta reviews
-->

## Verdict
Shippable. comfyStart mirrors the power client idiom (POST, error passthrough).
