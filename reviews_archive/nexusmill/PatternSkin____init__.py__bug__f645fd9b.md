# BUG review: PatternSkin\__init__.py

- source: `C:\Users\User\source\repos\Nexusmill\PatternSkin\__init__.py`
- model: xiaomi/mimo-v2.6-pro
- reviewed: 2026-09-24 13:15
- tokens: in 189944 / out 46920
- est cost: $0.1234

---

## Verdict
All five findings from the previous review are genuinely fixed in these bytes (verified against the cited lines). What remains is medium-grade state-corruption risk on error paths — the worst being `_punch_holes`, whose boolean-bake helper can permanently disable every other modifier on the user's object when the EXACT solver fails.

## Bugs & vulnerabilities

**[MEDIUM] `_punch_holes._apply` has no exception safety — a boolean failure permanently disables the user's other modifiers and leaks the cutter** - `line 4305`
- What: the helper disables every other modifier before evaluating the boolean and has no `try/finally` to undo it:
  ```
  4315	        others = [(m2, m2.show_viewport) for m2 in obj.modifiers if m2.name != mod.name]
  4316	        for m2, _sv in others:
  4317	            m2.show_viewport = False
  4318	        deps = context.evaluated_depsgraph_get()
  4319	        baked = bpy.data.meshes.new_from_object(obj.evaluated_get(deps))
  4320	        obj.modifiers.remove(mod)
  4321	        for m2, sv in others:
  4322	            m2.show_viewport = sv
  ```
  If `new_from_object` raises (EXACT solver failure on a degenerate/near-coplanar cutter, out-of-memory on a dense mesh, freed depsgraph), the `show_viewport = False` assignments are **never reverted**, the `holes` boolean modifier stays on `obj`, and `cutter` + `cme` (4306–4307) leak as datablocks. The caller at 4448–4453 (`scale_from_outline`) swallows the exception with `except Exception: pass`, so the user sees a scale with no holes **and** their Mirror/Subsurf/etc. silently greyed out with no message at all. `_build_scale` (4406) propagates instead, but the damage is already done.
- Trigger: **Create scale pair** / **Create scales from outline** with an outline that produces a degenerate cutter (zero-area hole component that survived the `r < 0.6` filter at 4377, or a countersink cone whose `csd` collapses at 4298–4300), on an object that already has modifiers.
- Impact: silent, unrecoverable-from-the-UI loss of modifier state on the user's own object plus orphaned `PS_ScaleCut` object/mesh datablocks that accumulate in the .blend.
- Fix: wrap the whole body of `_apply` in `try/finally` that restores `show_viewport`, removes `mod`, and removes `cutter`/`cme`; move `baked` assignment + `obj.data` swap into the success path only. Also free `bm_csink` in a `finally` so a raising `_apply(bm_through)` at 4329 doesn't leak it (4330–4335).

**[MEDIUM] `_apply_finish` mutates a shared, name-keyed material — a second Apply re-points the first object's texture and mapping scale** - `line 2252`
- What: the pattern material is keyed only by finish name:
  ```
  2251	    mname = "PS_Finish_" + fin[0] + ("_pattern" if use_pattern else "")
  2252	    mat = bpy.data.materials.get(mname) or bpy.data.materials.new(mname)
  ```
  and then, every call, its node tree is rebuilt against the *current* apply's image and tile size:
  ```
  2261	            for nm in ("PS_TexCoord", "PS_Mapping", "PS_PatternTex", "PS_Tint"):
  2263	                if nd: nt.nodes.remove(nd)
  2267	            inv = 1.0 / max(float(tile_units or 1.0), 1e-6)
  2268	            mp.inputs["Scale"].default_value = (inv, inv, inv)
  2270	            tex.image = bpy.data.images.load(pattern_path, check_existing=True)
  ```
  `pattern_path` and `tile_units` are not part of the key, so every object finished with the same `PS_FINISHES` entry shares one material whose image and scale are whatever the *last* Apply set. The documentstring even promises per-object results ("the image drives Base Color … at the same tile size as the relief").
