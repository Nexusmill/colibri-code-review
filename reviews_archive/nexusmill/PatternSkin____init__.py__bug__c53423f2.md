# BUG review: PatternSkin\__init__.py

- source: `C:\Users\User\source\repos\Nexusmill\PatternSkin\__init__.py`
- model: xiaomi/mimo-v2.6-pro
- reviewed: 2026-09-24 15:58
- tokens: in 189911 / out 31263
- est cost: $0.1098

---

## Verdict
Safe to ship — this file has been hardened well past the round‑9 state and I found no high‑impact vulnerability or correctness break. The single biggest risk is still user data loss: `​_apply_finish`'s whole‑mesh path silently wipes every pre‑existing material slot, a defect the function's own comment names but only fixes for the partial‑selection case.

## Bugs & vulnerabilities

**[MEDIUM] `_apply_finish` whole-mesh path still does `me.materials.clear()`, destroying every existing material slot** - `line 2356`
- What: after the `selected_only` region handling (2329–2355), control falls through to `me.materials.clear(); me.materials.append(mat)`. That runs whenever `selected_only` is False, or `selected_only` is True but nothing/everything is selected (`nv == 0`, `not vs.any()`, `vs.all()`, or `region.all()`). The docstring at 2279–2282 explicitly calls this out as part of the bug being fixed ("it also silently discarded any materials the user already had"), but the fix only covers the `region.any() and not region.all()` branch. The `_finish_slot` helper (2260–2270) exists precisely to append non-destructively and is used only on that one branch.
- Trigger: any Apply on a multi-material object with a finish selected and "Selected faces only" off (or with the whole mesh selected) — e.g. a knife with wood/steel/brass slots, or a model that already carries a hand-built node material.
- Impact: every material slot and its assignments are replaced by one `PS_Finish_*` material. Not recoverable except via Undo; on a batch apply across many objects the loss is multiplied. `PATTERNSKIN_OT_apply._ps_item_done` calls this unconditionally at 2680 whenever `fin_name` is truthy.
- Fix: route the whole-mesh case through `_finish_slot` too, then set `material_index` for every polygon to that slot instead of clearing; only `clear()` if the mesh had zero user materials before. If the wipe is truly intended, say so in the tooltip and gate it behind an explicit "Replace all materials" toggle.

**[LOW] Three operators call `self._cleanup_glb()`, a method that only exists on `PATTERNSKIN_OT_ai_parts_native`** - `line 8016` (also 8215, 8505)
- What: `PATTERNSKIN_OT_ai_parts._end` (8016), `PATTERNSKIN_OT_sel_text._end` (8215) and `PATTERNSKIN_OT_ai_parts_semantic._end` (8505) all do `try: self._cleanup_glb() except Exception: pass`. `_cleanup_glb` is defined only on `PATTERNSKIN_OT_ai_parts_native` (8584); the other three inherit `_SelMeshSciPy`/`_SelMesh`/`bpy.types.Operator`, none of which define it. Every exit of those three operators therefore raises `AttributeError` that is swallowed.
- Trigger: any completion, Esc, or force-cancel of the multiview scan, text-select, or named scan.
- Impact: today zero (those operators never set `_glb`), but the `except Exception: pass` is masking a genuine missing method — and the comment at 8008 ("temp-file lifetime lives HERE (the one exit every path shares)") is false for these classes. The moment any of them starts producing a `.glb`, cleanup silently no-ops and the temp file leaks.
- Fix: move `_cleanup_glb` into `_PSCancellableApply`-style shared base or a module-level `_rm_quiet(path)` helper used by all four `_end`s; keep the `getattr(self, "_glb", None)` guard but stop calling a method that isn't there.

