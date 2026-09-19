# Colibri Review - bug (DELTA) - PatternSkin/selectcore.py

- **Source path:** `PatternSkin/selectcore.py`
- **Reviewer:** claude-fable-5-1 (in-session), Colibri G37 protocol, campaign item 1 (product cores), rank 5
- **sha256 reviewed:** `2abcd247a910eb35b66c105aadf0dc96280b29beff8df0b751fd6fe826195f34` (sha8 `2abcd247`)
- **Date:** 2026-09-10 · **Mode:** bug, stale-file DELTA against `ab0edae1` (2026-07-24 round 2)
- **Delta reviewed:** 2 commits / 40 diff lines: 60bbde28 (GLM-POLISH `capability()` honest about no numpy fallback), 53e12489 (GROK-SC4 per-face orthonormal frame hoisted out of the SDF ray loop) - every hunk read.
- **Context pack:** the prior review record(s) for the file, `docs/remediation_manifest.json` rows from 2026-07-24 on, `docs/deferred_manifest.json` rows naming the file, `_hunt_plan.json` + `_refuted_ledger.json` loaded; jCodemunch `get_symbol_source` on the call sites each finding depended on.

## Fixed since last review
- Every remediation row dated after the base review was verified present at the bytes (they are the delta).

## Verdict
Clean at the delta. The hoisted frame is orthonormal for every normal: `t1 = cross(N, z)` normalised where it exists, the fixed x tangent where N is parallel to z (then `t2 = cross(N, t1)` is +/-y); the `np.where` broadcast is (nf,1) against (nf,3) and (3,).

## Bugs & vulnerabilities
None confirmed at the delta.

## Adversarial verification pass / notes
- SC-2 / SC-3 deferrals unchanged and out of scope.

---

# FULL re-audit 2026-09-10 (appended - the record above predates the adversarial gate and is kept as history, not as baseline)

# Colibri Review - bug (FULL re-audit) - PatternSkin/selectcore.py

- **Source path:** `PatternSkin/selectcore.py` (junction twin `blender_dev/addons/PatternSkin/selectcore.py`, same bytes)
- **Reviewer:** claude-fable-5-1 (fork of the lead session), Colibri G37 protocol, campaign item 1 (product cores), rank 5
- **sha256 reviewed:** `2abcd247a910eb35b66c105aadf0dc96280b29beff8df0b751fd6fe826195f34` (sha8 `2abcd247`) - the PRE-fix bytes
- **Date:** 2026-09-10 · **Mode:** bug, FULL review of the current bytes (owner ruling 2026-09-10: the 07-20..08-21 audits predate the adversarial gate and cannot be trusted - no delta against them)
- **Context pack:** all 420 lines read; every method's call sites in `__init__.py` read (`_sel_ctx` :6228, `sel_region`/`sel_brush` :6443-6457, `sel_similar`, `sel_band` :6477-6493, `sel_clickcut` :6613-6651, `sel_strokecut._cut` :6674-6689, the smart-select auto path :6399-6411) and in `ai_parts.py` (`proxy_sdf` :558, `relief_field` :794/:1173); the 5 remediation rows (07-20 stale-cache/validation/solver guards, 07-23 `_CTX` + `_geo_cache` bounds, GROK-SC4 frame, GLM-POLISH capability) each re-verified present at the bytes; deferred SC-2/SC-3 read. Numerical experiments run on the system SciPy 1.16.3: degenerate triangle, empty sources, disconnected shells, non-manifold edge.

## Verdict
One CONFIRMED defect in the product's paid selection core: geodesic distances on a mesh with more than one connected shell are finite on the shells the seed cannot reach, so Geodesic Grow and Edge Band select whole floating islands at an arbitrary radius. The Laplacian, heat factorisation, region grow, harmonic solve, SDF frame, Dijkstra path and the two caches hold; the remediated guards are all present.

## Bugs & vulnerabilities

