# ui.test.cjs — spec
Source: C:/Users/User/source/repos/OpenAIAstra/work/iris/ui.test.cjs
Reviewer: /root/dock_music (independent UI reviewer)
SHA256: c90d04305fe1042f84625ab73edf9f6a5b519442235c36e7fafd1cddcb5dc25b
Date: 2026-09-08
Mode: spec
Context: Iris task contract, current UI report/diffs, prior docking UI review, exact engine/terrain contracts, current voice integration API. Native indexed navigation context previously resolved; ignored exact candidates read directly.

## Verdict
CLEAR for this file’s observable contract.

## Divergences
None remaining.

## UNJUDGEABLE HERE
Actual browser frame rate and photographic visual acceptance require root browser fixture. Female clip/audio behavior lives in independently authored voice module and assets; this review does not self-review them.

Contract trace: Tests execute actual candidate game in a bounded DOM/canvas harness with real engine state constructors. They cover actual insertion routing, current/restored counts, trusted gestures, mute/visibility/pause, rings, photo texture crop and projected countdown boundary. New regression asserts restored/toggled Iris button state. Engine step and Canvas raster are mocked, so passing tests do not prove FPS or actual audio playback.
