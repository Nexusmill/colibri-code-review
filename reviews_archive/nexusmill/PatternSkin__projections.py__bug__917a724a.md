# colibri-review — PatternSkin/projections.py — bug

- **Source:** PatternSkin/projections.py (C:\Users\User\source\repos\Nexusmill\PatternSkin\projections.py)
- **Model:** claude-opus-4-8[1m] (in-session, max) · cost $0.00
- **sha256:** 917a724a3f27cff353ca5818c1e81517f29ece1ac7d8f00e87aff3a55cbf2426 · 18,609 bytes / 358 lines, read end to end
- **Date:** 2026-07-23 · **Mode:** bug · first review of this file (extracted at 6c7bbfc, PSK-13 tranche 1)
- **Context pack:** jCodemunch outline (18 symbols) + the sole importer PatternSkin/__init__.py:61
  (re-exports all 18 names; `find_importers` reported 0 — it misses the relative-import re-export
  edge, an index gap, NOT dead code); both live call sites read (bake `apply_pattern` :197-219,
  live `_live_build` :1949-1956); `accel.nearest` contract (k>1 → (n,k) int64 nearest-first,
  raises on empty tree_pts); tile_mm/tile_mm_y FloatProperty bounds (min=0.5 / min=0.0);
  tests/test_projections.py (25 headless checks); remediation manifest (one row: the `math`
  import lost during extraction, fixed at 11bcc50); deferred manifest PSK-12/PSK-13 rows.
  Current on-disk bytes re-hashed at dispatch (G36). Findings verified by execution against
  the real module under asset-forge-user/.buildenv (Python 3.12, numpy 2.5).

## Verdict
Not shippable as-is for SWEPT3D. The kernels are carefully written — eps-guarded divisions
throughout, real fallbacks at every degenerate branch (`m < 4`, `len(path) < 4`, UV-without-layer),
a fixed RNG seed for determinism, and the PSK-12 shared dispatch genuinely removes the bake/live
drift it was built to remove. The single defect is in `_resample_polyline`: its smoothing
zero-pads at the array edges, which yanks the second and second-to-last skeleton nodes toward
the world origin and corrupts SWEPT3D's arc-length parameterization on **every** use. Measured on
a straight 20-unit tube: U spans 7.03 tiles where 4.00 is correct.

## Bugs & vulnerabilities

**[HIGH] `_resample_polyline` smoothing zero-pads the ends — corrupts every SWEPT3D projection** - `line 193` (`np.convolve(out[:, c], ker, mode="same")`), pinning at `line 194`
- **What:** `np.convolve(..., mode="same")` treats out-of-array samples as **zero**, not as the
  curve's own endpoint. With `smooth=2` the kernel is 5 wide, so the windows centred on index `1`
  and index `-2` each include one zero sample. Those two nodes are therefore averaged with the
  origin and dragged ~20% of their coordinate magnitude toward `(0,0,0)`. Line 194
  (`sm[0] = out[0]; sm[-1] = out[-1]  # pin endpoints`) shows the author anticipated an edge
  problem, but pins only indices `0` and `-1` — the two genuinely corrupted nodes are `1` and
  `-2`, which stay corrupted. In general `smooth=s` corrupts indices `1..s-1` and `-s..-2`.
- **Trigger:** every `project_swept3d` call — `line 288` calls
  `_resample_polyline(path, n_out=max(256, 3*len(path)), smooth=2)` unconditionally, and
  `len(out)=256 > k=5`, so the smoothing branch always runs. Severity scales with distance from
  the object origin, but it is never zero: a centreline centred on the origin still measured a
  26.7× spacing spike.
