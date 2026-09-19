# Emberline next-ten implementation closure — 2026-09-17

Reviewer: GPT-6 Codex /root. This synthesis follows thirteen separate current-hash implementation/delta review units. It closes the ten main recommendations of the 2026-09-16 next-ten feature synthesis in source; optional browser and human acceptance remain distinct.

## Scope mapping
| Main proposal | Delivery | Evidence |
| --- | --- | --- |
| Readable HUD/captions | game.js, index.html, style.css | Saved preference/default/toggle/reload, 16 cells; optional browser lane skipped |
| First-flight recovery guide | README.md | Current controls/checkpoints cross-checked |
| Real-runtime integration | ui.test.cjs | Actual engine/music/voice dock/reset/caption/duck lifecycle passes |
| Controllable media | tools/emberline-audio-fixture.cjs, voice.test.cjs | Deferred rejection, old callbacks, synchronous failures pass |
| Atlas/contact sheets | tools/emberline-media-audit.js | Implementation CLEAR; pure measurement tests pass; real decoder unrun |
| Replay diagnostics | tools/emberline-diagnostics.cjs | Actual CLI generation/readback and first divergence pass |
| Canvas gallery/cache comparison | tools/emberline-world-audit.js | Seven actual-game scene fixtures implemented; pinned browser skipped |
| Shield corpus | tools/emberline-diagnostics.cjs | Mixed legal operations and earliest failing prefix pass |
| Route/clearance reports | tools/emberline-diagnostics.cjs, ui.test.cjs | One shared BFS across all 150 garden/seed cases; CLI JSON/SVG pass |
| Offline auditions | tools/emberline-media-audit.js | Real-clock OfflineAudioContext implementation; numeric PCM/WAV tests pass; rendering/listening unrun |

The browser page ties atlas, canvas and audio outputs together with current source hashes and browser metadata. tests/test_emberline_media.py pins an optional backend, retains bounded work artifacts, and exercises readable HUD persistence, native keyboard/focus and three CSS viewports when available. It does not install dependencies or use production profiles.

## Cross-file findings, ranked
1. Confirmed linked-output CLI defect was reproduced with an owned hard link under work. outputPath now uses lstat without existsSync and rejects existing nonregular/symbolic/multiply-linked targets. Regression failed first, then passed. This is not race-proof OS confinement.
2. Independent browser-test BLOCK identified ineffective CSS zoom coverage. The revised test removes the simulation and zoom claims, uses explicit CSS viewport sizes, and preserves real zoom as manual QA. Revised exact bytes received CLEAR.
3. Shared BFS extraction removes duplication while retaining all existing garden/seed coverage and opening-resource assertions. Actual media modules remain in the integration test; simulated hardware and real browser rendering have separate acceptance boundaries.
4. The optional pinned browser prerequisites are not satisfied here, so actual atlas decode, canvas capture, offline render and browser layout assertions did not run. Do not infer their success from source review or pure numeric measurements.

## Verification
After source changes, native run_checks: passed true, exit 0, unchanged tree; 37 repository tests in 49.304 seconds, five skipped. All nine Node suites passed through tests/test_emberline.py; the preceding unchanged test inventory had 147 tests, with only the subsequently fixed hard-link case failing. The conditional dangling-link branch can be unavailable on Windows and is not independently proven by aggregate success output.

Per-file reports name exact source SHA-256 values, current dependency contracts and validation limits. Canonical manifest rows preserve other modes and historical reports. Documentation review is not independent executable-code approval. Native writes required CLEAR before application; actual provider/fallback sequences inside reviewed_write are not readable through the broker.

## Release boundary
Earlier source tranche: 054e456d577c. This continuation adds the remaining audit tools, shared route use, CLI acceptance and the link correction. No gameplay runtime source changed in this continuation. Final post-record verification and automatic explicit-path Git commit follow; their actual result is recorded by the closing commit message and task response. Original unrelated untracked config/progression task are excluded. No push, ZIP rebuild, human device/listening QA or automatic archive byte-readback success is claimed.
