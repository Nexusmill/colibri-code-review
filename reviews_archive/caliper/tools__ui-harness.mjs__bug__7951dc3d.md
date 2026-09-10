<!-- colibri review
source: tools/ui-harness.mjs
reviewer: glm-5.3 (ZCode session, colibri v0.2.0 protocol)
sha256: 7951dc3df7b441a9abf59acf54d7b68eabf446631355ff9c42d3f845f8140e88
date: 2026-09-06
mode: bug
context: E-3 wave (POWER ON); live e2e through the rig (stop -> START seat -> 15s return with flags); delta reviews
-->

## Verdict
Shippable. power-on fast-tier test: cold and honest in both worlds - backend up asserts the 409 refusal vocabulary AND that the taskbar shows no START key; backend down asserts the START seat exists. It never starts or stops anything itself (the start path is the launcher's own tail, exercised by the e2e verification recorded in HISTORY).
