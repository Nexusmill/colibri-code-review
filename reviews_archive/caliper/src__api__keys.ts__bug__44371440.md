<!-- colibri review
source: src/api/keys.ts
reviewer: glm-5.3 (ZCode session, colibri v0.2.0 protocol)
sha256: 44371440a7aa466736a274e352c7ed47610e3ff092b8fa4732d469d2c77d49b9
date: 2026-09-06
mode: bug
context: E-2 wave (key liveness + stale routes); live-verified through :4173 (three real probes, stale flag + restore); delta reviews vs prior shas
-->

## Verdict
Shippable. testKey mirrors the setKey idiom (throw on !ok with the server's error); the verdict shape carries ok/account/kind/say.
