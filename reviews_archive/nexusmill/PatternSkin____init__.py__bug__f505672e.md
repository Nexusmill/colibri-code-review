# BUG review: PatternSkin\__init__.py

- source: `C:\Users\User\source\repos\Nexusmill\PatternSkin\__init__.py`
- model: xiaomi/mimo-v2.6-flash
- reviewed: 2026-09-25 05:52
- tokens: in 202236 / out 63629
- est cost: $0.0461

---

## Verdict

Not yet safe to ship: the vertex-selection fix from the last pass left the **polygon** domain corrupted, so after any whole-mesh Apply the next seed-based selection tool reads every face as its seed. That is the single biggest new risk — it silently produces whole-model selections and, via `send_to_spector`, whole-model exports.

## Bugs & vulnerabilities

**[MEDIUM] Apply with `selected_only=False` restores only the VERTEX selection — the POLYGON/EDGE selection comes back fully set, corrupting every polygon-domain consumer** - `line 232`
- What: the write-back loop at lines 227–231 rewrites `v.select` only, then `bm2.to_mesh(me)` at line 232 flushes the bmesh face and edge selection unconditionally. With `selected_only=False` every vertex is tagged `True` (line 179), so the whole mesh is subdivided; `bmesh.ops.subdivide_edges` (line 211) replaces the faces, and newly-created BM elements are born selected — so the mesh comes back with essentially all polygon flags set. The comment at lines 224–225 justifies this by claiming *"the vertex domain is the one the pickers and region tools consume"*, which is false: `_sel_seed` reads `me.polygons.select` (line 7188), `PATTERNSKIN_OT_sel_facing` reads it at line 7452, and `PATTERNSKIN_OT_send_to_spector` reads it at line 9952.
- Trigger: any Apply where "Apply to this selection only" is off and `target_edge > 0` — unchecking the box, every `api_apply()` call (default `selected_only=False`, line 2514), and **every** "Batch apply to selected" run (line 5285 hard-codes `selected_only=False`).
- Impact: the next seed-based tool sees all faces as the seed, so `sel_region` / `sel_brush` / `sel_similar` / `sel_clickcut` / `smart_select2` return the whole model instead of the intended region, and `sel_facing` computes its reference normal from the average of every face normal. `send_to_spector` exports the entire mesh to Spector's inbox. The vertex-domain fix therefore only half-closes the defect reported last review.
- Fix: snapshot `me.polygons.select` and `me.edges.select` alongside `_ssel` before `bm2.from_mesh(me)` and write all three domains back in the same loop (new faces/edges forced off), or route the write-back through `_ps_apply_face_selection` so all domains are set from one mask.

**[MEDIUM] `_live_build` deletes the only copy of the tone-mapped tile even when `img.pack()` failed — the documented "silent zero displacement" outcome is guaranteed rather than avoided** - `line 3089`
- What: `img.pack()` is wrapped in `try/except: pass` (lines 3083–3086), and the enclosing `finally` at lines 3087–3091 unconditionally `os.remove(png)`. When pack fails, the image datablock is left unpacked with `filepath` pointing at a file that has just been deleted. The comment at lines 3084–3086 states the consequence itself: *"unpacked pixels die with it (.blend reopen -> missing image -> silent zero displacement at mid_level=0.0)"* — but the code still swallows the error and then removes the file, converting a recoverable failure into that exact outcome.
- Trigger: `img.pack()` raising during "Apply as live modifiers" — temp dir read-only, disk full, or the temp file already gone.
- Impact: the live relief works in-session (pixels are still buffered), then silently vanishes on save/reload: the Displace modifier with `mid_level = 0.0` (line 3129) evaluates a missing texture to zero, so the relief flattens with no error, no warning, and no way to tell why. This is data loss of the user's relief plus a silent failure.
- Fix: move `os.remove(png)` inside the pack `try` so it only runs after `pack()` returns successfully; on pack failure keep the temp file and `self.report({"WARNING"}, ...)` instead of `pass`.