**[LOW] Modal `cancel()` handlers touch `context.workspace` / `context.window` unguarded — raise during teardown, leaving the modal cursor stuck** - `line 7200` (also 7305, 9331)
- What: `PATTERNSKIN_OT_sel_click.cancel`, `PATTERNSKIN_OT_sel_strokecut.cancel` and `PATTERNSKIN_OT_ai_pick.cancel` call `context.workspace.status_text_set(None)` and `context.window.cursor_modal_restore()` with no try/except. Blender invokes `cancel()` precisely when the modal is torn down from outside (`window/area closing`, `file load`, another modal grabbing input) — the exact cases where `context.window` is `None` or the workspace is gone.
- Trigger: start "Pick on the model" / "Split with a stroke" / "Pick a part" (each sets `cursor_modal_set(...)` at 7161/7260/9302), then close the window or load a file before finishing.
- Impact: `AttributeError: 'NoneType' object has no attribute 'cursor_modal_restore'` escapes `cancel()`; the status text and `PAINT_BRUSH`/`PAINT_CROSS`/`EYEDROPPER` cursor are never restored, and Blender logs a raw traceback from a teardown path. Every other modal in this file (`_PSCancellableApply.cancel`, `install_accel.cancel`, `check_updates.cancel`, the AI operators' `_end`) guards this correctly.
- Fix: wrap both calls in `try/except Exception: pass`, or use `getattr(context, "window", None)` / `getattr(context, "workspace", None)` with a null check before use.

**[LOW] `_write_3mf` materialises the full vertex XML before enforcing the 4,000,000-triangle ceiling** - `line 3680`
- What: `vtx = "".join('<vertex .../> ...)` (3680–3681) is built from every vertex, and only afterwards does the guard at 3683–3686 `raise ValueError(... "exceeds the 4,000,000-triangle ceiling")`. `objs_xml.append(... % (oid, vtx, tris))` (3694) then makes a second full copy of `vtx`.
- Trigger: export 3MF from a mesh with a very high vertex count but a triangle count under the ceiling (e.g. a 20M-vertex / 3M-triangle scan mesh, or a 5M-triangle mesh that also trips the check).
- Impact: the guard exists specifically because "the in-memory XML build OOMs long before Blender does", yet the largest single string in that build is allocated unconditionally. A `MemoryError`/hard Blender crash instead of the intended clean `ValueError` report at 3755.
- Fix: move the `nt > 4_000_000` check (and an equivalent `nv` ceiling) to immediately after `me.calc_loop_triangles()` / `nv = len(me.vertices)`, before any string is formatted.

**[LOW] `_stamp_stl_header` uses a fixed temp name `fp + ".ps_tmp"` and swallows every failure** - `line 1535`
- What: `_tmp = fp + ".ps_tmp"` then `open(_tmp, "wb")` … `os.replace(_tmp, fp)`, all inside `except Exception: pass`. `_atomic_write_text` (1417–1435) was correctly migrated to `tempfile.mkstemp(dir=..., prefix=".ps_tmp_")` + `os.replace` + failure cleanup; this sibling write was not.
- Trigger: two exports landing on the same path in the same second; or an `os.replace` failure (target locked by a slicer holding the STL open on Windows); or a pre-created `part.stl.ps_tmp` symlink in the export folder.
- Impact: partial/foreign bytes can be swapped into the exported STL header, or a stray `.ps_tmp` is left next to the user's export with no indication — and because the whole block is `except Exception: pass`, the license stamp silently vanishes while the operator still reports `"Exported STL + print notes"`.
- Fix: use `tempfile.mkstemp(dir=os.path.dirname(fp) or ".", prefix=".ps_stl_", suffix=".tmp")` + `os.fdopen` + `os.replace`, and `os.remove(tmp)` on `BaseException`; at minimum log (don't swallow) a failed stamp.

## Missing safeguards
- `_apply_finish` should be covered by a test that pre-populates `me.materials` with two slots and asserts they survive a whole-mesh apply with a finish enabled.
- `_ai_write_colors`' drift guard at 9107 is unreachable for the over-long case: `pp = np.asarray(polypart)[:len(me.polygons)]` (9103) truncates before the `len(pp) != len(me.polygons)` test, so a part map longer than the mesh is silently clipped instead of raising the intended "rescan needed". Check the length of `polypart` itself before slicing.
- `PATTERNSKIN_OT_send_to_spector` builds `path` with `time.strftime("%Y%m%d-%H%M%S")` (9426) — two sends in the same second overwrite each other silently. Add a counter or `tempfile`-style suffix.
- `_PSCancellableApply._ps_rest_kwargs` is never cleared after `_apply_pattern_rest` runs (698), keeping a live reference to `obj`, both heightmap arrays and every kwarg alive for the operator instance's lifetime.
- No test pins the three unguarded `cancel()` handlers or asserts that a modal force-cancel restores the cursor and clears `status_text`.

## Fixed since last review
All four round‑9 items verified resolved in these bytes:
- **R9‑1 `ai_parts.modal` unguarded `self._res[0]`** — the `wait` phase now branches on `if self._err or not self._res:` (7860), normalises `_msg` before every `[:70]`/`[:160]` slice, checkpoints the missed view past via `save_scan_partial` (7886), and `return {"RUNNING_MODAL"}` (7890) exits the miss branch so `assign_view(self._job, self._i, self._res[0])` (7892) is only reached with a truthy result. A None/empty SAM‑2 outcome is now a missed vote, never a `TypeError` abort and never a re-bill.
- **R9‑2 `_punch_holes` cross-call leak** — `_apply` is now one `try` from `cme` creation with pre-initialised `cme/cutter/mod/others` handles (4355) and `except BaseException` teardown (4380–4393); the call site owns both bms in a `finally` keyed on `is_valid` (4413–4422), so a through-boolean failure frees `bm_through`, `bm_csink` and `cme` on every path.
- **`_gen_lib_names` infinite loop / basename collision** — rewritten with a `taken` set (5765–5786): first occurrence keeps the bare basename, later collisions are parent-namespaced with a numeric fallback; the `while cand in taken` loop provably terminates.
- **`_atomic_write_text` fixed temp name** — now `tempfile.mkstemp(dir=os.path.dirname(path))` + `os.fdopen` + `fsync` + `os.replace`, with `os.remove(tmp)` on `BaseException` (1422–1435). (Only the STL-header sibling at 1535 remains on the old pattern.)

---

## In-session verification + remediation (2026-09-24, round 10 - first round under the
owner's efficiency directive: D1 RED-first tests, D2 clears = zero CONFIRMED MED+, D3
LOW-quota effective round 11, D5 parallel agents 2+3 after agent 1 clears)

All 5 findings verified. Adversary gate round 10: APPROVE WITH MODIFICATIONS - every
modification folded in: R10-1's fresh-mesh special case avoids the phantom None slot
(keeps the probe batteries honest), the index fill is np.full (np.zeros would have
silently painted every face onto the EMPTY slot - a silent-wrong-output bug the adversary
caught in the plan text), the vanished-selection fall-through routes to SKIP (a finish over
an undisplaced mesh), and the RED test's self-contradictory assertion was rewritten
(whole-mesh = uniform index + originals survive); R10-4 got a BEHAVIORAL test (the
extracted _check_3mf_ceilings predicate, not a source-order string), a grounded 4M nv
ceiling aligned to the triangle budget, and per-object + running-total checks; R10-3 is one
shared _ui_teardown helper across ALL sites (7 found, not 3); R10-5 shares _rm_quiet with
BaseException coverage and logs failed stamps naming fp.

Fixes: R10-1 _apply_finish whole-mesh = non-destructive slot + np.full index assign (bare
meshes unchanged; multi-material meshes keep their slots) + vanished-selection SKIP;
R10-2 _rm_quiet shared idiom, _end cleans _png AND _glb via getattr (no missing-method
swallowing); R10-3 _ui_teardown helper on every cursor/status restore site; R10-4
_check_3mf_ceilings(nt, nv) called before any XML string + multi-object totals; R10-5
_stamp_stl_header via mkstemp/fdopen/fsync/replace with logged failures; promos: part-map
drift checked BEFORE the truncating slice, send_to_spector existence-checked collision
suffix, _ps_rest_kwargs/_ps_gen cleared after the rest call.

Tests: tests/test_hunt_r10_fixes.py 12/12 PASS - whole-mesh preservation (both user slots
survive, uniform finish index, vanished-selection SKIP), _end dual-temp cleanup, dead-context
teardown, the ceiling predicate truth table (3,999,999 passes; 4,000,001 either axis raises),
failed-stamp integrity, all three promo source pins. The r8 material probe updated for the
new slot semantics (active-slot assertions; the old probe's slot-0 assumption encoded the
very clear() behavior this round removed). r1-r9 probes + smoke re-passed. NOT COMMITTED.
