# BUG review: PatternSkin\__init__.py

- source: `C:\Users\User\source\repos\Nexusmill\PatternSkin\__init__.py`
- model: xiaomi/mimo-v2.6-pro
- reviewed: 2026-09-24 10:42
- tokens: in 186133 / out 60044
- est cost: $0.1332

---

## Verdict
Not safe to ship as-is for the selection/generator tooling: `sel_strokecut._cut` mixes **polygon** indices from `obj.ray_cast` with the **triangle** index space of `selectcore`'s MeshCtx, so "Split with a stroke" anchors its harmonic cut on the wrong triangles and can flip the kept side. The single biggest risk is that silent-wrong-geometry generators survived the R4 Nyquist pass in two places (`grip_pattern`/`generate_grip`, and the `res = max(0.3, pitch/4)` floor in both scale builders).

## Bugs & vulnerabilities

**[MEDIUM] `sel_strokecut._cut` indexes the triangle-space MeshCtx with polygon-space ray-cast indices** - `line 7041`
- What: `_raycast_pick_face` (6898) returns `obj.ray_cast()`'s **polygon** index (this is the same index space `ai_pick.modal` uses at 9037 — `int(pp[face])` with `pp` per-polygon). `_face_at` (7036–7037) hands that straight to `_cut(context, fa, fb)`, which then does `va = np.unique(ctx.F[fa])` (7041) and `if sel[fa] < 0.5: sel = ~sel` (7053). But `ctx = sc.get_ctx(key, V, T)` is built from **loop triangles** (`T`, `_sel_ctx` 6594–6604), so `ctx.F` is `(nt, 3)` and `sel = xf >= bestL` (7052) is per-**triangle** (confirmed by `_sel_write` 7703–6704 doing `np.add.at(acc, tp, tribool)` with `tp` = tri→poly). Every sibling operator converts correctly — `sel_clickcut` seeds with `_sel_seed()` = `np.where(psel[tp])[0]` (6606–6609) and indexes `ctx.F[seed]` (6993).
- Trigger: `patternskin.sel_strokecut` on any mesh with n-gons/quads (i.e. `nt > npoly`) — the polygon index is numerically a valid but *different* triangle index, so no exception fires; the bug is silent. Only an all-triangle mesh accidentally works.
- Impact: the harmonic field is pinned at the wrong triangles' vertices (both anchors wrong), and the "keep the seed's side" flip at 7053 is decided by a random triangle's value. The reported "Stroke Cut: N faces" is a plausible-looking but unrelated partition. `sel_clickcut`, `smart_select2`, `sel_region`, `sel_brush`, `sel_similar`, `sel_band` are unaffected.
- Fix: convert polygon → triangles once in `_cut`: `ta = np.where(tp == fa)[0]; tb_ = np.where(tp == fb)[0]` (guard `if not len(ta) or not len(tb_)`), anchor with `np.unique(ctx.F[ta].ravel())`, and orient with `if sel[ta].mean() < 0.5: sel = ~sel`. Better: make `_raycast_pick_face` return `(poly_index, tri_indices)` (via `me.polygons[face].loop_indices` + `loop_triangles`) so no caller can re-introduce the mismatch. Add a quad-mesh test asserting the cut's fixed-value side contains polygon `fa`'s triangles.

