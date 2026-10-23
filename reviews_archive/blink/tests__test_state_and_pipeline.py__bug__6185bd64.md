# colibri review — tests/test_state_and_pipeline.py (delta + test-quality hunt)

- source: `tests/test_state_and_pipeline.py`
- reviewer: ZCode in-session (GLM-5.3), colibri-review v0.4.0, bug mode, test-specific classes
- sha256: 6185bd649574cf5e8c01f0b8309d3f99c8c3d84ea08940dabdbe58daa9e5c35a
- date: 2026-10-05 04:50
- context pack: prior reviews 2a48b6a0 (hy4, 2026-09-19) + 0aba0cb8; delta 88eb139→c88d8b6
  (orphan adoption, songs-page description link, person-exclusion suite, hermetic unpublish tests
  per remediation 2026-09-23 row 3); contract sources pipeline/state/blink_client/cli/person_detect
  all reviewed this session.

## Verdict

new: 0. This is the suite's anchor file: the delete-safety machine (confirmation gating, hash
verification, missing-archive refusal, orphan adoption without re-upload, vanished re-post with
verified bytes) is locked in from every angle, and the takedown chain is tested end to end
including the resurrection guard.

Test-quality hunt results:

- Wire-level assertions, not just return values: DeleteEndpointCase records what delete_clip
  actually SENDS (exact v4 URL, reqtype, parsed media_list body, Bearer header) and pins the
  no-retry-storm property (auth.calls == 1 on 404).
- The two real-ffmpeg tests skip honestly when ffmpeg is absent and otherwise exercise the true
  duration/video-track contract — including a LYING-stats injection to prove the video-track gate
  fires (985-1024) and a staging_root pass on every production path with the NameError war story
  documented (1079-1081).
- Hermeticity verified where it once failed: the unpublish tests patch cli._store/load_config to
  temp fixtures with addCleanup (1522-1528) — the exact remediation for the 2026-09-23 live-state
  incident; the takedown suite asserts the note supersedes stale errors so retry --vanished cannot
  resurrect (1567-1579).
- Person-exclusion coverage matches the module's contract: excluded status + error text + local
  file removed + never in a batch + never deleted from Blink + audit frame requested under
  data/excluded_frames (1395-1422); detector load failure blocks ALL staging; dry-run reports
  broken detectors without raising or staging.
- Fakes inventory clean (FakeBlinkClient/FakeYouTube/FakeCompiler/StubPersonDetector with seam
  swaps restored via addCleanup); one manual try/finally restore in the description-link test is
  equivalent; no env leaks, no order coupling, no tautologies found.

Prior findings not restated.
