Source: PatternSkin/printfit.py
Reviewer: claude-sonnet-5 (in-session)
sha256: 4bde03a800f5876bc86b3e76c06136e1b313abc94b504fa9c832218d066c33e2
Date: 2026-08-06
Mode: bug (FIRST actual review - ranked #21 in _hunt_plan.json since 2026-07-24 but rounds:[]
i.e. never scanned; sha matches the plan's original seed_sha unchanged, confirming this)
Context pack: full 65-line file read; search_text confirmed callers: PatternSkin/__init__.py
imports print_check/slicer_notes/_print_reco directly; PatternSkin/filmstrip.py imports
_print_reco (marked `# noqa: F401` "kept for extensions", i.e. currently unused there); no
network, no file I/O, no bpy import - pure arithmetic + string formatting.

## Verdict
Shippable. Pure functions over caller-supplied floats; no I/O, no external input, no crash
surface beyond what a caller already controls (Blender's own bounded property sliders feed
depth_mm/layer_mm/nozzle_mm/tile_mm in __init__.py).

## Bugs & vulnerabilities
None confirmed.

Considered and not reported: print_check() computes its warning threshold as the raw expression
`2 * layer_mm` inline, while _print_reco() computes the same rule as `round(2.0 * layer, 2)` for
its returned min_depth. Both are gated identically (only active when layer/nozzle > 0). In an
IEEE-754 edge case where the rounded and unrounded values straddle a caller's exact depth_mm/
tile_mm, the warning list and the boolean depth_ok/tile_ok flags could theoretically disagree by
one ULP-scale amount, invisible at the 2-decimal-place precision both paths already display.
Could not construct a concrete diverging input in this session (no working shell to execute
Python this session - Bash tool is non-functional, verified via desktop-commander PowerShell
instead) to confirm or refute; the practical impact even if real is undetectable at the mm
precision this tool displays. Left unreported rather than shipped as an unverified "bug" per the
protocol's no-unverified-findings rule; worth a two-line unify-the-threshold-computation cleanup
if this file is touched again (compute min_depth/min_tile once, use in both print_check and
_print_reco) - logged as a LOW quality note, not a bug.

## Missing safeguards
None beyond the above.