**[MEDIUM] `grip_pattern` / `generate_grip` sample the grip carrier at or below Nyquist — the third generator was missed by the R4 sampling fixes** - `line 1199`
- What: `grip_pattern(kind, count, size=512)` always rasterises on a **fixed 512×512** grid (`yy, xx = np.mgrid[0:size, 0:size] / size`, 1199) with `n = max(1, int(count))` cycles across it (1198, 1200). `generate_grip.execute` derives `count` from geometry with no cap and never raises `size`: `gn = max(2, int(round(s.grip_tile_mm / max(0.1, s.grip_pitch_mm))))` (4486). `grip_tile_mm` has `soft_max=80` but **no hard max** (1905) and `grip_pitch_mm` has `min=0.3` (1888). At `grip_tile_mm=80, grip_pitch_mm=0.3` → `gn = 267` → **1.92 samples per period**. `PYRAMID`'s `|(U*nu)%1 − 0.5|*2` (1186–1188) then lands on `{0,1}`; `KNURL_DIAMOND`'s two `nu+h` cosines (1167–1168) and `HEX`'s `pq=round(nu/2)`, `h=round(nv*0.866)` (1173–1177) reach ~500 cycles on 512 samples.
- Trigger: drag "Grip tile" to its slider top (80) and "Feature size" to its minimum (0.3), then "Generate grip texture".
- Impact: the generated seamless texture is aliasing noise / a constant, then silently becomes the active pattern and is baked as relief. This is the same "silent wrong geometry" class as the two R4 findings, and `res = pitch/4` / the 4-sample sleeve budget / the scale carrier clamp do not cover this path. The local 4-sample guards added at 4306/4353 and 4089–4091 make the inconsistency explicit.
- Fix: `grip_pattern(kind, count, size=max(512, int(math.ceil(4 * max(1, count) / 16.0)) * 16))` (derive `size` from `count`, ≥4 samples/cell per period), or clamp `n = max(1, size // 4)` and report the achieved feature count. Assert `size >= 4*count` in a harness sweep over `PS_GRIP_PRESETS` × the UI's tile/pitch corners.

**[MEDIUM] Scale knurl carrier is floored at `res=0.3`, so every pitch below 1.2 mm is silently rendered at ≥1.2 mm — the R4-2 `res=pitch/4` fix is incomplete** - `line 4306`
- What: `res = max(0.3, pitch / 4.0)        # 4 samples per feature period: Nyquist-safe knurl` (4306, and identically 4353). The comment claims 4 samples/period, but the `max(0.3, …)` floor makes `res = pitch/4` hold **only for pitch ≥ 1.2**. Below that, `nx = round(L/res) = L/0.3`, and the carrier clamp `nu = max(2, min(nu_want, (nx1-1)//4))` (4152) then caps `nu` at `L/1.2` — i.e. **every requested pitch in [0.3, 1.2) is forced to an achieved pitch of ~1.2 mm**. That covers the `PEN` (0.8) and `PRECISION` (1.0) presets and the whole `grip_pitch_mm` range under 1.2. Two further gaps: `ny` is capped at 360 while `nx` is capped at 500 (4307/4355), so the Y clamp can be strictly worse than X; and the operator's warning measures **only `nu`** — `_ach = s.scale_len_mm / nu` (4392, 4425) — so an `nv`-only clamp (e.g. `L=20, W=120, pitch=1.25` → `nu=16` unclamped, `nv=90` from 240, achieved 1.333 mm vs 1.25 mm) produces **no message at all**. The `_log.warning` at 4153–4155 is file-log only.
- Trigger: "Create blank pair" / "Scales from outline" with `grip_pitch_mm` in [0.3, 1.2), or a portrait outline (`W ≫ L`) with a fine pitch.
- Impact: knurls come out up to 4× coarser than asked and the warning misattributes it to "the grid cap" (the `nx<=500` cap is not what binds at `L=127`; the `res` floor is). `_print_reco` then evaluates a `grip_pitch_mm` that is not in the geometry.
- Fix: `res = max(1e-3, pitch / 4.0)` and let the 500/360 grid caps be the only ceiling (they are what the message already blames). Report **both** directions: `_ach_x = L/nu`, `_ach_y = W/nv`, warn with `max(_ach_x, _ach_y)` and name which axis clamped. Assert `ZT.ptp() > 0.5 * depth` **and** measured carrier period ≈ `pitch` for every `PS_GRIP_PRESETS` entry in both builders.

