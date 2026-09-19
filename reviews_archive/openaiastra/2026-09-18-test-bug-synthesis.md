# Colibri test bug hunt — 2026-09-18

## Scope and verdict
Seventeen test/acceptance files accounted for: nine Emberline Node suites and eight Python files. Sixteen current-byte review units; terrain.test.cjs reuses its matching bug-cache record (7783e72c81cfc72277876c6c59ff0f199e59b1e03e6793c77c8f2f1cc1656699). Five source-confirmed test gaps across four files. Review only: no implementation repairs or mutation execution.

## Ranked cross-file findings
### T1 — MEDIUM: Snapshot indexing test can pass using only the archive row

tests/test_memory.py:158

The sync-boundary test asserts that any stored row contains cobalt and no row contains the replacement secret (lines 158–162). handle() independently archives the prevalidated original document after autoindex.sync returns (tools/memory_lifecycle.py:131–155). If sync silently does nothing, the archive still supplies cobalt and neither assertion detects the missing docs/calibration/section row. The patched callback is not asserted to have run either. Require callback invocation and a source-filtered docs row with the original content; check archive content separately.

Confirmed by tracing both row producers and the existential predicate. The source key docs/calibration/section is correct: canonical repo_memory/autoindex.py derives it from path.stem. This is source-level counterexample verification, not an executed mutation.

### T2 — MEDIUM: First-two-spawns regression never observes a spawn

implementations/emberline/engine.test.cjs:53

The test named 'every stage mixes enemies within its first two spawns' only checks new Set(g.types).size >= 2. spawnEnemy selects types separately using spawnCount modulo roster length (engine.js:300). A regression that always picks types[0] preserves every assertion in this test. Exercise two successful real spawns for each garden and compare their observed types against an independently chosen expectation; assert both spawns actually occurred.

Confirmed by tracing the current spawnEnemy implementation against the complete test body. Other engine tests exercise one spawn or roster differences after longer runs; none asserts the first two actual types in all 50 gardens. No production spawn defect is claimed.

### T3 — MEDIUM: Reachability acceptance omits all spectrum pickups

implementations/emberline/ui.test.cjs:300

The 150-case route test delegates its target set to routeReport and accepts every returned target. routeReport (tools/emberline-diagnostics.cjs:115–116) includes HOME, reset stations, ordinary embers and the rich patch, but no state.spectrumPickups. Therefore an opening shield pickup in an isolated clear pocket is never checked for connectivity. terrain.test.cjs checks collision clearance, which does not establish a connected route. Assert expected target identities/counts independently and include every opening spectrum pickup in the route acceptance.

Confirmed by the target-construction expression and caller. A disconnected but collision-clear spectrum pickup leaves the routeReport input fields it actually uses unchanged. This is a source-level omission; no existing generated unreachable pickup is claimed.

### T4 — MEDIUM: Focus-return test cannot detect missing canvas focus

implementations/emberline/ui.test.cjs:333

The test promises 'P still resumes with focus return', but only checks overlay.hidden. harness node.focus is an empty function at line 13 and document.activeElement is absent, so removing canvas.focus from game.js resume (line 101) cannot affect an assertion. Record focus in the DOM fixture, focus the summary before resuming, and assert focus returns to the arena. Keep native browser keyboard behavior as separate acceptance.

Confirmed by tracing KeyP to resume and reviewing every focus use in the harness. The optional browser test focuses the readable-HUD toggle; it does not test manual-to-arena focus restoration.

### T5 — LOW: Unclipped PCM assertion accepts positive full-scale saturation

implementations/emberline/voice.test.cjs:60

The WAV check takes abs(int16) and accepts peak < 32768. A valid-length PCM buffer filled with +32767 satisfies peak > 500 and peak < 32768, while -32768 is rejected. It therefore cannot support its stated unclipped claim for positive saturation. Check the signed positive and negative rails (or a documented symmetric near-full-scale threshold), ideally counting saturated runs; retain a synthetic positive-rail and negative-rail regression.

Confirmed directly from signed 16-bit endpoints and the exact assertion: 32767 > 500 && 32767 < 32768 is true. The media helper's float clipped counter does not validate these shipped voice WAVs. No claim that current audio assets are clipped.

## Cross-file assessment
The Node bridge includes all nine current suites and propagates failure. Optional installed-environment and paid-review lanes are explicitly skipped; requirements_gate.py is an intentional standalone audit. Source review found no additional confirmed defect in the remaining units. Synthetic DOM/canvas/audio fixtures do not prove browser focus, rendering or listening quality.

