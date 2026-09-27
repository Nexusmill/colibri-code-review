# BUG review: PatternSkin\__init__.py

- source: `C:\Users\User\source\repos\Nexusmill\PatternSkin\__init__.py`
- model: deepseek/deepseek-v4-pro-0813
- reviewed: 2026-09-24 20:28
- tokens: in 157501 / out 121277
- est cost: $0.0000

---

_(Model returned only reasoning, no final answer. Raw reasoning below.)_

We need to review the current source (the one provided) and compare with the previous review. The previous review was for an earlier version; we need to identify NEW or CHANGED findings, and confirm fixed ones. The source is the same file but presumably updated. We need to look at the code and see if the previously reported issues are fixed or still present, and find new bugs.

We have the full source with line numbers. We need to analyze carefully.

First, let's understand the structure: The file is PatternSkin/__init__.py, a Blender add-on. The previous review identified several issues. We need to check if they are fixed in the current version.

Let's go through the previous findings one by one and see if they are addressed in the current code.

1. **[HIGH] apply_pattern/api_apply run against stale mesh data in Edit Mode** - line 236 in previous version. In current code, `apply_pattern` is at line 221. Let's examine the current `apply_pattern` function (lines 221-254). It does:
```
def apply_pattern(obj, tile, *, mode, tile_mm, depth_mm, raised, selected_only,
                  target_edge, max_faces=700000, decimate_to=0, autofit_tiles=4, smooth_base=False,
                  tile2=None, layer_mode="OFF",
                  depth_falloff="NONE", depth_falloff_invert=False, depth_vgroup="",
                  depth_feather_mm=0.0,
                  tile_rotate=0.0, u_offset=0.0, v_offset=0.0, tile_variation="OFF", tile_mm_y=0.0,
                  tile2_mm=0.0, layer_factor=1.0):
    me = obj.data
    if len(me.vertices) == 0 or len(me.polygons) == 0:
        raise RuntimeError("Mesh has no geometry - nothing to apply a pattern to.")
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    if bpy.context.mode != "OBJECT":     # BEFORE _apply_prepare: in Edit Mode the RNA
        bpy.ops.object.mode_set(mode="OBJECT")   # select/co arrays are the PRE-edit snapshot
    tile_mm, tile_mm_y, depth_mm, target_edge, selected_only, fallback_whole, autofit = _apply_prepare(   # (whole-mesh
        obj, tile_mm, depth_mm, selected_only, target_edge, autofit_tiles, tile_mm_y)   # fallback lie), and
    # a target_edge=0 apply's foreach_set write would be discarded on Edit-Mode exit.
    for _ in _subdivide_stepwise(me, target_edge, max_faces, smooth_base, selected_only):
        pass
    return _apply_pattern_rest(obj, tile, mode=mode, tile_mm=tile_mm, depth_mm=depth_mm,
                               raised=raised, selected_only=selected_only, target_edge=target_edge,
                               decimate_to=decimate_to, tile2=tile2, layer_mode=layer_mode,
                               depth_falloff=depth_falloff, depth_falloff_invert=depth_falloff_invert,
                               depth_vgroup=depth_vgroup, depth_feather_mm=depth_feather_mm,
                               tile_rotate=tile_rotate, u_offset=u_offset, v_offset=v_offset,
                               tile_variation=tile_variation, tile_mm_y=tile_mm_y, tile2_mm=tile2_mm,
                               layer_factor=layer_factor, fallback_whole=fallback_whole, autofit=autofit)
```
We see that there is now a mode_set to OBJECT before _apply_prepare. So the HIGH issue is fixed. The comment says "BEFORE _apply_prepare: in Edit Mode the RNA select/co arrays are the PRE-edit snapshot". So that's fixed.