**[MEDIUM] `PATTERNSKIN_OT_lithophane` allocates O(res²) Python tuples with `litho_res` up to 2048 — multi-GB spike, no progress, no cancel** - `line 4692`
- What: `res = int(s.litho_res)` (4678) with `min=40, soft_max=800, max=2048` (2029–2030 — `max` is a *hard* Blender clamp, so 2048 is reachable by typing). The slab is built as raw Python object graphs: `verts` = `2*nx*ny` 3-tuples of freshly-created `float()`s (4692–4693) and `faces` ≈ `2*nx*ny` 4-tuples of `int`s appended in a nested Python loop (4696–4706), then `me.from_pydata(verts, [], faces)` copies it all again (4707). At `res=2048` on a square photo that is ≈8.4 M verts + 8.4 M faces ≈ **2.5–3 GB of transient tuples** plus the mesh itself. At the slider's `soft_max=800` it is already ≈350 MB.
- Trigger: set Resolution to 2048 (or 800) on a roughly square photo and press "Make lithophane".
- Impact: Blender's main thread stalls for tens of seconds to minutes with no progress bar and no Esc (the operator is a plain synchronous `execute`), and on a 16 GB machine the 2048 case can OOM-crash the whole session — taking the unsaved .blend with it. The property's own description ("hard cap: the slab allocates per cell") understates this.
- Fix: build `verts`/`faces` as numpy (`np.empty((2*nx*ny,3))`, `np.mgrid`-derived quad index arrays) and feed `from_pydata(verts.tolist(), [], faces.tolist())`, or lower `max=` to a value the builder can actually absorb (~800) and add a `vert_count > N` refusal with the honest maximum. Add a smoke test at `res=800` and `res=2048` measuring peak transient allocation.

**[LOW] `install_accel`'s "no pip flags" token filter accepts `.` and `..`, which pip treats as local build paths** - `line 3038`
- What: `if _tok.startswith("-") or not _re.fullmatch(r"[A-Za-z0-9_.\-]+(==[A-Za-z0-9_.\-]+)?", _tok)` is explicitly framed as the guard against a scripted `bpy.ops` call smuggling pip arguments past the index allowlist. `"."` and `".."` match `[A-Za-z0-9_.\-]+` and do not start with `-`, so they pass; `args += self.packages.split()` (3041) then becomes `pip install --target <modules> … .`, and `--only-binary=:all:` does not apply to a local project directory — pip runs its PEP 517 build backend / `setup.py`.
- Trigger: `bpy.ops.patternskin.install_accel(packages=".")` from a script or a third-party add-on, with Blender's CWD containing a buildable project.
- Impact: build-time code execution and a package installed onto `accel.ensure_dep_path()`'s import path, i.e. loaded into Blender on the next import. No privilege boundary is crossed (the caller can already run Python), but the control is advertised as a supply-chain guard and silently doesn't cover this case — the same failure mode R4-5 just closed for `index_url`.
- Fix: reject tokens that are not plausible distribution names — require the first character to be `[A-Za-z0-9]` (e.g. `re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.\-]*(==[A-Za-z0-9_.\-]+)?", _tok)`) and additionally refuse any token equal to `.`/`..`. Pin with a source assertion on the two tokens.

**[LOW] Config writes truncate in place — a crash or disk-full silently destroys every user preset** - `line 1356`
- What: `_save_user_presets` (1352–1357), `_save_license` (1414–1416), `_save_session_settings` (2263–2264) and `_save_forge_path` (4521–4522) all do `open(p, "w")` directly on the destination. `_user_presets()` (1319–1324) treats any parse failure as `raw = {}`, so a partial write is indistinguishable from "no presets". The codebase already documents and fixed exactly this defect class for STL export — `_stamp_stl_header` 1443–1448: *"atomic replace (PSK-11): truncating fp in place meant a crash mid-write destroyed the export"*.
- Trigger: crash / power loss / disk-full during "Save as new", "Update my preset" or "Activate / personalise" (all of which write on the main thread at the moment of the click).
- Impact: **all** user presets (or the license stamp) are gone with no error surfaced — `_user_presets()`'s `except Exception: raw = {}` swallows the corruption and the UI simply shows an empty preset list.
- Fix: reuse the `_stamp_stl_header` pattern — write to `p + ".ps_tmp"` then `os.replace(tmp, p)` — in all four writers. Test: inject a failure between the write and the replace and assert the previous file is byte-identical.