The memory deletion source-name suspicion was refuted against canonical autoindex.sync: source names use the filename stem, so docs/calibration/section is correct. The renderer audit deliberately reports pixel differences without a universal cross-backend threshold; this was not misreported as a failed equality test. Recent remediation entries were consulted and no closed defect was reopened as an implementation bug.

## Validation and limits
Native run_checks baseline: 37 Python tests, five skipped, exit 0, tree unchanged; includes the nine-suite Node bridge. Final post-record check and gated commit are recorded by the closing task/commit. All findings were verified by a separate source trace against current producers/callers; no runtime mutation was executed. Passing tests do not refute these oracle omissions. Optional browser/device/listening acceptance and current automatic archival byte readback remain unverified.

## Review inventory
- [tests/requirements_gate.py](tests__requirements_gate.py__bug__e8c26a58.md) — e8c26a584a500595d1491ebddf488fee6a2b92627431486b7c137c5eb99dfdc1
- [tests/test_automatic_review.py](tests__test_automatic_review.py__bug__34cc9eb4.md) — 34cc9eb486c115dd1dd1423f8bb27c3e0bcabd937216c9ac25cdc17f3547c526
- [tests/test_emberline.py](tests__test_emberline.py__bug__0ec964d0.md) — 0ec964d06d717d44913fdbeca4d5f42a0b28302b7067e6e2369c115ad352855a
- [tests/test_emberline_media.py](tests__test_emberline_media.py__bug__bd101196.md) — bd10119648d4ca52370a9e98640ef58ad43f395bdd4fc8a648efeedf4031fe76
- [tests/test_gate.py](tests__test_gate.py__bug__4afd8fd9.md) — 4afd8fd9eec0fdb12ee69ac8b7ce0cbea4ed3a5e229b5da90ebbbf902b85016a
- [tests/test_jcodemunch.py](tests__test_jcodemunch.py__bug__b33486cb.md) — b33486cbf31be52f82c54bd383662736628b7a4537c382652fe5db43fc7e9266
- [tests/test_memory.py](tests__test_memory.py__bug__b2643ab4.md) — b2643ab480e8df59f0112fb7e00b3509b73211abb9bd754cf8c6317a1936ea49
- [tests/test_observability.py](tests__test_observability.py__bug__cf58c658.md) — cf58c6589389249f10c5c95fda60a6f8d1bfaf8d05c461c89248128cd504c620
- [implementations/emberline/civilizations.test.cjs](implementations__emberline__civilizations.test.cjs__bug__e7d7c2b4.md) — e7d7c2b4c61ad78caa0802942b498bf71dc0d9dd7a55bd8494ced6a38a291fe7
- [implementations/emberline/diagnostics.test.cjs](implementations__emberline__diagnostics.test.cjs__bug__7f93b983.md) — 7f93b98312d64dc8c2aaaab4b32a5434f9866d0c10234fc9c7b433a8759ddb03
- [implementations/emberline/engine.test.cjs](implementations__emberline__engine.test.cjs__bug__ef899e94.md) — ef899e94e8d189318b4f91006fc9435e546f2eb6fcc3bac5193721c32894f0af
- [implementations/emberline/spectrum.test.cjs](implementations__emberline__spectrum.test.cjs__bug__2dd26870.md) — 2dd26870cb101cd11fe72375e24139314886ec033dbc99561237a0caf68c2d9a
- [implementations/emberline/music.test.cjs](implementations__emberline__music.test.cjs__bug__a6972896.md) — a6972896c35f7a4a13802b32dc55d5eedf9a1b9a7cd19841f760e3906ef0b061
- [implementations/emberline/voice.test.cjs](implementations__emberline__voice.test.cjs__bug__0a5f82ed.md) — 0a5f82edca0db71b26cf32880048d0da661ccb0f23c8cc63c101a197cc1bc235
- [implementations/emberline/world3d.test.cjs](implementations__emberline__world3d.test.cjs__bug__2a54b94b.md) — 2a54b94b70f645eecedd7467ecab1d4280f632cc2074dea0c790fc6e0d8fdd17
- [implementations/emberline/ui.test.cjs](implementations__emberline__ui.test.cjs__bug__a8ecdd2e.md) — a8ecdd2e8a1c971ab1fce052bafc870d85eaf7916080aeeef7b2cf3c50a47d95
- [implementations/emberline/terrain.test.cjs](implementations__emberline__terrain.test.cjs__bug__7783e72c.md) — matching cached bug review, unchanged SHA-256 above.
