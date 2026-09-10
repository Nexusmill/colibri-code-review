<!-- colibri review
source: vite.power.ts
reviewer: glm-5.3 (ZCode session, colibri v0.2.0 protocol)
sha256: a07e80b6486931f4dc8a413335b0c3180c0dd7ea3fb254b046d36e274042dc21
date: 2026-09-06
mode: bug
context: E-3 wave (POWER ON); live e2e through the rig (stop -> START seat -> 15s return with flags); delta reviews
-->

## Verdict
Shippable. Delta: spawnStartTail (the launcher's own start-comfyui.cmd, detached+unref+windowsHide, identical to the restart tail's construction) and the comfy-start action - 409 when the backend already answers, spawn, observed 150s port poll, 504 with its sentence. No stop path touched.

## Bugs & vulnerabilities
(none confirmed)

- REFUTED in pass 3: "the detached start tail could double-start if pressed twice" - the UI keeps one press busy until the poll resolves, and a second app-server POST while up hits the 409 guard; start-comfyui.cmd itself also polls the port before handing back.