## Missing safeguards
- No `select_strokecut` (or `sel_clickcut`) test on a **quad/n-gon** mesh asserting that the cut's anchor triangles are the triangles of the clicked polygon — the polygon/triangle index-space bug is invisible on the triangle meshes most harnesses use. Enforce the convention at the API boundary: `_raycast_pick_face` should return triangle indices (or a named tuple), never a bare `int`.
- No sampling invariant in `grip_pattern`/`_grip_field`: assert `size >= 4 * count` (and `nu <= na // 4`, `nv <= nz // 4` for the sleeve, `nu <= nx // 4`, `nv <= ny // 4` for the scales) as a single shared pre-check with an honest "achieved pitch" message. Sweep `PS_GRIP_PRESETS` × `grip_tile_mm ∈ {0.5, 12, 80}` × `grip_pitch_mm ∈ {0.3, 1.5, 8}` and assert `ZT.ptp() > 0.5 * depth` and the measured carrier period within 10% of the request.
- `PATTERNSKIN_OT_lithophane` has no face/vertex budget check and no modal/progress path; `PATTERNSKIN_OT_grow`'s BFS (2956–2970) relies on `BMFace.index` without `bm.faces.index_update()`, so `seen` can collapse to `{-1}` and truncate the flood on meshes where indices aren't populated by `from_edit_mesh`.
- `_AI_SHADE_PREV` is keyed by `id(sp)` (8967) where `sp` is a possibly-transient RNA wrapper — a recycled address restores the wrong shading state, and the dict is never pruned when `_ai_overlay(on=True)` is called repeatedly. Key by `sp.as_pointer()` and clear the entry in `unregister()`. Same class: `_AI_PARTS_CACHE` / `_PS_AUTOLOAD_LAST` are keyed by `obj.name` (7076, 1104) even though `_ps_start` (562–563) explicitly rejects name keying because *"an Outliner rename mid-apply would defeat a name-keyed guard"*.
- `_ps_start`'s modal branch correctly claims `_PS_APPLY_BUSY` after the `wm`/`win` computation (568–573), but nothing re-asserts `obj` as active + Object Mode at the deferred execution points inside the modal gap: `_subdivide_stepwise`'s `bpy.ops.object.mode_set(mode="OBJECT")` (161) acts on whatever is active when the first `next()` lands, and `_apply_pattern_rest` writes `me.vertices.foreach_set` (445) and runs `bpy.ops.object.modifier_apply` (478) without re-pinning the target. `_apply_pattern_rest` already acknowledges this hazard for the shade op (450–453); extend the same scoping to 161/445/478, or disable `PASS_THROUGH` for selection-changing events while `self._ps_gen` is live.
- `PATTERNSKIN_OT_generate_default_library.execute` returns bare `{"CANCELLED"}` with no `self.report` when the manifest (5662–5664) or the Replicate token (5665–5667) is missing — reachable via `EXEC_DEFAULT`, which skips the `invoke()` pre-checks. Report and fail loudly like `invoke()` does.

