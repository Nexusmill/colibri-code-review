# Colibri Review - bug (FULL re-audit, adversarial-era) - PatternSkin/projections.py

- **Source path:** `PatternSkin/projections.py` (blender_dev symlink twin, same bytes)
- **Reviewer:** glm-5.3 (ZCode in-session), Colibri G37 postures A-D
- **sha256 reviewed:** `7f78e7f9d26a5d3c77724e0fe0c7ede147b4e8bc43c819db9b969609131762ce` (sha8 7f78e7f9; 579 lines)
- **Date:** 2026-10-01 · **Mode:** bug, FULL re-audit (owner-ordered: the prior record 219e6368 is 2026-07-27 = pre-gate era and missed the 2026-09-10 core sweep)
- **Context pack:** file read end-to-end; prior record 219e6368 loaded (verdict then: shippable + one PLAUSIBLE numerical-bias note, low); both dedicated batteries run GREEN pre-pass (test_projections.py, test_projection_degeneracy.py); importers = __init__ (apply_pattern/_live_build) + filmstrip's import surface; every measured-rationale comment cross-checked against the code it justifies.

## Verdict
CLEAN at these bytes - shippable, no wave. The module is the best-documented code in the add-on: every threshold carries its measurement (1.4e10 cap angular dominance, 1.25-1.61% pole tears, 79x/96x UV distortion vs median 1.0, the U=7.03-vs-4.00 smoothing bug), the GROK-PJ3 empty-input guards are complete across every kernel (including the triplanar/planar/uv paths that lack an explicit guard but are empty-safe by array semantics - traced), and the historical averaging defect (per-vertex UV island boundaries) is documented in the code that has it, beside its shipped per-loop replacement.

## Bugs & vulnerabilities
None confirmed. None plausible-open.

## Adversarial verification pass (refuted candidates - recorded as calibration)
- "_frame_from_normal degenerates when n is near ±X" - refuted: the 0.9 branch sends near-±X normals to the Z reference; near-±Z (the X-reference branch) always crosses non-parallel.
- "empty P crashes the unguarded kernels (planar/triplanar/uv)" - refuted by trace: empty matmul/argmax/bincount paths all yield empty arrays without raising; the kernels with loops or reductions carry the explicit GROK-PJ3 guards.
- "_parallel_transport_frames crashes on a 1-node path" - true in isolation, unreachable: its only caller (project_swept3d) guards len(path) < 4 twice (pre- and post-resample) with the swept fallback.
- "spherical poles tear" - by design and documented; AUTO selects BALL (pole-free) for closed ball shapes; explicit SPHERICAL stays for recipe reproducibility (recorded decision).
- "tile_mm <= 0 divides to inf" - caller-guarded input space (UI minimums + _film_fit floors); same adjudication class as every prior audit of this file.
- "per-vertex project_uv averages island-boundary UVs" - the documented defect the per-loop project_uv_loops exists to replace; both shipped deliberately (different call paths).

## Notes
The 2026-07-27 record's single PLAUSIBLE note (numerical bias, low, unconfirmed) was never escalated by any later probe; nothing in this pass re-raises it. No remediation rows (nothing remediated); no deferred rows (nothing proposed). This record closes the projections.py assurance gap named in CODE_RATING_2026-10-01.
