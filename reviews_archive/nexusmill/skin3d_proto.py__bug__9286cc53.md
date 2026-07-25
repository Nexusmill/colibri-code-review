# Colibri review: skin3d_proto.py — bug mode

- **Source:** C:\Users\User\source\repos\Nexusmill\skin3d_proto.py (repo root)
- **Model:** claude-fable-5 (in-session, max)
- **sha256:** 9286cc5351c1c613cd2681d223f77d58034b6be01377b5e4e326e65564b995ee (9,535 bytes, re-hashed at dispatch per G36)
- **Date:** 2026-07-22
- **Mode:** bug
- **Context pack:** jCodemunch outline + find_importers (0 importers); repo-wide skin3d text search; PatternSkin twin symbols (projections.py:64 project_triplanar, heightmap.py tiling_score/make_seamless, __init__.py:72 apply_pattern); docs/AGENT_STATE.md tranche notes; docs/remediation_manifest.json (0 skin3d entries, G35 clean); GLM second opinion at same sha (junk/glm/skin3d_proto.py__glm52_high__9286cc53.md) consulted AFTER the in-session pass, each adoption re-verified. Every finding below verified by executing the actual staged module bytes (numpy 2.4.4, trimesh 4.12.2, Pillow) in the review container.
- **Prior reviews:** bug@6405bc71, quality/feature@bb41e92e — all stale shas; this supersedes the bug review.

## Role determination

**Dead prototype / manually-run dev CLI — not live code.** Evidence:
- jCodemunch `find_importers` → 0 importers; no production module imports it.
- `tests/` contains zero references to skin3d_proto.
- Docstring self-declares "STATUS: reference prototype - the production implementation lives in PatternSkin"; only mentions elsewhere are junk/ sweep scripts (v20_tools_verify.py, k3_final_verify.py) and review manifests. The similarly-named asset-forge/forge/skin3d.py is a different, live module.
- It IS kept deliberately runnable ("standalone CLI for quick experiments outside Blender") and was maintained through remediation tranche 7 ("skin3d round-2", AGENT_STATE), so it is a curated dev tool, not abandoned junk.

Severity weighting: nothing here ships; every finding is tool/documentation risk, not ship risk. Damien decides its fate.

## Verdict

Not shippable as what its first line promises — and it doesn't ship, so that is documentation/tool risk only. The single biggest risk: `apply_skin` breaks watertightness on any non-uniformly tessellated mesh (its own demo torus included) via T-vertices from selective subdivision, so the "REAL printable relief" prototype emits cracked STL with exit code 0; anyone using it for quick experiments, or treating it as the reference algorithm, inherits that flaw. The file is otherwise in good post-remediation shape: earlier K3/GLM-era findings (npy pickle RCE, NaN-to-STL, demo flag plumbing, arg validation) are genuinely fixed in these bytes.

## Bugs & vulnerabilities

**[HIGH] apply_skin destroys watertightness: selective subdivision leaves T-vertices, displacement opens them into real cracks** - `line 122`
- What: `trimesh.remesh.subdivide_to_size` subdivides only faces exceeding `max_edge`, producing hanging (T) vertices where refined faces meet coarser neighbors; `Trimesh(process=True)` (line 123) welds duplicates but cannot pair a half-edge with a full edge, and displacement (line 130) then moves each T-vertex off its neighbor's straight edge — a geometric slit per T-junction.
- Trigger: any input whose triangles need different subdivision depths, i.e. most real meshes. Reproduced with the module's own demo geometry: base torus watertight True → skinned False; amplitude=0 isolates the break to line 122 (edge-incidence histogram {2: 44640, 1: 576} — 576 boundary edges from subdivision alone). Uniform tessellations (box, icosphere) survive, which is why casual tests can miss it.
- Impact: cracked, non-watertight STL from the tool whose stated purpose is printable relief on "tubes/irregular parts"; demo prints "watertight: False" but still exits 0 and exports. Slicer behavior on such files is repair-dependent.
- Fix: subdivide uniformly — loop whole-mesh 1→4 `trimesh.remesh.subdivide` until the global max edge ≤ `max_edge_mm` (keeps conformity; budget check per iteration), or stitch T-junctions before displacing; at minimum, warn and return nonzero when a watertight input yields a non-watertight output. (Production PatternSkin displaces in Blender via BMesh and is unaffected — do not port anything back.)

**[MEDIUM] Generated tile is not y-periodic, but the sampler wraps v and asserts "the tile is periodic"** - `lines 27-48` vs `lines 70-71, 87-89`
- What: `make_scale_heightmap` row pitch `sy = 0.72/rows` does not divide 1.0, and the alternating half-column offset flips parity across the wrap; `_bilinear_wrap_sample` nevertheless wraps v as fully periodic (its docstring claims periodicity outright — the generator only claims x-wrap, "seamless-ish").
- Trigger: default usage. Measured on these bytes: rows=7 → y-wrap step 0.393 vs 0.047 max interior row step (8×); rows=18 (pitch divides exactly but 25 rows is odd) → 0.96. x-wrap is exactly seamless (0.0521 == interior), as designed.
- Impact: a ~0.24 mm ledge (0.393 × 0.6 mm default amplitude) repeating every `tile_mm` across every surface — a visible/palpable groove lattice on prints.
- Fix: make y truly periodic — choose `n = max(2, 2*round(rows/(2*0.72)))` rows and set `sy = 1.0/n` (even count preserves offset parity), or port the production seam fix (PatternSkin/heightmap.py `tiling_score`/`make_seamless`, added precisely for this).