## Fixed since last review
All eight round-4 items verified landed in the current bytes:
- **R4-1** `_write_3mf` interpolates `trs` (the XML built at 3561–3562) into the object template at 3564–3565 — the numpy `tris` array is used only to build `trs`. Refutation upheld; the 3MF round-trip pin stands.
- **R4-2** `res = pitch/4` plus the `nu`/`nv` carrier clamp and operator WARNINGs are present (4151–4155, 4306–4307, 4353–4355, 4392–4395, 4425–4428); `_extrude_scale_mask` now returns `(obj, nu, nv)`. (Residuals reported above as new.)
- **R4-3** Sleeve refuses unresolvable pitches with the honest achievable minimum instead of coarsening: `na = max(96, nu*4)`, `nz = max(48, nv*4)`, 1.2 M-vertex budget at 4090–4098 raising `ValueError` with `circ/_nu_cap` / `length/_nv_cap`.
- **R4-4** `semantic_finalize` is threaded behind a `finalize_wait` phase (8187–8204); `ai_parts_native` is re-phased `poll → fetch_wait → import → finalize_wait` with the download and `regranulate` on worker threads, the glTF import on the main thread behind an honest "importing…" tick (8365–8369), and the GLB removal deferred to `_cleanup_glb()` after the import consumes it (8340–8345, 8371–8377); `cancel()` also removes `_glb` (8499–8501).
- **R4-5** Non-allowlisted `index_url` now refuses with the refused host named rather than falling through to the default index (3031–3035).
- **R4-6** `_library_items`' empty placeholder uses the real identifier `"__none__"` (921), mirroring `_PS_NO_PRESET`.
- **R4-7** `_load_preset` filters `cfg.items()` through `_PRESET_KEYS` before `setattr` (5066–5068).
- **R4-8** `_ps_start` computes `wm`/`win` before claiming `_PS_APPLY_BUSY` (568–573), closing the claim-order strand.

---

## In-session verification + remediation (2026-09-24, round 5)

All 6 findings verified. Adversary gate round 5: APPROVE WITH MODIFICATIONS, folded in:
grip_pattern's derived size bounded at 8192 with clamp-and-log (my unbounded formula was a
new allocation vector); the scale carrier clamp made UNIFORM across axes (independent
clamps silently stretched the knurl) with both-axis operator warnings (outline included via
a.dimensions.y); the lithophane rebuild uses foreach_set buffers (from_pydata(lists) would
have re-materialized the exact tuple spike the fix exists to kill); the modal-gap deferral
was REBUTTED (the shade-op precedent demonstrably does not cover Edit-Mode-on-target during
the gap) and the cheap guard added (re-assert active+mode at the first deferred tick).

The probe then caught a REAL bug in my own rebuild before any scan did: the bottom-face
group dropped the +Nn vertex offset (bottom quads duplicated top indices) - found by the
adversary-demanded raw-tuple comparison, fixed, and now tuple-identical to the old loop.

Fixes: R5-1 strokecut poly->tri conversion (tp map, mean-orientation, missed-mesh guard);
R5-2 grip_pattern size=min(8192, max(512, ceil(4n/16)*16)) + count clamp + log; R5-3
res floor 1e-3 + uniform pitch_eff clamp + honest both-axis warnings; R5-4 numpy/foreach_set
lithophane (winding verbatim, +Nn corrected, ~0.5GB vs 3GB at res 2048); R5-5 pip token
PEP-503 grammar + explicit dot refusal; R5-6 _atomic_write_text for all four config
writers; promos: grow faces.index_update(), _AI_SHADE_PREV as_pointer-keyed + cleared on
unregister, gen_lib EXEC_DEFAULT failures report loudly, modal-gap active/mode guard.

Tests: tests/test_hunt_r5_fixes.py 17/17 PASS - quad-mesh strokecut anchoring (keeps fa,
cuts fb), grip grid derivation incl. a scripted 10M count (clamped, logged, 8192 grid),
uniform-clamp equality across axes, lithophane RAW-TUPLE equality vs the old loop at res 64
(+ heights at spot cells), pip grammar pins, os.replace failure injection (original
byte-identical), promo source pins. r1-r4 probes + smoke all re-passed. NOT COMMITTED.
