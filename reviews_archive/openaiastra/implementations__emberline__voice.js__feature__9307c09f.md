# Emberline feature delta: voice.js

Mode: feature implementation review
Reviewed: 2026-09-16 18:12 UTC
Source: implementations/emberline/voice.js
SHA-256: 9307c09fe582946a2e90b416b553f353b2b527fc2de9123b04655c8c3ddf6afd
Prior feature review: .colibri_reviews/implementations__emberline__voice.js__feature__3121593a.md
Prior source SHA-256: 3121593a917c09e147e8e6121015f266838786902f64b0abd60d11fc06b653f8
Gameplay commit: 0eba7e0b2601

## Fixed since last review
Main proposal — Independent silent captions: implemented.
Caption availability is independent of audible narration. Silent lines have bounded reading lifetimes, require no Audio or audio unlock, and retain interruption/cancellation policy without ducking.

## Evidence
voice.test.cjs uses an audioFactory rejection sentinel, checks silent expiry, cancellation and duck callbacks; UI tests muted silent preference.
The integrated broker run passed (36 Python tests, four skipped, exit 0, unchanged tree), including all eight Node suites. Exact-byte pre-write reviews cleared the applied source; the additional Git gate returned CLEAR in .adversary/reviews/gate_20260916-121154.md and committed 18 source/test files.

## Scope and limits
This delta closes the main proposal from the prior feature review. Optional Nice-to-haves remain exploratory and unimplemented. This is not a new blanket bug/spec clearance. Live browser, physical-device and listening QA were unavailable because browser automation was refused by project policy. See docs/tasks/2026-09-16-emberline-features.md for shared validation and boundaries.
