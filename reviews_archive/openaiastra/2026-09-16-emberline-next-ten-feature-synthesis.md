# Emberline — next-ten Colibri feature synthesis

Date: 2026-09-16
Reviewer: GPT-6 Codex /root
Mode: feature

## Scope and selection
The first ten reviewed units were the nine runtime JavaScript modules and index.html. Indexed inventory has exactly ten remaining text files in implementations/emberline: style.css, README.md and eight test suites. Each received its own current-byte feature review, with a separate adversarial reread and full source hash. None had a feature-mode cache entry. Runtime modules were supporting caller context, not re-reviewed as new units.

This is a feature recommendation run. No suggested add-on has been implemented and no gameplay/test source was changed. Existing main proposals from the first run remain implemented in source commit 0eba7e0; their documentation release is 9fc711e. Current source hashes and individual reports are in the canonical manifest.

## Ranked recommendations
Value and effort are estimates. S/M/L indicate relative implementation scope, not promises of elapsed time.

| Rank | Review unit | Main proposal | Value | Effort |
| --- | --- | --- | --- | --- |
| 1 | [ui.test.cjs](implementations__emberline__ui.test.cjs__feature__dcde5bfd.md) | Real-runtime integration lane | High | M |
| 2 | [style.css](implementations__emberline__style.css__feature__ba62c758.md) | Readable HUD and caption preset | High | M |
| 3 | [README.md](implementations__emberline__README.md__feature__3ec1099f.md) | First-flight walkthrough and recovery guide | High | S |
| 4 | [voice.test.cjs](implementations__emberline__voice.test.cjs__feature__a9f30ec6.md) | Controllable asynchronous audio fixture | High | S |
| 5 | [civilizations.test.cjs](implementations__emberline__civilizations.test.cjs__feature__e7d7c2b4.md) | Shipped-atlas audit and contact sheets | High | M |
| 6 | [engine.test.cjs](implementations__emberline__engine.test.cjs__feature__ef899e94.md) | Deterministic replay diagnostics | Med | M |
| 7 | [world3d.test.cjs](implementations__emberline__world3d.test.cjs__feature__2a54b94b.md) | Real-canvas scene gallery and cache parity | High | L |
| 8 | [spectrum.test.cjs](implementations__emberline__spectrum.test.cjs__feature__2dd26870.md) | Stateful shield scenario corpus | Med | M |
| 9 | [terrain.test.cjs](implementations__emberline__terrain.test.cjs__feature__7783e72c.md) | Route and clearance diagnostics | Med | M |
| 10 | [music.test.cjs](implementations__emberline__music.test.cjs__feature__a6972896.md) | Offline audio audition and measurements | Med | L |

## Cross-file findings and order
1. **Connect existing runtime behavior before adding more isolated assertions.** ui.test.cjs replaces engine.step and the music/voice schedulers. Unit tests already check the parts. An explicit real-runtime lane would exercise the event → caption → duck/restore path through game.js. Build the controllable voice promise/error adapter once and share it with that lane. This is a testing capability proposal, not a demonstrated production defect.
2. **Improve access to existing game information.** The CSS preset and README walkthrough build on the already implemented manual, silent captions and shield symbols. Preserve all 16 cells and sequential assigned-craft progression. Validate real layout/focus/zoom when browser access is available; static font sizes alone do not establish a usability failure.
3. **Make failures reproducible and explainable.** Engine replay traces, a bounded shield sequence corpus and route diagnostics can share a small fixture/report format. Keep deterministic seed/input capture separate from garden-entry checkpoints, which deliberately reset world transients. Reuse the existing 50-garden/three-seed BFS rather than duplicating it.
4. **Verify final assets and composition.** Civilization contact sheets inspect shipped PNG bytes; the real-canvas gallery inspects composed terrain pixels; offline audio excerpts inspect synthesized PCM. These complement the current fake-image/canvas/context tests. They need explicit optional backends and bounded scratch artifacts; do not silently enlarge the fixed default check dependency set or claim physical-device/listening acceptance from synthetic results.

## Existing coverage preserved in the recommendations
The current code already has all 50 garden route checks, exact MIDI asset parity, WAV format/duration/peak checks, caption-only gating, old onended cancellation, primary release/rearm tests, source-copy shield forecast parity, geometry/cache invalidation and missing-art fallbacks. None is reported as a newly missing feature. No route/craft selector, save-semantic replacement, production-store fixture write or change to combat balance is proposed.

## Uncertainty and exclusions
Confirmed labels in individual reports refer to inspected extension points and scope gaps. Player value, pixel tolerance, audio-backend feasibility and human readability/listening quality remain plausible and unmeasured. Historical browser evidence is not current visual QA. Nice-to-haves are explicitly secondary; they are not acceptance requirements for this review run. Bug/spec/quality verdicts are outside this feature pass.

## Artifacts and verification
Ten per-file reports retain line-level hook points, callers and refutation notes. The manifest keeps one absolute-path row per file and preserves existing modes. Its ten prior feature timestamps recorded as UTC strings are normalized to the equivalent America/Denver minute values to satisfy the current canonical format; source hashes and historical report references remain unchanged. Exact source/report/manifest readback, post-write checks and gated commit are the closing verification steps; outcomes are reported in docs/tasks/2026-09-16-emberline-next-ten-feature-review.md and the task response.
