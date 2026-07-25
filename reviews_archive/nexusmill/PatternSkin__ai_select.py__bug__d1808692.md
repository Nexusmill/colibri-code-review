# BUG review: PatternSkin\ai_select.py

- source: `C:\Users\User\source\repos\Nexusmill\PatternSkin\ai_select.py`
- model: moonshotai/kimi-k3
- reviewed: 2026-07-20 01:00
- tokens: in 5112 / out 2704
- est cost: $0.0559

---

## Verdict
Mostly safe to ship — no injection/auth/secret surface (pure NumPy geometry) — but the `look_at_basis` degenerate-vector handling is broken and can silently produce a garbage (all-zero) camera basis, which corrupts every downstream projection/mask lift without any error.

## Bugs & vulnerabilities

**[HIGH] look_at_basis degenerate fallback up-vector still parallel to forward** - `line 46`
- What: when `fwd` is (nearly) parallel to the default `up=(0,0,1)`, the code substitutes `up=(0,1,0)`. But if the camera happens to be positioned directly *above/below on the Y axis* (or the caller passes `up=(0,1,0)` already, which the API allows), `fwd` is parallel to the *new* up too. `np.cross(fwd, up)` is then ~0, `right` becomes ~0/1e-12 (a noise/garbage unit vector), and `true_up` inherits the garbage.
- Trigger: `look_at_basis(cam=[0, r, 0], center=[0,0,0])` — fwd = (0,-1,0), dot with default up is 0 (no fallback), fine; but `look_at_basis(cam=[0,0,r], center=[0,0,0], up=(0,1,0))` or any caller-supplied up parallel to fwd: dot = 1 > 0.999, fallback up = (0,1,0) which is *still parallel* → cross = 0.
- Impact: silently invalid camera basis → all projected points map to wrong/garbage pixels → SAM masks are lifted onto wrong faces; no exception raised.
- Fix: pick the fallback up as the axis *least* aligned with fwd, e.g. `up = np.array([0.,1.,0.]) if abs(fwd[1]) < 0.9 else np.array([1.,0.,0.])`, and raise if `np.linalg.norm(right) < 1e-9` after the cross product.

**[MEDIUM] look_at_basis silently returns zero basis when cam == center** - `lines 41-43`
- What: if `cam == center` (e.g. `fibonacci_viewpoints` called with `radius=0`), `nf = 0`, `fwd` stays the zero vector. `dot(fwd, up) = 0` doesn't trigger the parallel guard, `right = cross(0, up) = 0`, normalized by `+1e-12` to stay 0. Returns an all-zero basis.
- Trigger: `radius=0` in `fibonacci_viewpoints`, or any viewpoint coincident with `center`.
- Impact: every projection yields px/py = width/2, height/2 with z=0 → all faces "seen" at one pixel; mask lifting produces nonsense with no error.
- Fix: `if nf < 1e-9: raise ValueError("camera coincides with center")`. Also validate `radius > 0` in `fibonacci_viewpoints`.

**[MEDIUM] Unvalidated face indices in dual_edges cause silent corruption (negative) or crashes** - `lines 84-85, 105-106, 140-141, 238, 167-168`
- What: `dual_edges` is indexed straight into `L`, `comp`, `labels`, and Python lists (`adj[x]`). Negative indices silently wrap (NumPy/Python semantics), connecting the *wrong* faces; indices ≥ n_faces raise `IndexError` deep inside. The same applies if `face_view_label.shape[0] < n_faces`.
- Trigger: a dual graph built for a different/subdivided mesh, or a -1 sentinel leaking into the edge list.
- Impact: wrong adjacency → wrong part merges and splits; silent wrong results for negative ids, unhandled exception for out-of-range ids.
- Fix: after each `E = np.asarray(dual_edges).reshape(-1, 2)`, assert `E.size == 0 or (E.min() >= 0 and E.max() < n_faces)`; validate `L.shape[0] >= n_faces` in `lift_masks_to_parts`.

**[LOW] refine_parts_by_geometry early return violates the re-packed-labels contract** - `line 237`
- What: when `len(E) == 0` it returns `labels.copy()` and `labels.max() + 1` as the part count. If labels have gaps (e.g. only labels {0, 5} present, possible after upstream filtering), the count is 6 while only 2 parts exist — inconsistent with the "re-packs 0..k-1" contract the main path honors.
- Trigger: edgeless dual graph (single-face or disconnected mesh) with sparse labels.
- Impact: downstream operators allocating per-part data using the returned count see phantom empty parts.
- Fix: re-pack via `np.unique` in the early-return branch as well.

**[LOW] Small-fragment flood can silently drop faces to -1 forever** - `lines 255-259`
- What: components with `n < min_faces` are set to -1 and reflooded by `assign_unseen_to_parts`. If an entire connected region of the mesh consists of small fragments (or `min_faces` exceeds the whole mesh size), no neighbor is ever ≥ 0, the flood never assigns, and those faces come back as -1 — indistinguishable from "never visible" downstream.
- Trigger: `min_faces` large relative to part sizes on a small proxy mesh.
- Impact: faces silently excluded from the final selection.
- Fix: after flooding, if any -1 remain among previously-visible faces, iteratively lower the threshold or assign to nearest part by graph distance; at minimum document/log the dropped count.

## Missing safeguards
- No validation that `n_faces > 0`, that `face_view_label` is 2-D with `shape[0] == n_faces`, or that `dual_edges` is integral (`reshape(-1,2)` also raises an unfriendly error on odd-length input).
- `assign_unseen_to_parts` (line 170) has no iteration cap: correctness holds (labels only flip -1 → ≥0) but a defensive `max_iter` + assert would catch future regressions.
- `_otsu` / `_sdf_levels` assume non-empty input; `sd.min()`/`x.min()` on an empty array raises a bare `ValueError` — add explicit guards.
- No tests evident for: Y-axis-aligned camera (the basis fallback bug), cam == center, empty/gapped label sets in the `len(E)==0` path, negative edge indices, or the all-small-fragments flood case.