- **Impact (measured, not reasoned):** on a straight tube from x=10 to x=30 —
  · node `[1]` lands at `[8.05, 4, 4]` instead of `[10.04, 5, 5]`; node `[-2]` at `[15.95, 4, 4]`
    instead of `[19.96, 5, 5]`
  · segment lengths spike to **109× the median**; measured centreline arc = **23.23 for a
    10-unit path**
  · `_parallel_transport_frames` therefore starts from a **reversed** tangent
    (`T[0] = [-0.81, -0.41, -0.41]`, true direction `[1, 0, 0]`), so the transported frame carries
    an arbitrary rotation down the whole tube — the V seam lands at an angle that depends on where
    the object sits in space
  · end to end: **U spans 7.03 tiles where 4.00 is correct (76% too many repeats)**, with pattern
    slip up to **2.21 tiles** (11.1 object units), worst at the tail (2.09 tiles)
  User-visible as pattern smearing/compression at both ends of a SWEPT3D tube plus a wrong overall
  repeat count along it.
- **Fix:** replicate-pad before convolving so the ends smooth against the curve instead of against
  the origin:
  ```python
  padded = np.pad(out[:, c], (smooth, smooth), mode="edge")
  sm[:, c] = np.convolve(padded, ker, mode="valid")
  ```
  Verified: U span 7.033 → **3.925** (correct 4.000), max slip 2.211 → **0.072** tiles, spacing
  spike 3.2× → 1.2×. Both assertions the current suite makes on this function still pass
  ("resample returns requested count", "smoothing pins endpoints"), and no call site changes —
  `_resample_polyline` has exactly one caller, `project_swept3d:288`.
- **Verified:** CONFIRMED by execution against the current on-disk module.

## Missing safeguards
- **The unit suite cannot catch this class.** `tests/test_projections.py:115-121` *documents* the
  behaviour rather than testing it — "uniformity is only guaranteed at smooth=0" — so the uniform-
  spacing check runs with `smooth=0`, the path the product never uses. The remaining SWEPT3D
  checks are `isfinite` smoke tests (`:135`) and frame orthonormality (`:127`), and neither can
  fail on a corrupted centreline: orthonormality holds for any tangent, including a reversed one.
  Suggested additions: assert smoothed spacing stays within ~2× of median, and assert U is
  monotone and linear-in-axial-position on a straight tube.
- `project_swept3d`'s NN-walk (`:273-281`) can `break` early and silently use a truncated
  skeleton; only `len(path) < 4` is checked. Probed on both the unit test's helix and a 4×
  tighter coil — the walk completed 100% of nodes with max step 1.5× median in both, so this is a
  latent gap, not an active defect. Worth a warning if `len(order) < 0.9 * m`.
- `_estimate_tube_radius` retries `tree.query(..., workers=-1)` inside the k-loop, so on old SciPy
  the `TypeError` is raised and caught up to 68 times per call. Harmless, but hoisting the
  capability probe out of the loop would be cleaner.

## Refuted during verification (recorded so they are not re-raised)
- *"Zero `region_normal` collapses `project_planar` to a single point"* — both callers guard it
  first: `__init__.py:207` and `:1953` divert PLANAR to AUTO when `_nmag < _CLOSED_NMAG`.
- *"Empty selection reaches the kernels and raises `ValueError: zero-size array …`"* — the kernels
  do raise on empty input (confirmed), but `apply_pattern:89-94` flips `selected_only=False` when
  nothing is selected and `_live_build:1945-1946` falls back to the whole mesh, so `P` is never
  empty at any call site.
- *"Bake and live paths resolve PLANAR-on-closed differently (the 'crumpled cube' drift)"* — both
  now call the shared `_resolve_auto_mode` with the identical pre-check. The PSK-12 extraction did
  its job.
- *"`tile_mm = 0` divides by zero across every kernel"* — unreachable: every tile property is
  declared `min=0.5`.

---
**Status update (2026-07-23, same session):** the HIGH was FIXED after this review was filed —
replicate-padding at `_resample_polyline`, plus three regression checks in
`tests/test_projections.py` that fail against the pre-fix bytes (36× spike / 2.211 tiles slip /
7.033 span) and pass after (1.21× / 0.072 / 3.925). projections.py moved
917a724a → ee38e5df; see `docs/remediation_manifest.json`. The in-Blender SWEPT3D bake battery
has NOT been re-run — headless coverage only.
