<!-- colibri review
source: src/api/client.ts
reviewer: glm-5.3 (ZCode session, colibri v0.2.0 protocol)
sha256: 982e05eb87e72dfdcc6db1adba79b05ac444d29bdec70f20124744516a02f509
date: 2026-09-06
mode: bug
context: E-1 wave (node self-identification); live-verified through :4173 + backend 8188 this session; prior reviews consulted via _manifest.json (delta reviews)
-->

## Verdict
Shippable. Delta: NodeSync interface + getNodeSync() following the getCaliperVram idiom (throw on !ok so the footer keeps its last good canonical). No other exports touched.