**[HIGH] Geodesic distance is a finite number on unreachable shells - Grow / Edge Band leak onto floating islands** - `geodesic_verts` `line 170-176` (the `phi - phi[sources].min()` shift), consumed by `geodesic_faces` `line 178-182`
- What: the heat method solves `(W - 1e-8 I) phi = div`. On a component with no source, `u = 0` -> `X = 0` -> `div = 0`, and the regularised solve leaves `phi = 0` there; the shift `phi - phi[sources].min()` then turns that into `-min(phi at sources)`, a positive constant that scales with the seed shell's own span. Nothing marks unreachable vertices.
- Trigger: any mesh with two or more connected shells (blade + separate handle, kit-bashed parts, scan islands, a logo floating over a plate) and a selection tool that thresholds the field: `sel_brush` (`d <= sel_radius`, `__init__.py:6454`) and `sel_band` (`d <= sel_band`, :6490).
- Impact: measured - seed shell 30x30 (true far distance 42.8), separate island: every island vertex reads 22.5; a Grow radius of 22.5 selects 100% of the island and only 46% of the seed's own shell; seed shell 12x12 with a 40x40 island: the island reads 8.6, so a small grow takes 1600 faces the user never pointed at. The docstring at :6444 promises the grow "doesn't leak across gaps". Every scale of shell pairs tested shows the island constant ~= 0.52 x the seed shell's span.
- Fix: build vertex connected components once in `_build_topology` (`scipy.sparse.csgraph.connected_components` over the face-edge graph, stored as `self.vert_comp`), and in `geodesic_verts` set `phi[~np.isin(self.vert_comp, self.vert_comp[src])] = np.inf` after the shift (cache stores the inf field). Call-site check: `sel_brush`/`sel_band` compare with `<=` -> inf never selects; `geodesic_faces` means three same-component verts -> inf per island face; `sel_clickcut` (:6632) takes `far_v = argmax(dist)` and would now pick an island vertex as the far anchor, so it needs the companion one-liner `far_v = int(np.argmax(np.where(np.isfinite(dist), dist, -1.0)))` (same commit; `__init__.py` is the lead's unit). Probe `probe_ps_selectcore_1.py`: 4 of 5 checks RED at these bytes, 5/5 GREEN on a patched scratch copy; the connected-mesh check is unchanged.
- Verification: CONFIRMED (traced through the solve and measured at three shell-size ratios).

## Missing safeguards (not fixed)
- `harmonic()` on a multi-shell mesh: the free block of a shell with no Dirichlet constraint is exactly singular (`W 1 = 0`); SuperLU returned finite but arbitrary values in the experiment, so `sel_clickcut` / `sel_strokecut` include or exclude a whole unconstrained island by luck of the factorisation (PLAUSIBLE: unverified because the returned values depend on SuperLU's pivoting on the singular block; the isfinite check at :233 only catches NaN/inf). A one-line `sel &= np.isfinite(ctx.vert_to_face(dist))` in clickcut would close it once geodesic islands read inf.
- `sdf()` is a Python loop over faces (:269) - O(nf) interpreter time; pre-existing, perf only.
- `dijkstra_path` / `harmonic` numpy fallbacks are unreachable (the constructor raises without SciPy) - dead code, stale comments.

## Adversarial verification pass (refuted claims - deleted from findings)
- "A degenerate (zero-area) triangle poisons the cotangent Laplacian and the heat geodesics" - refuted numerically: a collapsed sliver gives `|W|max = 3.7e9` yet the geodesic field stays finite and within 0.3% of the clean mesh (42.68 vs 42.82 at the far corner); `features()` finite.
- "Empty source selections crash `geodesic_verts` / `region_grow`" - they raise `IndexError`, but every caller checks `len(seed) == 0` first (:6453, :6470, :6489, :6627); `_cut` receives ray-cast faces. Not reachable.
- "`_prep_heat` reuses a stale factorisation when `m` changes" - refuted: `_heat_m != m` rebuilds (:142) and the cache key carries `m`.
- "`get_ctx` returns a stale ctx after a retriangulation" - refuted: the signature hashes both V and F (:404-405).
- "`_geo_cache` returns a shared array the caller mutates" - refuted: `.copy()` on hit and on store.
- "Non-manifold edges (3 faces on one edge) break the dual graph" - the consecutive-pair scan links (f1,f2),(f2,f3) only; geodesics stay finite (tested) and the dual is still connected - a modelling quirk, not a defect.

## Remediation postscript (same session)
The fixes were applied after this review hashed the bytes above; the file is now `405019a7c3ad05e17cb0636035e56042ea2daa334e2beeb48783bfbd4d44a879`. Rows PS-SC-GEODESIC-ISLANDS in `docs/remediation_manifest.json`, same commit.

