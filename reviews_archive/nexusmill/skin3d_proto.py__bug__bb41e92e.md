# BUG review: skin3d_proto.py

- source: `C:\Users\User\source\repos\Nexusmill\skin3d_proto.py`
- model: moonshotai/kimi-k3
- reviewed: 2026-07-19 19:41
- tokens: in 1670 / out 2008
- est cost: $0.0351

---

## Verdict
Not shippable as-is, though this is a single-user prototype so blast radius is limited. The biggest risk is silent numeric corruption: invalid parameters (`tile_mm=0`) or NaN/degenerate geometry propagate through NumPy without raising, producing a garbage STL that exports "successfully."

## Bugs & vulnerabilities

**[MEDIUM] `tile_mm=0` (or NaN inputs) silently produces corrupted geometry instead of failing** - `line 33` (with `line 26`)
- What: `points / tile_mm` with `tile_mm == 0` yields `inf` (NumPy warns, doesn't raise). Then `inf % 1.0` → `nan`, `np.floor(nan).astype(int)` → undefined platform-specific integer (typically `INT64_MIN`), and `% W` maps it to a valid-but-wrong index. No exception is ever raised.
- Trigger: calling `apply_skin(mesh, tile, tile_mm=0.0)`, or a mesh containing NaN vertices/normals (degenerate input), or a tile containing NaNs.
- Impact: exported STL contains arbitrary garbage displacement while the script reports success — worst kind of failure for a print pipeline.
- Fix: validate `tile_mm > 0` and `np.isfinite(tile).all()` up front; add `assert np.isfinite(disp).all()` before export in `apply_skin`.

**[MEDIUM] Zero-length normals make the relief silently vanish or go NaN** - `line 38`
- What: `w.sum(axis=1)` is 0 for vertices whose averaged normal is the zero vector (possible on certain symmetric/degenerate geometry after subdivision+merge). The `+ 1e-9` guard prevents a crash but yields weights ≈ 0, so those vertices get ~zero displacement with no indication.
- Trigger: meshes where opposing face normals cancel at a vertex, or NaN normals from degenerate faces (`trimesh` emits NaN normals rather than raising).
- Impact: holes/flat patches in the relief, or NaN vertices in the output mesh; `is_watertight` on line 58 won't catch NaN.
- Fix: after line 45, do `n = np.nan_to_num(n); bad = np.linalg.norm(n, axis=1) < 1e-12; n[bad] = [0,0,1]` (or drop/flag those vertices).

**[LOW] Unbounded mesh densification — memory blowup / DoS on large inputs** - `line 43`
- What: `subdivide_to_size` with `max_edge=0.7` subdivides every face until all edges are below the threshold. A large input mesh (or a small `max_edge` passed by a caller) explodes face count by up to 4× per iteration with no cap.
- Trigger: any large mesh, or `max_edge` set tiny relative to mesh scale.
- Impact: RAM exhaustion / hung process. For a library-grade function this is a resource-exhaustion vector.
- Fix: cap iterations or total face count (e.g., raise if `len(f)` would exceed a budget), and validate `max_edge > 0`.

**[LOW] `process=True` on the displaced mesh can merge near-coincident vertices** - `line 48`
- What: `trimesh.Trimesh(..., process=True)` runs `merge_vertices` with default tolerance. After displacement, vertices displaced to within the merge tolerance get welded, silently altering the relief and potentially creating degenerate faces.
- Trigger: small `amplitude_mm` relative to `max_edge`, or fine tiles where adjacent displaced vertices converge.
- Impact: subtle geometric corruption of the pattern.
- Fix: pass `process=False` on line 48 (geometry is already clean from line 44) and validate explicitly instead.

## Missing safeguards
- No validation of any `apply_skin` inputs: `mesh` (None / empty vertices), `tile` (2-D? non-empty? finite?), `tile_mm > 0`, `amplitude_mm`, `max_edge > 0`.
- No finiteness check on the final `disp` array before export — NaN would be written straight into the STL.
- No error handling around `subdivide_to_size`, `export`, or `np.save`; a failure mid-script leaves partial files with no message.
- Hardcoded absolute output paths (lines 59–61) with no existence/permission check; `/tmp/tile.npy` is world-writable-location dependent.
- No tests at all — at minimum: known-input test for `_sample` (bilinear interpolation correctness at wrap boundaries), watertightness/finiteness assertion after `apply_skin`, and rejection tests for `tile_mm=0` and NaN inputs.