- Trigger: apply a color-pattern preset (e.g. damascus) to object A at tile 20 mm, then to object B at tile 8 mm — or with a different pattern file. Object A's material scale becomes `1/8` and its texture becomes B's.
- Impact: previously finished objects silently change appearance in the viewport and in any material-aware export; nothing warns.
- Fix: include a hash of `(pattern_path, tile_units)` in `mname`, or copy the material per object (`mat.copy()` / `mat = mat.copy(); mat.name = ...` before mutating), so the node-tree rewrite never touches another object's slot.

**[LOW] `_self_update_worker`'s rollback only catches `OSError`, so any other failure skips it and leaves a half-updated add-on** - `line 1793`
- What: the two-phase install claims "keeping a backup so **ANY** failure restores the previous version" (1752–1755), but the rollback loop is gated on:
  ```
  1793	            except OSError as ce:
  1794	                for dp, bak in reversed(applied):
  ```
  `MemoryError`, `KeyboardInterrupt` (Ctrl+C in a `-b` batch), or a non-OSError from `shutil.copyfile`/`os.replace` jumps straight past the rollback *and* past the `RuntimeError` that names the failure — the `finally` at 1820 only removes the staged dir and the temp zip. Separately, if `shutil.copyfile(sp_, new)` at 1790 raises after `shutil.copyfile(dp, bak)` at 1788, that `.psbak` is stranded (it is only removed at 1804–1809 for entries that reached `applied`).
- Trigger: run **Update now (one click)** on a machine that runs out of memory/disk mid-copy, or interrupt the worker thread.
- Impact: the add-on's own `PatternSkin/` tree is left in a mixed old/new state with no rollback and no error message; `.psbak`/`.psnew` files accumulate next to the live modules.
- Fix: change `except OSError as ce` to `except BaseException as ce` (re-raise after rollback), move `applied.append((dp, bak))` to immediately after the backup is made, and delete the just-created `.psbak`/`.psnew` in the per-file `except` path.

**[LOW] `modal()`'s Esc branch calls `_ps_on_cancel` with no containment — the round-7 backstop only covers `_ps_item_done`/`_ps_item_failed`** - `line 663`
- What:
  ```
  663	        if event.type == "ESC":
  664	            self._ps_close_gen()
  665	            self._ps_release_busy()
  666	            return self._ps_on_cancel(context)
  ```
  `_ps_item_done_safe`/`_ps_item_failed_safe` (695–714) were added precisely so a raising callback can't escape `modal()`, but `_ps_on_cancel` was not given the same wrapper. `PATTERNSKIN_OT_batch_apply._ps_on_cancel` at 4913–4914 does `for o in self._bq_meshes: o.select_set(True)` **outside** any `try` (contrast `_bq_finish`, 4901, which is now covered by the backstop).
- Trigger: select 2+ meshes, run **Batch apply to selected**, delete one from the Outliner mid-run, then press Esc.
- Impact: `ReferenceError: StructRNA of type Object has been removed` escapes `modal()` as a raw traceback; the operator ends without an undo push. (Timer/busy are already released by 4907/665, so nothing is stranded — hence LOW.)
- Fix: wrap `return self._ps_on_cancel(context)` in the same `_ps_on_cancel_safe` backstop as its siblings, and make `batch_apply._ps_on_cancel` guard each `select_set` with `try/except Exception`.

