# Iris UI/world independent synthesis
All six exact candidate hashes in clearance.json match ui-manifest.json and have separate bug/spec/quality records (18 records). No production edits or commits. No self-review of voice source.

Independent command: node --test work/iris/engine.test.cjs work/iris/spectrum.test.cjs work/iris/terrain.test.cjs work/iris/world3d.test.cjs work/iris/ui.test.cjs
Result: 104 tests passed, zero failures; 93 engine/shield/terrain tests, 10 world tests, one UI test-file wrapper containing24 assertion groups.

## Fixed since last review
Iris mute feedback and projected top-edge countdown regressions confirmed against initial game hash b8ab07ae are fixed and behaviorally tested. Foundation overpaint is fixed by drawing base before textured organic faces. Sprite caching replaces repeated triangle rasterization on warm frames and is bounded64; damage/destruction/garden/texture readiness invalidate.

## Cross-file synthesis
Engine collision envelopes and actual player altitude feed geometry; conservative organic bounding boxes are documented. Per-pad count/dwell uses actual engine values. Voice receives present counts and simulation time plus actual dock/reset/insertion events, with trusted-gesture and pause/mute/hidden lifecycle. HTML dependency order and cache tokens match. Source contracts clear.

## Acceptance limitation
CLEAR_SOURCE is not browser acceptance. Parent reported initial2FPS/overpaint; code paths causing repeated rasterization and overpaint have changed and tests cover cache/order, but reviewer did not measure final real-browser FPS. Root must retain its real browser performance/appearance hold until verified. Node mocks cannot establish Canvas2D raster speed, visibility throttling, final textures, or actual voice playback.