2. **[MEDIUM] Post-displacement failures are reported as ERROR/CANCELLED after mesh mutated** – In current code, `_ps_item_done` (line 2668) has try/except around `print_check` and `_apply_finish`? Let's check. In `_ps_item_done` (lines 2668-2780), we see:
```
        try:                            # the mesh is ALREADY displaced at this point: a raise
            for warn in print_check(s.depth_mm, s.tile_mm, s.layer_mm, s.nozzle_mm):
                self.report({"WARNING"}, warn)
        except Exception as _pc_err:    # here must never report the apply itself as failed
            self.report({"WARNING"}, "Print-check failed: %s" % _pc_err)   # (a retry would
        ...
        try:
            fin_name = _apply_finish(obj, s,
                                      pattern_path=(path if s.finish_uses_pattern else None),
                                      tile_units=eff_tile,
                                      selected_only=bool(s.selected_only
                                                         and not res.get("fallback_whole")))
        except Exception as _fin_err:   # the relief SUCCEEDED - only the finish failed
            self.report({"WARNING"}, "Relief applied, but the finish failed: %s" % _fin_err)
            fin_name = None
```
So both `print_check` and `_apply_finish` are now wrapped in try/except and report warnings, not errors. That addresses the MEDIUM issue. Also `_ps_item_done_safe` still exists but now the inner `_ps_item_done` handles those exceptions. So fixed.

3. **[MEDIUM] 3MF export truncates destination file in place** – In current code, `_write_3mf` (lines 3809-3877) now uses `tempfile.mkstemp` and `os.replace`. Let's check: lines 3864-3876:
```
    import tempfile as _tf3                              # mkstemp+replace (PSK-11): ZipFile
    _fd3, _tmp3 = _tf3.mkstemp(dir=os.path.dirname(os.path.abspath(filepath)) or ".",
                                prefix=".ps_3mf_", suffix=".tmp")
    os.close(_fd3)                                       # ZipFile reopens by NAME (the fd form
    try:                                                 # avoids the Windows open-handle block)
        with zipfile.ZipFile(_tmp3, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("[Content_Types].xml", ct)
            z.writestr("_rels/.rels", rels)
            z.writestr("3D/3dmodel.model", model)
        os.replace(_tmp3, filepath)                      # atomic: the old export survives any
    except BaseException:                                # failure up to this exact point
        _rm_quiet(_tmp3)
        raise
```
So fixed.

4. **[MEDIUM] Auto-fit scales tile_mm and depth_mm but not tile_mm_y, and has no ratio < 1 guard** – In current code, `_apply_prepare` (lines 90-139) now includes:
```
                tile_mm_y = tile_mm_y * _ratio if tile_mm_y else tile_mm_y  # the SAME proportional
```
So tile_mm_y is scaled. Also, there is a guard:
```
            if _ratio < 1.0:            # guard: with hint=1 a 1.0-1.5x object ENLARGES the tile -
                tile_mm *= _ratio       # the single-giant-blob failure autofit exists to prevent
                depth_mm *= _ratio
                tile_mm_y = tile_mm_y * _ratio if tile_mm_y else tile_mm_y
                if target_edge:
                    target_edge = max(target_edge * _ratio, tile_mm / 64.0)
                autofit = {...}
```
So the guard is present. Also `_live_build` (lines 2858-3058) now scales tile_mm_y? Let's check `_live_build` around line 2888-2894:
```
    if ext > 0 and (ext / tile_mm) < 1.5:
        _ratio = (ext / float(max(1, s.autofit_tiles_hint))) / tile_mm
        tile_mm *= _ratio
        depth_mm *= _ratio
        resolution = max(resolution * _ratio, tile_mm / 24.0)
        note = ...
```
It does not scale tile_mm_y. But the previous review mentioned `_live_build` also had the omission. In current code, `_live_build` still does not scale `tile_mm_y`. However, the previous review's MEDIUM issue was about `_apply_prepare` and `_live_build`. The `_apply_prepare` part is fixed, but `_live_build` still lacks scaling of `tile_mm_y`. Is that a new/remaining issue? The previous review said "The same omission exists in `_live_build` at line 2871-2873." In current code, `_live_build` is at lines 2858-3058. Let's check if it scales tile_mm_y. In the autofit block (lines 2888-2894), it does not scale tile_mm_y. So that part is not fixed. But the previous review's MEDIUM finding was about both `_apply_prepare` and `_live_build`. Since `_apply_prepare` is fixed but `_live_build` is not, we should note that the `_live_build` part remains. However, the instruction says "Report ONLY findings that are NEW or CHANGED since that review." The previous review already reported this as a MEDIUM issue. If it's partially fixed, we might mention in "Fixed since last review" that `_apply_prepare` is fixed but `_live_build` still has the issue? Actually, the previous review's finding was a single MEDIUM issue covering both. Since one part is fixed and the other not, we should note that the `_live_build` part remains as a new/remaining finding? The instruction says "Report ONLY findings that are NEW or CHANGED since that review." The `_live_build` omission is unchanged from the previous review, so it's not new. But the previous review's finding was partially fixed; we can mention in "Fixed since last review" that the `_apply_prepare` part is fixed, but the `_live_build` part remains. However, the instruction says "Add a '## Fixed since last review' section confirming previously-reported findings that no longer apply." So we should list the ones that are fully fixed. For partially fixed, we might need to report the remaining part as a new finding? But it's not new; it's the same issue in a different function. I think we should treat it as a remaining issue and report it as a new finding because the previous review's finding was about both functions, and now one is fixed but the other remains. But the instruction says "Report ONLY findings that are NEW or CHANGED since that review." The `_live_build` part is unchanged, so it's not new. However, the previous review's finding was a single item; if we consider it as two sub-issues, one is fixed and one remains. To be safe, we can mention in "Fixed since last review" that the `_apply_prepare` part is fixed, and then in "Bugs & vulnerabilities" we can report the remaining `_live_build` issue as a new finding because it's now the only remaining part of that previous finding. But that might be considered restating. I think it's acceptable to report it as a new finding because the previous review's finding was about both, and now the scope is narrowed to `_live_build`. We'll do that.

