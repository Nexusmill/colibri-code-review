# BUG review: tests/test_projection_degeneracy.py

- source: `tests/test_projection_degeneracy.py`
- model: claude-fable-5-1 (in-session, colibri-review protocol)
- sha256: `480c3b69c00b69673a13f24f55750cb12ba24d435b7d2223523721ad3fdf7b23`
- reviewed: 2026-09-19 07:25
- mode: bug (test-unit hunt per the 2026-09-19 doctrine: tests are units)
- context pack: contract source projections.uv_collapse_ratio (172-225: returns float(bad.sum())/float(real.sum())); _dispatch_projection signature; harness wiring bpy_patternskin.py:627-639 via probes/ps_proj_modes.py (PS-PROJ-PERLOOP / PS-PROJ-BALL); remediation row 2026-07-27 (the starburst fix this battery reproduces); live run all checks passed.

---
## Verdict
Clean: analytic fixtures, honest `main()` exit code, wired into the harness. All checks pass live.

## Bugs & vulnerabilities
None confirmed.

## Missing safeguards
- None material.

## External second opinions (grok-4.3, background)
- "exact `== 0.0` / `== 1.0` on `uv_collapse_ratio`" - REFUTED: the function returns `float(bad.sum()) / float(real.sum())` (projections.py:225), a ratio of integers - 0/n and n/n are exactly 0.0 and 1.0.
- sys.path - not adopted.
