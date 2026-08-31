Source: PatternSkin/projections.py
Reviewer: claude-sonnet-5 (in-session)
sha256: 219e6368e808f4e8c7de34b982e5934b827632e750b615bd6852589585171875
Date: 2026-07-27
Mode: bug
Context pack: full-file read; diffed 9a0ee6a..c2d2f34 (cap-aware project_cylindrical, new
project_uv_loops/uv_collapse_ratio/project_ball, loop_mask threaded through _dispatch_projection,
_resolve_auto_mode returning BALL); cross-read the call sites in PatternSkin/__init__.py
(apply_pattern, _live_build) and tests/test_projection_degeneracy.py's fixtures.

## Verdict
Shippable. This session's additions hold up under adversarial re-tracing (including the two
metric mistakes already caught and fixed earlier this session, whose corrected versions are what
sits on disk now). One PLAUSIBLE, unconfirmed numerical-bias note, low severity.

## Bugs & vulnerabilities
None confirmed.

**[LOW, PLAUSIBLE - unverified because it needs an asymmetric-topology mesh to observe]**
`project_cylindrical` / `project_spherical` / `project_ball` / `project_swept`'s internal
`c = P.mean(0)` and `span = P.max(0) - P.min(0)`, when called from the per-loop bake path, are
computed over per-LOOP points, not per-vertex or per-area. A face contributes as many points to
that mean as it has corners (a triangle: 3, a quad: 4, an n-gon: n), so a mesh mixing topologies
very unevenly - e.g. one large n-gon end cap next to a finely triangulated body - would pull the
computed centroid/span/axis pick slightly toward whichever region happens to have more loops per
unit area, rather than weighting by true surface area or unique vertex count. I could not trace a
concrete case where this flips an axis choice or visibly shifts a wrap on the meshes this product
actually targets (mostly uniform quad topology from box-modeling/subdivision); flagging as
PLAUSIBLE rather than CONFIRMED. Not worth fixing pre-emptively without a reproducer.

## Verified correct (traced, not flagged)
- **`project_ball`**: L1-normalisation + lower-hemisphere unfold traced by hand against the
  |u|+|v|=1 diamond parameterisation; the `low = n[:,2] < 0.0` branch's sign selection
  (`su`/`sv` from `n[low,0]`/`n[low,1]`) correctly reflects across the diamond's four quadrants.
  Scaling by `(pi * r_mean * 0.5) / tile_mm` matches the documented "arc length" intent.
- **`uv_collapse_ratio`'s cyclic `nxt` construction** (lines 183-192): requires `face_of` to be
  grouped into contiguous per-face runs in original loop-winding order. Confirmed this invariant
  survives boolean masking (`[loop_mask]`) upstream in apply_pattern, since masking preserves
  relative order and only removes elements — a face's surviving loops stay contiguous even under
  partial vertex selection. See PatternSkin/__init__.py's review for the follow-on trace of what
  happens to partially-selected faces specifically (verified harmless, not a bug).
- **`project_cylindrical`'s cap-aware branch** (`cap = np.abs(N[:, ax]) > CAP_DOT`): `N` is
  required and used as the per-loop FACE normal (never a vertex normal), matching the docstring's
  stated reason a shared-vertex normal would misclassify the rim.
- **AUTO's BALL/SPHERICAL split** (`_resolve_auto_mode`, `_SPHERE_SPAN_MIN` branch): returns BALL
  for the closed-and-round case, leaves explicit SPHERICAL selection untouched elsewhere in the
  dispatch table - confirmed `ps_recipe` back-compat is preserved since only the AUTO resolution
  path changed, not `project_spherical` itself.