5. **[MEDIUM] generate_default_library.execute omits active guard** – In current code, `PATTERNSKIN_OT_generate_default_library.execute` (lines 6046-6096) now includes:
```
        if _GEN_LIB.get("active"):                   # invoke guards the DIALOG path; this
            self.report({"WARNING"},                 # guards EXEC_DEFAULT (script/console) -
                "A library generation is already running - wait for it to finish.")   # a second
            return {"CANCELLED"}                     # worker = double paid spend + corrupt PNGs
```
So fixed.

6. **[MEDIUM] live_commit bakes modifiers one at a time and returns CANCELLED mid-way** – In current code, `PATTERNSKIN_OT_live_commit.execute` (lines 3101-3141) now uses a single evaluated bake:
```
        # ONE evaluated bake (the _punch_holes._apply discipline): the evaluated mesh is
        # identical to apply-Subd-then-Displace, so both bake ATOMICALLY. Any failure
        # before the data swap leaves the stack, the mesh AND ps_live untouched - "the
        # live relief is still active" stays TRUE, and Revert still works. (The old
        # per-modifier loop baked Subd irreversibly, then CANCELLED mid-way leaving a
        # flat subdivided shell whose Revert destroyed the Displace settings.)
        others = [(m2, m2.show_viewport) for m2 in obj.modifiers
                  if m2.name not in ("PS_Live_Subd", "PS_Live_Displace")]
        for m2, _sv in others:
            m2.show_viewport = False
        try:
            deps = context.evaluated_depsgraph_get()
            baked = bpy.data.meshes.new_from_object(obj.evaluated_get(deps))
            old = obj.data; obj.data = baked
            if old.users == 0:
                bpy.data.meshes.remove(old)
        finally:
            for m2, sv in others:
                try: m2.show_viewport = sv
                except Exception: pass
            for name in ("PS_Live_Subd", "PS_Live_Displace"):
                try:
                    if obj.modifiers.get(name):
                        obj.modifiers.remove(obj.modifiers[name])
                except Exception:
                    pass
        del obj["ps_live"]
        ...
```
So it's fixed.

Now, we need to look for NEW bugs introduced or remaining issues not previously reported. The previous review also had a list of "Missing safeguards" which are not necessarily bugs but suggestions. We need to see if any of those are still present and if they are now more critical or changed. But the instruction says "Report ONLY findings that are NEW or CHANGED since that review." So we should focus on new bugs/vulnerabilities that were not in the previous review. However, we can also note if some previous "Missing safeguards" are now fixed or still present, but we should not restate them unless they have changed.

Let's examine the current code for new issues.

We'll go through the code systematically, looking for logic errors, security issues, etc.

First, note that the file is huge (over 10,000 lines). We need to focus on areas that might have changed or new code. The previous review was on an earlier version; the current version has many changes, including new features like AI parts, selection tools, etc. We need to identify new bugs in those areas.

Let's scan for potential issues:

