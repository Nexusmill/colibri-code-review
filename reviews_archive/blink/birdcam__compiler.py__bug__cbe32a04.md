# colibri review — birdcam/compiler.py

- source: `birdcam/compiler.py`
- reviewer: in-session (zai-coding-plan/GLM-5.3-Flash), colibri-review v0.2.0 bug mode
- sha256: cbe32a04… (105 lines, bytes on disk at review time)
- date: 2026-09-05
- context pack: callers pipeline.compile_batches (find_ffmpeg/build_compilation/batch_id_for) and cli.check-setup; tests FakeCompiler + real-ffmpeg smoke run (3× testsrc clips joined, 10333 bytes, sha verified); blink_client.sanitize_component shared.

## Verdict

Small, single-purpose, and correct for its contract (stream-copy concat of same-camera clips);
no real defects found. The residual risks are inherent to the ffmpeg boundary and are already
shaped fail-loud.

## Bugs & vulnerabilities

None confirmed. Candidates examined and refuted in the adversarial pass:

- *"List-file path escaping breaks on apostrophes"* — refuted: `_ffmpeg_arg` uses the concat
  demuxer's documented `'\''` escape and forward-slash normalization; repo-local names are
  sanitized upstream, and Windows drive letters survive (`C:/...` is accepted by ffmpeg).
- *"Two clips with the same second collide"* — refuted at this layer: compile receives the
  stage-unique per-clip files; filename uniqueness was stage's responsibility and holds
  (clip id is in the name).
- *"Partial output accepted on failure"* — refuted: `returncode != 0` raises before hashing;
  a partial file can only exist alongside a raise, and the batch never records a sha for it.
- *Stream-copy codec mismatch across a day (camera firmware update mid-day)* — the one genuine
  residual: concat `-c copy` with mismatched parameters produces a broken file (or ffmpeg error).
  A ffmpeg error raises CompileError (loud, day skipped); a silent-parameter-mismatch file would
  fail YouTube processing later (batch failed, clips released, Blink kept). Fail-loud both ways —
  accepted residual, noted.

## Missing safeguards

- No duration sanity check on the output (a concat that silently drops all but the first clip
  would still "succeed"); a cheap guard is comparing output duration to the sum of
  `pts_length_ms` from clip metadata — noted as a future safeguard, not a current defect.
- `find_ffmpeg` runs `shutil.which` every call — harmless at this frequency.

Adversarial pass: all four candidates refuted against the bytes; the codec-mismatch residual is
labeled accepted-residual, not a finding.
