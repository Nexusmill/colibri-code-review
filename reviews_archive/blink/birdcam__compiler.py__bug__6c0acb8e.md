# colibri review — birdcam/compiler.py (delta + security hunt)

- source: `birdcam/compiler.py`
- reviewer: ZCode in-session (account:zai-individual-coding-plan/GLM-5.3), colibri-review v0.4.0, bug mode, security lens
- sha256: 6c0acb8ea25996e1d737ce82c2f28ff86b62318653bbf36d4709d80c49b2ea0d
- date: 2026-10-05 03:55
- context pack: prior bug review cbe32a04 (2026-09-05, 105 lines — the file has since QUADRUPLED;
  the entire preflight/remediation wave 422caba→2344441 was gate-reviewed but never stored as a
  colibri artifact until now); callers pipeline.compile_batches + cli.check-setup + enricher
  (probe/find/_find_ffprobe reuse); Sep-6/8 incident classes per commit messages; smoke-test
  evidence in the prior artifact.

## Verdict

Clean under both lenses. The unreviewed wave implements exactly what its commit messages claim:
re-encode concat, dual duration gates (container AND video-stream), and a three-class pathological
preflight with an absolute floor plus a batch-median sparse reference that cannot be anchored by
its own liars (median computed over per-clip survivors only). Containment of remote-derived paths
is enforced at the concat-list sink, visibly and redundantly. No new findings.

## Fixed since last review

- The prior "missing safeguard: no duration sanity check on the output" is now implemented TWICE:
  container-duration gate (370-377) and video-stream gate (393-404), each with a
  max(5s, 2%) tolerance. Verified in current bytes.

## Bugs & vulnerabilities (new findings only)

None. Verified by trace:

- preflight arithmetic: zero-container-duration clips fall through `fdur > 0` guards to the
  stream-duration fallback consistently in both `_starved` and the exclusion loop (166, 187, 215);
  the redundant-looking packets==0 check at 216 exists to give a better reason string than the
  per-clip boolean — consistent, not conflicting.
- `_write_concat_list` (273-298): ensure_inside + an explicit second resolved-prefix check at the
  sink (289-294) — defense in depth on remote-name-derived paths; `duration` directives prevent
  the demuxer guessing from corrupt metadata; ffmpeg runs with `-safe 0` (required for the
  absolute paths the containment check just blessed).
- Temp list file lives in output.parent (inside the staging root by construction) and is unlinked
  in a finally (336-368); a failed ffmpeg leaves no batch record (sha computed only after both
  gates pass).
- `_find_ffprobe` sibling logic handles both bare names and .exe (54-66); a misconfigured bare
  ffmpeg_path still recovers via PATH lookup.

Adversarial pass: each gate's tolerance expression, the median-survivor reference construction
(198-207), and the concat-list escape function (unchanged, re-verified) were traced against the
bytes. Prior findings not restated.
