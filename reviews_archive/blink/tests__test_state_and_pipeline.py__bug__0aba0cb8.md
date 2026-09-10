# colibri review — tests/test_state_and_pipeline.py

- source: `tests/test_state_and_pipeline.py`
- reviewer: in-session (zai-coding-plan/GLM-5.3-Flash), colibri-review v0.2.0 bug mode
- sha256: 0aba0cb8… (472 lines, bytes on disk at review time)
- date: 2026-09-05
- context pack: all 22 tests pass live (run this session); fakes mirror the real client interfaces (FakeBlinkClient vs birdcam.blink_client, FakeYouTube vs youtube_client functions, compiler.build_compilation monkeypatched); production modules reviewed in their own units.

## Verdict

A genuinely behavioral battery — it covers the delete-guard machine, both upload modes, the
release-on-failure path, dry-run inertness, hash-mismatch blocking, and the metadata-as-string
regression — not a mirror test. No defects; two coverage gaps worth naming.

## Bugs & vulnerabilities

None confirmed. Candidates examined and refuted:

- *"Tests could pass while real clients drift from the fakes"* — partially true and inherent to
  the fake pattern; mitigated by the two live verifications this session (real-ffmpeg compile
  smoke; real dry-run through list/download-path code). Accepted residual, the colibri store
  exists to schedule those live passes.
- *"Midnight flake in day grouping"* — refuted: `timestamp_for` clamps to local midnight, and the
  held-back-today assertions compare calendar days, not hours.

## Missing safeguards

- No test exercises `pipeline.upload`'s max_uploads_per_run cap (truncation of the pending list)
  — one test with two batches and `max_uploads_per_run: 1` would pin it.
- No test for `clean`'s partial-failure path (fake `delete_clip` returning False on the second
  member → batch must stay confirmed, first member stays deleted, retry next run).
- CLI arg parsing (`--dry-run` before/after subcommand) is verified manually but not in the
  battery — a `build_parser().parse_args(["run", "--dry-run"])` row would pin the regression
  class that produced the launchers' first failure.

Adversarial pass: coverage-gap claims checked against the battery's actual rows; CONFIRMED as
gaps (safeguard-class, not bugs).