**[LOW] AI-scan temp files (`_png`, `_glb`) leak on Esc and on error — only `cancel()` cleans them, and `cancel()` is not called on a modal-initiated `CANCELLED`** - `line 7873`
- What: `PATTERNSKIN_OT_ai_parts._end` (7873), `sel_text._end` (8070), `ai_parts_semantic._end` (8358) and `ai_parts_native._end` (8589) all stop the timer and release the AI slot but never touch `self._png` / `self._glb`. The removal exists only in each class's `cancel()` (7894–7900, 8090–8096, 8379–8385, 8610–8616), and Blender does **not** call `cancel()` when `modal()` returns `{"CANCELLED"}`. The modal's own Esc handlers (7714–7716, 7991–7992, 8190–8191, 8465–8466) and the outer `except` blocks all exit through `_end`. `ai_parts_native`'s outer except (8583–8587) additionally skips `_cleanup_glb()`.
- Trigger: start any AI scan, press Esc during a view render or after a failure.
- Impact: one orphaned render PNG (640×640) — or a full downloaded `.glb` part mesh for the native-3D path — per cancelled/failed run, in `bpy.app.tempdir`, for the rest of the session.
- Fix: do the `os.remove(self._png)` / `self._cleanup_glb()` inside `_end` (guarded by `getattr`), so every exit path is covered; then `cancel()` only needs to call `_end`.

**[LOW] `_apply_pattern_rest`'s decimate step has no rollback — a failing `modifier_apply` strands a `PS_Decimate` modifier and aborts after the mesh is already displaced** - `line 473`
- What:
  ```
  475	        dm = obj.modifiers.new("PS_Decimate", "DECIMATE")
  476	        dm.decimate_type = "COLLAPSE"
  477	        dm.ratio = max(0.01, float(decimate_to) / len(me.polygons))
  478	        bpy.ops.object.modifier_apply(modifier=dm.name)
  ```
  No `try/finally`. The vertex displacement has already been written to the mesh at 445, so an exception here (object not in the current view layer, hidden, op-context failure inside a modal tick) aborts `_apply_pattern_rest` and rolls up to `_a_fail`, which reports "the mesh was subdivided for the apply; press Ctrl+Z" — while a dangling `PS_Decimate` modifier remains on the object and is never removed.
- Trigger: set **Decimate to** > 0 and Apply on an object whose modifier stack cannot be applied at that moment (e.g. hidden viewport, or the op runs against a stale `bpy.context`).
- Impact: a stray modifier on the user's object plus a misleading error that points at Ctrl+Z instead of the real cause.
- Fix: wrap 478 in `try/finally: obj.modifiers.remove(dm)` (or `except: obj.modifiers.remove(dm); raise`), and use the operator's `context` rather than `bpy.context` for the active-object assignment at 474.

## Missing safeguards
- `_punch_holes._apply` needs a `try/finally` that restores `show_viewport`, removes the boolean modifier and the cutter datablocks; add a test that a forced boolean failure leaves `obj.modifiers` and `obj.data` byte-identical.
- `_apply_finish` needs a per-object (or per-`pattern_path`+`tile_units`) material identity; add a regression test that finishing object A then object B with a different pattern does not change A's material node tree.
- `_self_update_worker` should roll back on `BaseException`, and the rollback path should report which files it could **not** restore rather than unconditionally claiming "rolled back".
- `modal()`'s Esc path should route `_ps_on_cancel` through the same containment used for the two completion callbacks; there is currently no test that a raising `_ps_on_cancel` terminates the modal cleanly.
- `_end()` in the four AI operators should own temp-file lifetime so Esc/error paths are covered without duplicating cleanup in `cancel()`.
- `_ai_cache_sig` (8812) reads `me.loop_triangles` without `calc_loop_triangles()`, unlike `_sel_ctx` (6702), `_ai_spector_recognize` (8800) and `send_to_spector` (9274). Call it explicitly for determinism so the cache-invalidation key can never be computed from a stale/empty triangulation.
- `_apply_pattern_rest` should assert `len(h) == len(P)` before `co[sel] = P + N * (h[:, None] * signed)` (444), and `_ai_write_colors` should assert `len(polypart) == len(me.polygons)` before `rgb[vis]` (8976) — both currently fail with a raw `IndexError` on any length drift.
- `_write_3mf` (3614) builds the whole model XML as one in-memory string; a multi-million-face mesh will spike memory with no cap. Stream into the zip, or document/enforce a face ceiling.

