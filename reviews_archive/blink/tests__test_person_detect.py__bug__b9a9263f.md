# colibri review — tests/test_person_detect.py (first review, test-quality hunt)

- source: `tests/test_person_detect.py`
- reviewer: ZCode in-session (GLM-5.3), colibri-review v0.4.0, bug mode, test-specific classes
- sha256: b9a9263f11300cc0a6c81a1ba1c76c943887d73be6b8576eb1fe5a3e2d07c979
- date: 2026-10-05 04:45
- context pack: never reviewed (born with 45d9ca0); contract source = person_detect.py (reviewed
  this session at 2065cd3d) + config validation; FakeSession/FakeCapture seam inventory.

## Verdict

new: 0. Strong contract tests with honest environment skips.

- Assertions are behavioral and can fail: the sampling-math test TRACES the real step arithmetic
  (10 frames @5fps, interval 0.5 → step 3 → samples 0,3,6,9; person_from_call=3 → frame 9 →
  t=1.8s) and asserts the short-circuit call count (124) — it would catch a step-arithmetic
  regression. The uint8-NHWC-RGB feed test asserts channel polarity through a lossy mp4
  round-trip with realistic tolerances (132-147).
- FakeCapture's hardcoded cv2 property ids (5=FPS, 7=FRAME_COUNT) verified correct.
- Skips are honest and precondition-probed: the chmod-unreadable test PROBES whether chmod had an
  effect before skipping (162-173) — on Windows it usually skips, which is disclosed, and the
  hash-mismatch test covers the same guard's other arm regardless.
- Fail-closed coverage is thorough: zero-decode, partial-decode, NaN/inf frame-count and fps
  fallbacks, count clamping, mid-scan session explosions → PersonDetectorError.
- Token-scope tests patch youtube_client.TOKEN_FILE with addCleanup — no global leak. One
  cosmetic wart: three config-validation tests live inside TestSessionOutputSafety (misfiled
  class, harmless).

Prior findings not restated.