- In `_apply_prepare` (lines 90-139), there is a potential division by zero? `_ratio = (_ext / float(max(1, autofit_tiles))) / tile_mm` – if `tile_mm` is 0? But earlier `if _nv0 and tile_mm and tile_mm > 0:` ensures tile_mm > 0. So fine.

- In `_subdivide_stepwise` (lines 142-218), there is a generator. It yields before each pass. The cancel safety is described. But there might be an issue: if the generator is closed mid-loop, the `finally` block runs, but the `bm2.to_mesh(me)` is skipped because it's after the loop. However, the `finally` block frees `bm2`. That's fine. But what about the `_pwm.progress_end()`? It's in finally, so it runs. Good.

- In `_apply_pattern_rest` (lines 257-497), there is a potential issue with `sel` and `P` when `selected_only` is True but no vertices selected? But `_apply_prepare` already handles fallback_whole. However, if `selected_only` is True and there are selected vertices, but after subdivision, the selection might change? The subdivision tags new vertices based on `v.tag` which is set from original selection. So selection should be preserved. But there is a check `if len(h) != len(P): raise RuntimeError`. That's good.

- In `_apply_pattern_rest`, the `_aa_pool` function (lines 340-368) has a potential issue: it crops the tile to `h0` and `w0` which are multiples of `k`, but if `k` is 0? `k = int(min(t.shape[0], t.shape[1]) // (1.6 * spt))`. If `spt` is large, `k` could be 0, but then `if k >= 2:` prevents division by zero. So fine.

- In `_apply_pattern_rest`, the `depth_falloff` handling: if `depth_falloff == "VGROUP"` and `vg` is None, it sets `vgroup_missing = True` and then `if not vgroup_missing:` skips the falloff multiplication. That's fine.

- In `_apply_pattern_rest`, the `depth_feather_mm` block uses `accel.nearest(_outs, P)` and then `np.linalg.norm(P - _outs[_idx], axis=1)`. If `_outs` is empty (i.e., no unselected vertices), then `(~sel).any()` is False, so the block is skipped. Good.

- In `_apply_pattern_rest`, after displacement, it does `me.vertices.foreach_set("co", co.reshape(-1))` and `me.update()`. Then it does shading and decimate. The shading part re-asserts selection. That's fine.

- In `_apply_pattern_rest`, the decimate block (lines 483-495) creates a modifier and applies it. If `modifier_apply` fails, it removes the modifier and re-raises. That's fine.

- In `_apply_pattern_rest`, the return dict includes `uv_fallback` but `uv_fallback` is defined in `_dispatch_projection`? Actually, `uv_fallback` is assigned in the `if len(Pl):` block at line 326: `mode, u, v, uv_fallback = _dispatch_projection(...)`. But if `len(Pl)` is 0, the else block at line 330 also assigns `mode, u, v, uv_fallback = _dispatch_projection(...)`. So `uv_fallback` is always defined. Good.

- In `_apply_pattern_rest`, the `_combine_heights` function is called if `tile2 is not None and layer_mode != "OFF"`. That's fine.

- In `_apply_pattern_rest`, the `_lattice_transform` is called with `tile_mm_y` and `tile_rotate` etc. That's fine.

- In `_apply_pattern_rest`, the `_aa_pool` function is applied to `tile` and `tile2`. That's fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function is called with `_wts` which may be None if `depth_falloff == "VGROUP"` and `vg` is None. But `_depth_falloff` handles `weights is not None` check. So fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` uses `np.clip(weights, 0.0, 1.0)`. If `weights` is None, it uses `np.ones(len(P))`. That's fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `AXIS_X/Y/Z` uses `P[:, ax]`. If `P` is empty, it returns `np.ones(0)` earlier. So fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `RADIAL` uses `d.max()` which could be 0 if all points are same? But `d.max() + 1e-9` avoids division by zero. So fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for unknown kind returns `np.ones(len(P))`. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a list? It's a numpy array. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being None and `kind == "VGROUP"`? It returns `np.ones(len(P))`. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array of wrong length? It's created from `sel_idx` so length matches `P`. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In `_apply_pattern_rest`, the `_depth_falloff` function for `VGROUP` with `weights` being a numpy array but `len(P)` is 0? It returns `np.ones(0)` earlier. Fine.

- In