## Fixed since last review
All five round‑7 findings verified resolved in the current bytes:
- **`grip_pattern` degenerate shape** — `return np.ascontiguousarray(np.broadcast_to(a, (size, size)), dtype=np.float32)` at **1250** squares both single-operand branches; `make_seamless` is now inside `generate_grip`'s `try` (**4574–4582**).
- **`_AI_PARTS_CACHE` stale `tp`/`labels`** — `_ai_cache_sig` (**8812–8822**, loop-triangle topology hash) is written at all six cache sites (1160, 7673, 7831, 8327, 8520, 8776) and `_ai_cache_hydrate` now validates it **before** its early return (**8834–8838**), with the attribute-based pick degrade (**8869–8877**) and the honest "mesh changed" message in `ai_parts_regran` (**8905–8907**).
- **`modal()` uncontained completion callbacks** — `_ps_item_done_safe` / `_ps_item_failed_safe` (**695–714**) stop the timer, release the busy guard, report and return `CANCELLED`; all six queue callbacks call `_ps_stop_timer` first (4882, 4888, 5037, 5043, 8731, 8737).
- **`install_default_library` unbounded fetch** — routes through `_verified_fetch(..., max_mb=400, progress_key="")` at **5579–5580** (host-pinned, no redirects, chunked cap, hash-verified before use); the temp file is removed in both the `except`/`finally` at **5584–5590** and **5625–5628**.
- **`_load_license` leaf types** — `{str(k): str(v) for k, v in raw.items() if isinstance(v, (str, int, float)) and not isinstance(v, bool)}` at **1467–1469**, so `null`/`int`/`list`/`bool` values can no longer break `PATTERNSKIN_OT_activate`.

---

## In-session verification + remediation (2026-09-24, round 8)

All 6 findings verified. Adversary gate round 8: APPROVE WITH MODIFICATIONS, folded in:
cleanup-in-finally-ONLY for _punch_holes (a cleanup that also ran on success would
double-remove dead RNA FROM the finally and mask the real exception); decimate removal is
except-only (modifier_apply CONSUMES the modifier - a finally-remove is a guaranteed
ReferenceError on every success); bm.free() single-owner inside _apply with the call sites'
else-branches the only other freer; .psbak kept on disk when its own restore failed (it is
the last backup) with the rollback message naming unrestored files; the re-raise chains the
cause; per-object select_set guards in BOTH batch loops (a freed ref on the SUCCESS path
must not turn "Applied to N/M" into an error); cancel() is now pure delegation with _end
owning temp-file lifetime (idempotent, null-then-remove) across ALL exits since modal()-returned
CANCELLED never triggers cancel(); _ai_cache_sig forces calc_loop_triangles() (loop triangles
are not persisted across saves - an empty triangulation false-invalidates AND false-accepts);
3MF ceiling documented AND enforced.

Fixes: R8-1 _punch_holes._apply finally-only teardown (viewport state restored first, mod/
cutter/cme each individually guarded); R8-2 finish materials keyed by (finish, normcase'd
pattern path, normalized tile) when use_pattern - non-pattern finishes correctly stay shared
(their constants never mutate per-apply); R8-3 rollback on BaseException with chained re-
raise, backup-recorded-at-backup-time, .psnew always cleaned, honest unrestored-file list;
R8-4 ESC-branch containment + both batch loops guarded; R8-5 _end owns _png/_glb (4 sites,
de-duplicated cancel()); R8-6 decimate except-only removal; promos: triangulation forced in
the cache sig, relief/part-map length-drift RuntimeErrors, enforced 4M-triangle 3MF ceiling.

Tests: tests/test_hunt_r8_fixes.py 14/14 PASS - forced boolean failure restores modifier
visibility and cleans the cutter; per-identity finish materials (different key -> new
material, same key -> shared, tile None==1.0); ESC containment drive; _end temp ownership;
source pins for the except-only decimate, forced triangulation, drift asserts, ceiling. r1-r7
probes + smoke re-passed. NOT COMMITTED.