**[MEDIUM] MAX_FACE_BUDGET guard under-estimates real face count ~10x** - `lines 117-121`
- What: `est_faces = mesh.area / max_edge_mm**2` ignores triangle geometry (a max_edge triangle has area ≈ 0.433·e², floor 2.31×) and subdivide_to_size's 4-way-split quantization overshoot.
- Trigger: any run near the budget. Measured: real/est = 10.04 at both max_edge 0.7 and 0.35 on a coarse box (ratio is tessellation-dependent; 2.3× is the geometric minimum).
- Impact: the "4,000,000 face" budget actually admits ~40M faces (multi-GB intermediate arrays, minutes of grind) — the guard's stated contract is off by an order of magnitude, and the error message's "~%d faces" misleads by the same factor.
- Fix: `est_faces = mesh.area / (0.108 * max_edge_mm**2)` (0.433/4), or enforce the budget inside an iterative subdivision loop where the true count is known.

**[LOW] Oversized heightmap images escape the CLI error net as raw tracebacks** - `lines 64-66` vs `line 191`
- What: `PIL.Image.DecompressionBombError` subclasses Exception, not OSError, so `except (ValueError, OSError)` misses it; `MemoryError` from a legal-but-huge image (float64 = 8 B/px) likewise.
- Trigger: `--heightmap` image beyond PIL's hard limit (~356 Mpx, e.g. a 20k×20k scan). Confirmed by executing `main()` on these bytes with the PIL limit scaled down: exception leaked uncaught.
- Impact: violates the file's own contract, stated on the very line: "CLI users get a message, not a traceback". Cosmetic-plus (the traceback does contain the reason).
- Fix: import PIL at the catch site and add `Image.DecompressionBombError` to the tuple (or wrap `load_heightmap` and re-raise as ValueError); optionally downsample tiles above a sane cap before float conversion.

**[LOW] --rows has a floor but no ceiling; tile build cost is O(rows^2) full-frame ops** - `lines 154, 160-161` vs `38-47`
- What: rows≥1 is enforced, but the dome rasterizer runs ≈ 4.2·rows² passes over the full N×N grid.
- Trigger: a fat-fingered `--rows 500`. Measured quadratic on these bytes: 0.34/0.98/3.48 s at rows 10/20/40 (N=256; ~4× at the hardcoded N=512) → rows=500 is hour-scale with zero feedback.
- Impact: apparent hang; inconsistent with the file's own guard philosophy (MAX_FACE_BUDGET exists for exactly this class on the mesh side).
- Fix: `ap.error` above a cap (64 is generous), or vectorize the per-dome loop.

**[LOW] Stale STATUS pointer: project_triplanar no longer lives in PatternSkin/__init__.py** - `lines 4-5`
- What: the docstring names `PatternSkin/__init__.py (project_triplanar/apply_pattern)` as the production home; `project_triplanar` was extracted to `PatternSkin/projections.py:64` in the PSK-13 god-module split (`__init__.py:61-65` merely re-exports it). `apply_pattern` is still defined in `__init__.py:72`.
- Trigger: a maintainer following the pointer greps a ~5,500-line file for an implementation that moved.
- Impact: documentation risk only — the twin map is this prototype's main remaining value, so the pointer should be exact.
- Fix: "production: PatternSkin/projections.py (project_triplanar) + PatternSkin/__init__.py (apply_pattern); tile loading/seam-fixing: PatternSkin/heightmap.py".

**[LOW] signed=True docstring overclaims: bounding-box growth is halved, not prevented** - `lines 99-100` vs `128-130`
- What: `h - 0.5` centers the range, so outward displacement still reaches +0.5·amplitude; "keeps mating faces from growing the bounding box" is false as written.
- Trigger: any signed run. Measured on these bytes: span growth 0.6 mm signed vs 1.2 mm unsigned (torus, amplitude 0.6).
- Impact: a press-fit face still grows +0.3 mm at defaults — wrong guidance for exactly the fit-critical use the sentence addresses.
- Fix: reword ("halves outward growth: relief spans ±amplitude/2 about the surface") or offer a true inward-only mode (`h - 1.0`).

## Missing safeguards

- No watertightness gate before export: the demo prints watertight True→False across apply_skin and still exits 0 — the one signal of the HIGH finding is displayed but never enforced.
- Negative `amplitude_mm` silently inverts the relief (only finiteness is validated, deliberately); harmless but undocumented — one help-text word ("negative engraves") would make it a feature.
- Very large parts with tiny `max_edge_mm` can hit subdivide_to_size's internal `max_iter=10` ValueError — caught, but the user-facing message ("max_iter exceeded") gives no guidance (unverified at runtime; API-known path).
- No unit tests reference this file (consistent with prototype role, but the twin-map claim in the docstring is then the only tested-by-nobody contract).

## Verification log (Phase 3)

- CONFIRMED ×7 above: all traced end-to-end by importing and executing the exact reviewed bytes (sha re-verified in-container) with numpy 2.4.4 / trimesh 4.12.2.
- Refuted and deleted during verification: point-cloud .xyz input crashing apply_skin (trimesh 4.12 loads it as an empty Trimesh; main's guard exits cleanly, rc=1); `trimesh.creation.torus` kwargs mismatch (accepted); GLM's "0-face mesh silently exports empty STL" (faceless OBJ loads empty, guard catches, no file written, rc=1 — does not reproduce on current trimesh).
- GLM second opinion (same sha): y-seam / rows-unbounded / budget-lower-bound independently corroborated (theirs adopted into mine with measurements); "uncaught exception types" adopted only in the narrowed, runtime-confirmed DecompressionBombError form.
