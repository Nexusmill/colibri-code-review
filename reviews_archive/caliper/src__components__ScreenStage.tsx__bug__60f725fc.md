<!-- colibri review
source: src/components/ScreenStage.tsx
reviewer: glm-5.3 (ZCode session, colibri v0.2.0 protocol)
sha256: 60f725fc7ca93fa2a6f8be975c6b14234e9f2e330d7bc3fb1addc494bd47ec8b
date: 2026-09-06
mode: bug
context: E-3 wave (POWER ON); live e2e through the rig (stop -> START seat -> 15s return with flags); delta reviews
-->

## Verdict
Shippable. Delta: PowerKeys reads socketState; the seat set is derived (restart while connected, start while not, a busy key pins its own seat so a restart cannot morph into a mid-press start when its own stop drops the socket); fire("start") walks comfyStart with BACKEND STARTING.../BACKEND UP status. Verified live: seats [START, POWER] while down, [RESTART, POWER] while up.

## Bugs & vulnerabilities
(none confirmed)

- REFUTED in pass 3: "socketState 'connecting' at boot could show START prematurely" - connecting is treated as not-down (the seat reads RESTART); the START seat requires disconnected, and a premature RESTART press gets the server's own 409.
