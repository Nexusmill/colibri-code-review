# colibri review — birdcam/person_detect.py (first review, security hunt)

- source: `birdcam/person_detect.py`
- reviewer: ZCode in-session (account:zai-individual-coding-plan/GLM-5.3), colibri-review v0.4.0, bug mode, security lens
- sha256: 2065cd3d386027f72344673dcb9ef31eb189c37dd4b038b58cd0e37c1f0854c16
- date: 2026-10-05 04:05
- context pack: never stored before (born 45d9ca0 2026-09-23 after the person-leak incident —
  remediation_manifest entry 1); spec docs/superpowers/specs/2026-09-23-local-person-detector.md;
  live evidence: staging runs since 09-23 succeed through this gate (dynamic-input model verified
  working); consumer pipeline._person_exclusion_reason (reviewed this session); config pins the
  model sha256 (validated 64-hex, case-normalized).

## Verdict

The fail-closed contract is implemented at every layer and the privacy direction of every choice
is correct. No new findings; two design-level notes.

## Bugs & vulnerabilities (new findings only)

None CONFIRMED. Verified by trace:

- Fail-closed coverage: import failure, bad path type, missing file, unreadable file, sha mismatch,
  session load failure, input-tensor problems, output-tensor layout mismatch, per-frame analysis
  exceptions (converted at 141-154), zero-frame decodes, and short decodes (<90% of the container's
  promised frames) ALL raise PersonDetectorError — and the pipeline caller excludes on that error.
  No path returns "clean" without having actually looked.
- Model pinning: exact sha256 comparison before the model is ever loaded into a session (76-87) —
  a swapped/tampered model file cannot run.
- Box math for the audit-frame annotation (227-237) correctly maps TF OD API [y1,x1,y2,x2]
  normalized coords to pixel rows/cols (cosmetic-only consumer, verified anyway).
- Output-index clamping (168) prevents malformed-model outputs from overrunning arrays; empty
  outputs mean "no detections", correctly clean rather than error.
- The threshold comparison is inclusive (>=, line 170) — ties exclude, the fail-safe direction.
- The audit-frame directory IS created here (236) — resolving the open question left in the
  pipeline.py review about imwrite directory creation.

## Missing safeguards / design notes

- A person visible only between sampled frames can be missed by construction (0.5 s default
  interval) — this is the documented recall/coverage tradeoff of the sampling design, tunable via
  person_detection.sample_interval_seconds; recorded so it is a known bound, not a surprise. [INFO]
- A hypothetical NaN score compares False at 170 (treated as no-hit); NaN outputs would indicate a
  broken model rather than a crafted evasion, and every other failure mode of that class raises.
  Micro-note only. [INFO]

Adversarial pass: each fail-closed branch was individually traced; the inclusive-threshold and
clamping semantics were checked against the exclusion direction in pipeline.stage.
