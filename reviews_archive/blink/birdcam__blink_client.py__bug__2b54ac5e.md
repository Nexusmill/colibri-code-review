# colibri review — birdcam/blink_client.py

- source: `birdcam/blink_client.py`
- reviewer: tencent/hy4-preview via hy4-review headless CLI (rung M2)
- sha256: 2b54ac5eb284f56e  (bytes at review time = commit f04d93d)
- date: 2026-09-19 16:05
- mode: bug
- context pack: prior review f48357c5 (delta flow — non-200 media response and
  auth edges remediated in 572703b, not restated); person-exclusion invariant
  (exclusion happens in parse_clip_item BEFORE download); metadata flows
  stage() -> ClipRecord -> enricher composite.

## Verdict
No new defects in the delta (clip_metadata helper, ClipInfo.metadata field,
excluded_labels refactor). new: 0.

## Notes
- The refactor preserves the exclusion ordering and both metadata forms
  (dict / JSON string); the JSON-safety round-trip cannot change cv_detection
  semantics consumed by excluded_labels.
