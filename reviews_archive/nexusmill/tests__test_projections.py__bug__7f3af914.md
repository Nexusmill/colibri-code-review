# BUG review: tests/test_projections.py

- source: `tests/test_projections.py`
- model: claude-fable-5-1 (in-session, colibri-review protocol)
- sha256: `7f3af91456783b50181bc723a4c70e04ebb400aa78e0ef271fc1802cf5b29b16`
- reviewed: 2026-09-19 07:25
- mode: bug (test-unit hunt per the 2026-09-19 doctrine: tests are units)
- context pack: jCodemunch outline of projections.py (all 10 called signatures verified: project_planar/cylindrical/spherical/triplanar/swept/swept3d, _resolve_auto_mode, _dispatch_projection, _lattice_transform, _resample_polyline, _parallel_transport_frames); remediation rows 2026-07-21 and 2026-07-23 (this file caught both); git ls-files (results file tracked); live run 28/28.

---
## Verdict
Clean and load-bearing (it caught two shipped regressions in July). 28/28 live.

## Bugs & vulnerabilities
None confirmed.

## Missing safeguards
- `tests/test_projections_results.txt` (173-174) is git-tracked - same class as test_heightmap's results file; today's run produced identical bytes, so no drift observed (LOW note).
- `open(out, "w").write(...)` without `with` (174), LOW.

## External second opinions (grok-4.3, background)
- "import executes the suite and calls sys.exit" - not adopted: documented as a script (line 7), no pytest claim.
- sys.path / handle - LOW notes only.
