# colibri review — tests/test_state_and_pipeline.py

- source: `tests/test_state_and_pipeline.py`
- reviewer: tencent/hy4-preview via hy4-review headless CLI (rung M2)
- sha256: 2a48b6a0d286b9e2  (bytes at review time = commit f04d93d)
- date: 2026-09-19 16:05
- mode: bug
- context pack: prior review 0aba0cb8 (delta flow); harness FakeBlinkClient /
  FakeCompiler / FakeYouTube; the delta is make_clip()'s new metadata parameter.

## Verdict
No new defects in the delta. new: 0.

## Notes
- Verified the default metadata dict cannot mask a previously covered
  missing-metadata path: pre-delta the fake Clip had NO metadata attribute at
  all, so no None-branch was ever exercised here (the None path is covered in
  tests/test_enricher.py). No assertion reads ClipRecord.metadata, so none was
  weakened.
- Post-scan addition in the same session:
  test_dry_run_upload_with_missing_archive_does_not_mutate_state (regression
  for the grok M3 pipeline finding).
- Scan-dispatch disclosure: two earlier dispatch attempts for this file timed
  out client-side (20 min each); the third completed in 133 s with the verdict
  above.
