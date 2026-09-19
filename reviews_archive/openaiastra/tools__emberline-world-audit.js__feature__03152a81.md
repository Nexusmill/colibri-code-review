# Emberline feature closure: emberline-world-audit.js

Source: C:/Users/User/source/repos/OpenAIAstra/tools/emberline-world-audit.js
Reviewer: GPT-6 Codex /root, in-session Colibri review
SHA-256: 03152a81e1472dccfab0f89d857a616c20d1bb2e101f10dabd538d2cc33f70f3
Date: 2026-09-17 12:48 America/Denver
Mode: feature
Context pack: native current source/dependency reads, indexed outlines, next-ten synthesis and remediation/feature ledgers; source release 054e456d577c and this continuation.

## What this module does
Creates seven isolated deterministic iframe fixtures around the unmodified game.js draw pipeline; captures cache-off/cache-on/difference PNGs and numeric deltas (installFixture lines 4–35; auditWorld lines 36–67).

## Suggested add-ons
Implements the accepted real-canvas gallery: flyer/ground, damaged/broken terrain, underwater, reduced water and missing texture. Fixed seed/time/960×600/DPR1, real loaded image decoding, and captured back/front pass order retain the game's actor/water composition.

## Fixed since last review
New unit; native source CLEAR 5a07ad88337843debd49ae11194655c3. Runtime game.js and world3d.js are not edited for the gallery.

## Adversarial verification
Traced E.create/checkpoint/restore and World.draw callers. Fixture storage is an in-memory replacement, all canvas capture is same-origin, and the iframe is removed in finally. Missing texture explicitly passes null. Cache comparisons report differences without claiming a universal cross-backend threshold. Optional pinned-browser acceptance was skipped; actual scene capture and equality remain unverified.

## Nice-to-haves
Human review of occlusion and appearance remains separate from the implemented measurements.

## Verification boundary
Source was read back through the native exact-byte reader. The current source-check run passed (37 repository tests, five skips, exit 0, unchanged tree). Documentation clearance is separate from source clearance. Final post-record checks and the automatic explicit-path Git gate remain required. Cross-file closure: .colibri_reviews/2026-09-17-emberline-next-ten-closure.md.