**[MEDIUM] `send_to_spector` serialises the STL one triangle at a time in pure Python — minutes of uninterruptible main-thread work on scan-sized selections** - `line 9934`
- What: `_write_binary_stl` writes the 80-byte header and count, then runs `for i in range(len(tris))` performing one normal `struct.pack`, three vertex `struct.pack`s, an attribute pack and five separate `f.write` calls per triangle (lines 9934–9938). There is no chunking, no progress and no cancel path — the operator is non-modal (`bl_options = {"REGISTER"}`, line 9944).
- Trigger: "Send selection to Spector" on a large selection. The AI-parts flow that produces this button routinely yields millions of loop-triangles — and the first finding above makes it worse, because after a whole-mesh Apply `psel` (line 9952) is all-True, so `tri` becomes every triangle in the model.
- Impact: tens of seconds to minutes of frozen Blender with zero feedback and no Esc deliverable — the exact G-HANG-1 failure mode this file already fixed for `_ai_write_colors` (lines 9649–9653, *"the per-polygon Python loop froze the main thread for seconds on 1M+ face meshes"*) and for `finalize_job`.
- Fix: build the 50-byte records vectorised — fill a `(N, 50)` `np.uint8`/structured buffer from `nrm` and `tris` in one shot and issue a single `f.write`, mirroring the approach used in `_write_3mf` (lines 3988–3994); optionally add a triangle-count ceiling with a clear refusal.

## Missing safeguards

- No test asserts that an Apply with `selected_only=False` leaves `me.polygons.select` and `me.edges.select` byte-identical to the pre-apply snapshot — the restore at lines 227–231 covers only the vertex domain and nothing checks the other two.
- No test drives a seed-based tool (`sel_region` / `sel_facing` / `send_to_spector`) immediately after a whole-mesh Apply and asserts the seed is not the entire mesh.
- No test forces `img.pack()` to fail in `_live_build` and asserts the temp PNG still exists afterwards (or that a warning was reported) — the current `except: pass` at line 3085 is untested.
- No test exports a scan-sized selection through `send_to_spector` with a time bound, asserting the operator stays within a responsive budget.
- `_write_binary_stl` has no triangle ceiling comparable to `_check_3mf_ceilings` (line 3950), so there is no upper bound on the freeze.

## Fixed since last review

- **MEDIUM — Apply with `selected_only=False` silently selected every vertex**: `_subdivide_stepwise` now snapshots the original selection into `_ssel` (lines 174–175) and restores it on normal completion — `v.select = bool(_ssel[i]) if i < _n0 else False` for new vertices (lines 226–231) — instead of writing `v.tag` unconditionally. (The polygon/edge domain remains broken; that is reported above as a new finding.)
- **MEDIUM — `PS_PartPattern.tile` had `min=0.5`, silently clamping sub-0.5 part tiles**: now `FloatProperty(default=20.0, min=0.001, soft_min=0.01)` at line 1350, matching `region_tile_mm` / `tile_mm`, so `ai_assign_part` → `ai_bake_parts` round-trips small tiles unchanged.
- **MEDIUM — `ai_parts_count` / `ai_parts_active` never reset when the active object changed**: `_ps_autoload_tick` now clears them on every no-parts path — non-mesh active object (lines 1194–1199), no saved parts (lines 1221–1224), saved-but-unloadable (lines 1226–1229) and stale part map (lines 1232–1235) — and recomputes from the attribute when it exists (lines 1210–1219).
- **MEDIUM — the modal Edit-Mode guard forced OBJECT mode on whatever the user was editing**: now gated on identity, `if _eo is not None and _o0 is not None and (_eo == _o0 or _eo.data == _o0.data)` (line 723), so an unrelated edit session is left untouched and only the apply target (or a linked duplicate sharing its mesh) is forced out of Edit Mode.