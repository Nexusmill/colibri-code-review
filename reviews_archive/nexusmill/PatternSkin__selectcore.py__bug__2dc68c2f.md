# BUG review: PatternSkin\selectcore.py

- source: `C:\Users\User\source\repos\Nexusmill\PatternSkin\selectcore.py`
- model: moonshotai/kimi-k3
- reviewed: 2026-07-20 00:55
- tokens: in 6934 / out 3295
- est cost: $0.0702

---

## Verdict
Not safe to ship as-is. The single biggest risk is the context cache in `get_ctx()`: it keys reuse solely on `(len(verts), len(faces))`, so any in-place mesh edit that preserves counts silently returns geometry, Laplacians, and solvers computed for the *old* mesh — every downstream selection is then computed on wrong data with no error.

## Bugs & vulnerabilities

**[HIGH] Stale cache: `get_ctx` signature ignores geometry/content** - `line 350`
- What: cache validity is checked only against `(len(verts), len(faces))`. Vertex positions, face ordering, and face content are ignored.
- Trigger: user edits a mesh in Edit Mode without changing vert/face counts (move verts, re-triangulate, weld), or a different object happens to share the same counts and cache key.
- Impact: `MeshCtx` (topology, cotan Laplacian, mass, dihedral, concavity, prefactored heat solvers) describes the old mesh. All selections (geodesic, region grow, harmonic cuts, SDF, auto-scenario) are silently wrong — the worst kind of failure for a selection tool.
- Fix: include a cheap content hash in the signature, e.g. `(nv, nf, float(V.sum()), float(V.var()), int(F[:min(nf,64)].tobytes().__hash__()))`, or require callers to pass a mesh version/pointer and document invalidation (Blender's `depsgraph` update / `mesh.update()` counter is the right hook).

**[HIGH] No index/face validation — silent corruption via negative or out-of-range indices** - `lines 31, 42, 117, 147, 186, 298`
- What: `faces` is never checked for being (nf,3), non-negative, or `< nv`; `source_verts`/`seed_faces`/`fixed_idx` are never bounds-checked. Negative face indices wrap silently (NumPy semantics) and produce a corrupt Laplacian/topology with no error.
- Trigger: degenerate input from importer (quads → only first 3 corners used, silently triangulating wrong), a -1 sentinel in faces, or seed indices from a stale selection after mesh edit.
- Impact: silently wrong geometry/operators (negative indices) or unhandled `IndexError` (positive OOB); empty `source_verts` reaches line 142 and raises `ValueError: zero-size array to reduction`.
- Fix: in `__init__` assert `F.ndim == 2 and F.shape[1] == 3`, `F.min() >= 0`, `F.max() < nv`; in each public method validate indices are non-empty and in range, raising a clear `ValueError`.

**[MEDIUM] Singular-solve silent failure in `harmonic`** - `lines 186-192`
- What: if `fixed_idx` is empty, `Wff` is the full (singular) cotan Laplacian. `spsolve` emits only a `MatrixRankWarning` and returns a vector of `nan`, which propagates silently into `x` and downstream cutting logic.
- Trigger: caller passes an empty constraint list, or all constraints lie on a disconnected component.
- Impact: NaN field, garbage cut levels, no error surfaced to the user.
- Fix: `if len(fixed_idx) == 0: raise ValueError(...)`; check `np.isfinite(xf).all()` after the solve and raise otherwise.

**[MEDIUM] Heat solver caches factorization keyed only on "built once", ignoring `m`** - `lines 102-116`
- What: `geodesic_verts(..., m=...)` only calls `_prep_heat(m)` when `self._heat is None`. A second call with a different `m` reuses the factorization for the old `t = m·h²` — wrong diffusion time, wrong distances.
- Trigger: two tools (or a UI slider) calling `geodesic_verts`/`geodesic_faces` with different `m` on the same ctx.
- Impact: silently incorrect geodesics for every call after the first.
- Fix: store `(m, t)` and rebuild when `m` changes: `if self._heat is None or self._heat_m != m: self._prep_heat(m)`.

**[MEDIUM] `dijkstra_path` returns a bogus path when dst is unreachable** - `lines 255-258`
- What: scipy marks unreachable nodes (and the source) with predecessor `-9999`. If `dst_face` is unreachable from `src_face` (disconnected mesh — common with boundary/non-manifold duals), the while loop exits immediately and the function returns `[dst_face]` — a "path" that does not start at the source.
- Trigger: src and dst on different connected components of the dual graph.
- Impact: caller treats `[dst]` as a valid path; boundary-snap feature silently misbehaves.
- Fix: check `np.isfinite(dist[dst_face])` (or `pred[dst_face] == -9999 and dst != src`) and return `[]`/raise; also assert final `path[-1] == src_face` after reversal.

**[LOW] Non-manifold edges produce incomplete dual graph** - `lines 55-58`
- What: for an edge shared by 3+ faces, consecutive-equal detection pairs only `(f0,f1)` and `(f1,f2)`, missing `(f0,f2)` — the dual graph, dihedral, and concavity are incomplete.
- Trigger: non-manifold input meshes (common in imported CAD/game assets).
- Impact: region grow/cut leaks or stalls unpredictably across such edges.
- Fix: detect runs of `same` length > 1 and either emit all pairwise combinations or raise/warn that the mesh is non-manifold.

**[LOW] Dead/unused Rodrigues rotation code in `sdf`** - `lines 222-225`
- What: `v = np.cross(z, tgt)` and `c = tgt @ z` are computed and never used; the code then uses a different tangent-basis approximation. Also `_unit(np.cross(N, [0,0,1]) + 1e-6)` picks an arbitrary, near-random tangent for normals parallel to z (cross ≈ 0), making ray directions for those faces effectively random per mesh.
- Impact: misleading code; SDF sampling for horizontal faces is inconsistent (mitigated by fixed rng seed for cone angles only).
- Fix: delete the dead lines; for `N` near ±z choose `[1,0,0]` as the reference axis explicitly.

**[LOW] Unsynchronized global cache and lazy mutation** - `lines 37, 115-116, 342-355`
- What: `_CTX` and the lazy `_prep_heat` mutation have no locking. Two threads building/prepping the same key can double-factor (wasted memory/CPU) or observe a half-initialized `_heatA`/`_heatL` pair (interleaved assignment between lines 106 and 111).
- Trigger: Blender operators or a background modal calling into `selectcore` concurrently.
- Fix: guard `get_ctx` and `_prep_heat` with a `threading.Lock`, or document single-threaded use.

## Missing safeguards
- No validation that `verts` is (nv,3) and finite; NaN vertices propagate through the Laplacian into NaN solvers with no error.
- No finite/success checks after `factorized` (line 106-107): on a degenerate mesh these raise `RuntimeError` mid-operator with no user-friendly wrapping, or worse produce NaN solves.
- No handling for `nv == 0` / `nf == 0` (line 47 `np.mean` of empty → NaN `h`, line 142 `.min()` on empty).
- `sdf` (line 230) doesn't guard against the `raycast` callback raising or returning NaN/negative distances; only `np.isfinite` filtering exists, and `len(row) >= 3` hard-codes a threshold that silently yields NaN faces when `n_rays < 3`.
- No tests evident for: stale-cache invalidation, empty/disconnected meshes, non-manifold edges, negative face indices, singular harmonic systems, or `dijkstra_path` on disconnected components — these are exactly where the defects above live.