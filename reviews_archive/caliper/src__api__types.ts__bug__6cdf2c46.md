<!-- colibri review
source: src/api/types.ts
reviewer: glm-5.3 (ZCode session, colibri v0.2.0 protocol)
sha256: 6cdf2c4639e1b5b96523d4c6dde15a9e2f7075b9cf840c31970dcf293ae87867
date: 2026-09-06
mode: bug
context: E-1 wave (node self-identification); live-verified through :4173 + backend 8188 this session; prior reviews consulted via _manifest.json (delta reviews)
-->

## Verdict
Shippable. Additive optional `node?: { name; version; sha256 }` on CaliperVram - mirrors the python payload field exactly; all existing consumers ignore unknown/absent fields.
