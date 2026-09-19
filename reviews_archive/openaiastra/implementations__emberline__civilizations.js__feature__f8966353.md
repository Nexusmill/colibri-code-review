# Emberline feature delta: civilizations.js

Mode: feature implementation review
Reviewed: 2026-09-16 18:12 UTC
Source: implementations/emberline/civilizations.js
SHA-256: f89663533d93613693a23076e8d2845fba3e136ee11414db11ea3d760f60aa11
Prior feature review: .colibri_reviews/implementations__emberline__civilizations.js__feature__888c03d5.md
Prior source SHA-256: 888c03d5043e7c64f02181869b7075fc45d86b9dc88f91ef92af6c1890538bfb
Gameplay commit: 0eba7e0b2601

## Fixed since last review
Main proposal — Civilization discovery journal: implemented.
Stable culture ids/lore back a read-only journal. Game persists actual garden-entry discoveries separately from expedition checkpoints, retains them on reset and supports missing art. No craft or route selection is introduced.

## Evidence
ui.test.cjs covers entry, checkpoint resume, reset, missing artwork and panel lifecycle; civilizations.test.cjs passes.
The integrated broker run passed (36 Python tests, four skipped, exit 0, unchanged tree), including all eight Node suites. Exact-byte pre-write reviews cleared the applied source; the additional Git gate returned CLEAR in .adversary/reviews/gate_20260916-121154.md and committed 18 source/test files.

## Scope and limits
This delta closes the main proposal from the prior feature review. Optional Nice-to-haves remain exploratory and unimplemented. This is not a new blanket bug/spec clearance. Live browser, physical-device and listening QA were unavailable because browser automation was refused by project policy. See docs/tasks/2026-09-16-emberline-features.md for shared validation and boundaries.
