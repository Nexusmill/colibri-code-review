# Emberline feature delta: engine.js

Mode: feature implementation review
Reviewed: 2026-09-16 18:12 UTC
Source: implementations/emberline/engine.js
SHA-256: 00c4c12d12b3ad531bdabc6f6dc199286f78df4f774d553636bf079ab009ee85
Prior feature review: .colibri_reviews/implementations__emberline__engine.js__feature__306ea0d9.md
Prior source SHA-256: 306ea0d9089f0a9611ce0011c41a35bd6ed0a98ca754420974c1443fec1971f1
Gameplay commit: 0eba7e0b2601

## Fixed since last review
Main proposal — Primary upgrade progress: implemented.
primaryProgress supplies the same level calculation used for firing and returns collected/remaining/MAX. Pickup crossing emits one primaryupgrade event. Enemy spawning consumes shared encounter metadata. Existing progression/combat work is included; intro shield pickups now avoid the opening circle.

## Evidence
engine.test.cjs covers collection thresholds 7→8 and 71→72, capped/restored state and once-only events; existing combat tests pass.
The integrated broker run passed (36 Python tests, four skipped, exit 0, unchanged tree), including all eight Node suites. Exact-byte pre-write reviews cleared the applied source; the additional Git gate returned CLEAR in .adversary/reviews/gate_20260916-121154.md and committed 18 source/test files.

## Scope and limits
This delta closes the main proposal from the prior feature review. Optional Nice-to-haves remain exploratory and unimplemented. This is not a new blanket bug/spec clearance. Live browser, physical-device and listening QA were unavailable because browser automation was refused by project policy. See docs/tasks/2026-09-16-emberline-features.md for shared validation and boundaries.
