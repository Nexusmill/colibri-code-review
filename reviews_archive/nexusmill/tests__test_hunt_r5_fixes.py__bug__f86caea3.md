# colibri bug review — tests/test_hunt_r5_fixes.py

- source: tests/test_hunt_r5_fixes.py · model: GLM-5.3-Flash (in-session)
- sha256: f86caea35b (full sha in manifest row) · reviewed_at: 2026-10-13 · mode: bug
- context pack: live execution (PASS, 0 failures, exit 0); "1e-3" occurrence census (2 in current __init__; the specific pin string present).

## Verdict
Clean behaviorally — the R5-4 lithophane tuple-for-tuple reconstruction is the series' most rigorous row. One weakened structural pin.

## Bugs & vulnerabilities

**[LOW] R5-3's source-pin fallback accepts any "1e-3" anywhere in a 9.6k-line file** - `line 66`
- Verbatim: `check("max(1e-3, pitch / 4.0)" in src.replace("res = ", "") or "1e-3" in src, "R5-3 res floor lifted to 1e-3 in source")`
- What: the `or "1e-3" in src` fallback makes the specific pin unnecessary — with 2 unrelated-plus-pin occurrences of "1e-3" in __init__, refactoring the actual floor expression away leaves the row green via the other occurrence.
- Trigger: the res-floor expression being renamed/restructured while any other 1e-3 tolerance remains.
- Producing caller: an edit to the `_build_scale`/grip res computation.
- Broken behavior: the structural pin silently stops pinning; the behavioral row above it still guards the outcome (hence LOW).
- Fix: drop the `or` fallback.
- Status: **CONFIRMED**.

## Missing safeguards
- None else; the R5-2 count ladder (8→8192 cap) and R5-6 atomic-write injection are sound.
