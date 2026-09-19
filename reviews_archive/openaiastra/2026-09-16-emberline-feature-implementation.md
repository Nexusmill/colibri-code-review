# Emberline feature implementation synthesis — 2026-09-16

This implementation closes all ten main proposals from .colibri_reviews/2026-09-16-emberline-feature-synthesis.md. Historical proposal reports are retained; current feature-mode delta reports are registered in _manifest.json with verified current source hashes. Optional Nice-to-haves remain unimplemented.

| Proposal | Feature | Outcome |
| --- | --- | --- |
| 1 | Held primary across inputs | Implemented; game.js |
| 2 | Primary upgrade progress | Implemented; engine.js |
| 3 | Narration ducking | Implemented; music.js |
| 4 | Independent silent captions | Implemented; voice.js |
| 5 | Flight manual and objective | Implemented; index.html |
| 6 | Encounter briefings | Implemented; gardens.js |
| 7 | Next shield packet forecast | Implemented; spectrum.js |
| 8 | Habitat terrain layouts | Implemented; terrain.js |
| 9 | Terrain readability overlay | Implemented; world3d.js |
| 10 | Civilization discovery journal | Implemented; civilizations.js |

## Integrated evidence
Gameplay commit 0eba7e0b2601 contains 18 source/test files. Automatic Git gate CLEAR: .adversary/reviews/gate_20260916-121154.md. All source mutations also passed independent exact-byte pre-write review. Final gameplay run: 36 repository Python tests, four skipped, exit 0, unchanged tree; the Node bridge successfully ran all eight Emberline suites. Route/resource validation uses actual terrain.move across 50 gardens and seeds 1, 42 and 1729. Tests cover primary boundaries and input cancellation, caption/audio separation, gain ducking, shield forecast parity, briefings, journal persistence and panel lifecycle.

## Corrections during implementation
Preserved existing lesson strings while adding accurate briefings; closed manual/journal on both begin and resume; aligned overlay filtering with default-solid and malformed geometry; cleared lost pointer capture and required gamepad trigger rearm after pause; removed inherited mobile width cap. Repaired opening shield-pickup placement and updated the stale HOME enemy-entry assertion to the newer no-camping contract while preserving full-black projectile vulnerability.

## Acceptance limits
Automated feature behavior is verified. Live browser appearance, physical touch/controller use, listening and human difficulty/retention are unverified because browser automation was refused. The offline ZIP is unchanged. This feature delta does not supersede historical bug/spec reviews or clear unrelated infrastructure gaps. Automatic archive delivery/readback remains unverified for this task. Full evidence and source release reference: docs/tasks/2026-09-16-emberline-features.md.
