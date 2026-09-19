# Emberline feature delta: music.js

Mode: feature implementation review
Reviewed: 2026-09-16 18:12 UTC
Source: implementations/emberline/music.js
SHA-256: 6ad8aa985adcfefdf60aba3ab0b5c99ae4c2f71724819d7d292e1f14f6a05877
Prior feature review: .colibri_reviews/implementations__emberline__music.js__feature__aaa191ad.md
Prior source SHA-256: aaa191ad12f4739b5567b5f5efee1f6ab366d38bf541851c1cde17f06cb5a57a
Gameplay commit: 0eba7e0b2601

## Fixed since last review
Main proposal — Narration ducking: implemented.
setDucked changes only the existing music gain, retaining score scheduling/cursor. Game preserves requested ducking before player creation and voice activity releases it on completion/cancellation.

## Evidence
music.test.cjs verifies gain changes, mute and unchanged notes/cursor; UI integration exercises connection.
The integrated broker run passed (36 Python tests, four skipped, exit 0, unchanged tree), including all eight Node suites. Exact-byte pre-write reviews cleared the applied source; the additional Git gate returned CLEAR in .adversary/reviews/gate_20260916-121154.md and committed 18 source/test files.

## Scope and limits
This delta closes the main proposal from the prior feature review. Optional Nice-to-haves remain exploratory and unimplemented. This is not a new blanket bug/spec clearance. Live browser, physical-device and listening QA were unavailable because browser automation was refused by project policy. See docs/tasks/2026-09-16-emberline-features.md for shared validation and boundaries.
