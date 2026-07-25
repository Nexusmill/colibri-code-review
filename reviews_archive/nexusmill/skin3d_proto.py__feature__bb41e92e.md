# FEATURE review: skin3d_proto.py

- source: `C:\Users\User\source\repos\Nexusmill\skin3d_proto.py`
- model: moonshotai/kimi-k3
- reviewed: 2026-07-19 19:43
- tokens: in 1627 / out 1283
- est cost: $0.0241

---

## What this module does
Displaces the vertices of an arbitrary mesh along its normals using a procedural heightmap (fish scales) sampled via triplanar projection — so no UVs are needed. It subdivides the mesh to a target edge length first so the relief has enough resolution, then exports STL.

## Suggested add-ons
Ranked by value:

**CLI + parameter configurability** - Value: High · Effort: S
- What: argparse entrypoint: input mesh path, output path, `tile_mm`, `amplitude_mm`, `max_edge`, `sharpness`, `rows`, tile resolution, optional custom heightmap image.
- Why: Right now everything is hardcoded in `__main__` (a torus at fixed sizes, one output path). No one can run this on their own mesh without editing the file.
- How: Replace the `__main__` block with `def main()` parsing args, calling `trimesh.load(args.input)`, then `apply_skin(...)`. Almost no new logic.

**Bidirectional relief + amplitude envelope** - Value: High · Effort: S/M
- What: Add `signed=True` (displace in/out around zero instead of only outward) and an optional vertex mask / spatial falloff (e.g. amplitude fades near a z-plane, or a painted region) so the skin doesn't cover the whole part uniformly.
- Why: Real products need grip texture on a handle *only*, or embossing that doesn't grow the bounding box on mating surfaces. Current code always bulges outward everywhere (`n * (h*amplitude)`), which also breaks flat mating faces.
- How: In `apply_skin`, center `h` (`h - 0.5`) when signed; accept `weight_fn(vertices) -> [0,1]` multiplied into `disp`. Weight function is a natural plugin point.

**Custom heightmap loading (PNG/npy) + pattern registry** - Value: High · Effort: S
- What: Accept any grayscale image as the tile; ship a small registry of procedural patterns (`scales`, `dimples`, `knurl`, `waves`) selectable by name.
- Why: Users think in "textures," not in this one fish-scale function. `make_scale_heightmap` is already a clean template for more patterns.
- How: `_sample` already works on any 2D array — just add `load_heightmap(path)` (normalize to [0,1]) and a `PATTERNS = {"scales": make_scale_heightmap, ...}` dict used by the CLI.

**Robustness: manifold/watertight checks and mesh validation** - Value: Med · Effort: S
- What: Validate input (watertight, no NaNs, volume > 0), report before/after stats (verts, faces, watertight, self-intersections via `trimesh.collision`), and optionally `process=True`/`remove_infinite_values` on load.
- Why: Displacement on a broken or non-watertight mesh silently produces unprintable STLs. The script prints `is_watertight` but never acts on it.
- How: Small `validate(mesh)` helper called in `apply_skin`; raise or warn; add logging (`logging.getLogger("skin3d")`) instead of bare prints.

**Adaptive subdivision / vertex budget guard** - Value: Med · Effort: M
- What: `subdivide_to_size` can explode a large mesh into tens of millions of faces. Add a `max_faces` cap, a warning with an estimated face count before subdividing, and optional region-limited subdivision (only near displaced regions).
- Why: Prevents the classic "ran for 20 minutes then OOM" failure; makes the tool safe on production meshes.
- How: Estimate via surface area / max_edge² before calling `trimesh.remesh.subdivide_to_size`; expose `max_faces` in `apply_skin`.

**Rotation/orientation control of the pattern** - Value: Med · Effort: M
- What: Allow rotating the triplanar frame (or scaling per-axis) so scales align with a part's axis instead of world XYZ, plus a `world_space` flag to bake the mesh's transform.
- Why: On a tube, scale direction relative to the part axis matters aesthetically; world-axis-only projection gives arbitrary orientation on rotated parts.
- How: Apply a 3×3 rotation to `points` (and inverse-rotate `normals`) at the top of `triplanar_height`; expose as `pattern_rotation` param.

**Metrics/logging observability** - Value: Med · Effort: S
- What: Log timings (subdivide, normals, sampling, displacement), mesh stats, and final volume change; optional `--report` JSON.
- Why: Subdivision dominates cost; users need to know why a run is slow and to sanity-check the result.
- How: `time.perf_counter` around the three stages in `apply_skin`, structured logging.

## Nice-to-haves
- **Seam fix for `h` normalization**: `make_scale_heightmap` normalizes by `h.min()/ptp`, which can differ per `rows`; expose `amplitude` normalization consistently.
- **Vectorized pattern gen**: the triple Python loop in `make_scale_heightmap` is O(rows²) NumPy calls — fine at 512, but document or vectorize for 2048+.
- **GLB/3MF export with the source mesh embedded** alongside displaced mesh for diffing.
- **Caching** of the subdivided base mesh (`v, f`) when sweeping amplitudes — re-running `apply_skin` re-subdivides every time.
- **Heightmap preview**: dump `tile` as PNG (it already saves `.npy` to /tmp) for quick visual iteration.
- **`sharpness` auto mode**: derive from curvature so blend regions shrink on high-curvature areas.
- **Unit handling**: assert/guess mesh units (`mesh.scale`) since all params are in mm.