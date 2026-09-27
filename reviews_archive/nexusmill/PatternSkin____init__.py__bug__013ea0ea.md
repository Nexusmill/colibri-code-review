# BUG review: PatternSkin\__init__.py

- source: `C:\Users\User\source\repos\Nexusmill\PatternSkin\__init__.py`
- model: xiaomi/mimo-v2.6-flash
- reviewed: 2026-09-25 04:33
- tokens: in 199391 / out 50867
- est cost: $0.0422

---

## Verdict

Safe to ship with reservations — no HIGH/CRITICAL and no security holes found, but the single biggest risk is **selection-state corruption**: two paths silently rewrite or clobber the mesh's vertex/edge selection as a side effect, which then feeds wrong regions into later operations (Add region, seed picks, "whole-model-lit").

## Bugs & vulnerabilities

**[MEDIUM] Seed-only picker (`tool="NONE"`) writes face selection only — reintroduces the documented "whole-model-lit" stale-selection bug** - `line 7445`
- What: `PATTERNSKIN_OT_sel_click._pick` does `me.polygons.foreach_set("select", zeros)` then `me.polygons[face].select = True` and never touches vertex/edge flags. The full-domain release only happens inside `_ps_apply_face_selection`, which is reached solely when `self.tool != "NONE"` (line 7447) *and* the spawned operator succeeds (line 7451 swallows its exceptions). The codebase itself documents why this is wrong at line 7144–7146: *"face flags alone leave stale vert/edge selection that flushes back up = the 2026-08-28 whole-model-lit bug."*
- Trigger: Advanced section → "Pick a seed on the model" (line 6435 sets `.tool = "NONE"`), after any prior selection that lit many verts/edges; or any click where the dispatched tool raises (line 7452).
- Impact: entering Edit Mode (line 7455) flushes the stale vert/edge set back up, so the user sees far more selected than the one seed face — and `_sel_seed` (line 7085) then reads that inflated polygon set as the seed for the next Advanced tool, producing a wrong region.
- Fix: route the `NONE` path through `_ps_apply_face_selection(obj, one-hot face mask, frame=True)` instead of raw `foreach_set`, and wrap the `tool != "NONE"` dispatch so a failed op still falls back to the canonical selector.

**[MEDIUM] Apply with "Selected faces only" OFF silently selects every vertex of the mesh** - `line 208`
- What: `_subdivide_stepwise` sets `v.tag = bool(v.select) if selected_only else True` (line 170), and on normal completion unconditionally writes `v.select = v.tag` (lines 208–209) before `bm2.to_mesh(me)`. With `selected_only=False` every tag is `True`, so the whole mesh comes back fully selected. Nothing downstream needs this: `_apply_pattern_rest` uses `sel = np.ones(nv)` (line 278) and `_apply_finish` takes `selected_only=False` (line 2756), so the selection is pure collateral.
- Trigger: any apply where `selected_only` is False — unchecking the checkbox, `api_apply(...)` (default `selected_only=False`, line 2461), or **every** "Batch apply to selected" run (line 5182 hard-codes `selected_only=False`) — provided `target_edge > 0` (line 163 early-returns otherwise, which is essentially never).
- Impact: the user's Edit-Mode selection is destroyed as a side effect. Concretely, `PATTERNSKIN_OT_add_region` then reads `v.select` (line 5256) and silently saves the *entire mesh* as the region; seed-based tools read the inflated set too.
- Fix: only write back when `selected_only` is True — `if selected_only: for v in bm2.verts: v.select = v.tag` — or restore the pre-existing selection snapshot instead of overwriting it.

**[MEDIUM] `PS_PartPattern.tile` has `min=0.5`, silently clamping sub-0.5 part tiles — the exact PSK-TILEFLOOR defect the file documents** - `line 1297`
- What: `tile: FloatProperty(default=20.0, min=0.5)` on `PS_PartPattern`, while the source property `region_tile_mm` was lowered to `min=0.001` (line 2210) precisely because, per the comment at lines 1980–1988, *"min was 0.5, which SILENTLY CLAMPED every smaller value … the field simply snapped back with no warning."* `PATTERNSKIN_OT_ai_assign_part` copies the value straight across: `ent.tile = s.region_tile_mm` (line 9084), and the bake reads it back unvalidated at `tile_mm=float(a.tile)` (line 9163).
- Trigger: set Relief → tile to e.g. 0.1 (legal), assign the pattern to an AI part, then "Bake all parts".
- Impact: the part is baked at 0.5 instead of 0.1 — 5× coarser relief than requested, with no warning anywhere. Blender clamps the RNA write silently, so the UI never shows the discrepancy.
- Fix: change line 1297 to `min=0.001, soft_min=0.01` to match `region_tile_mm`/`tile_mm`, and add a test asserting `ent.tile == s.region_tile_mm` after assign for values below 0.5.

**[MEDIUM] `ai_parts_count` / `ai_parts_active` are scene-global and never reset when the active object changes — stale part UI on unscanned objects** - `line 1166`
- What: `_ps_autoload_tick` is the designated per-object-switch hook, but every early-return branch (lines 1167, 1169, 1172, 1175, 1178, 1182) leaves `s.ai_parts_count` untouched; it is only ever assigned a positive value (lines 1185, 8069, 8235, 8776, 8965, 9294, 9415, 9477, 9811) and never `0`. Switching from a scanned object to a plain mesh therefore keeps the previous object's part count in the scene.
- Trigger: scan object A into parts, then click object B (no `ps_ai_part` attribute).
- Impact: the Pattern panel still draws the filmstrip (line 6256 `if int(s.ai_parts_count) > 0`) and the Selection panel shows the full part-navigation block (line 6468 `else` branch) for an object that has no parts; every action there fails with "Run a scan first" / "Scan into parts first".
- Fix: in `_ps_autoload_tick`, when the active object has no `ps_ai_part` (and isn't the object the count was computed for), set `s.ai_parts_count = 0; s.ai_parts_active = -1; s.ai_parts_overlay = False` before returning.

**[MEDIUM] Spector fast-reuse path runs `finalize_job` synchronously in `execute()` with the WAIT cursor already cleared — multi-second freeze** - `line 8066`
- What: the outer `try/finally` that sets/resets the WAIT cursor closes at line 8055 (`cursor_set("DEFAULT")`), and the Spector-reuse block starts at line 8057 — so `_ap.finalize_job(_ld["job"], ctx, ...)` at line 8066 runs inline with no cursor, no status update (still "preparing mesh…" from line 8034) and no thread. The file's own G-HANG-1 notes state `finalize_job` is "pure numpy/scipy … measured several seconds" on dense meshes, which is why lines 8212–8219, 8464–8471, 8745–8751 and 9242–9247 all moved it to a worker thread.
- Trigger: re-run "AI Parts" on a model Spector recognises from a previous scan, on a scan-sized mesh.
- Impact: Blender appears hung for seconds at the start of a *free* operation, with a status line that says something unrelated — the exact hang-report failure mode the remediation notes record.
- Fix: move the Spector branch behind the same `finalize`/`finalize_wait` thread pattern used at lines 8203–8229 (or at minimum re-set the WAIT cursor and a "Recognising from a previous scan…" status around line 8066).

**[MEDIUM] `ai_parts_native` performs blocking HTTP on the main thread inside `modal()` (and in `invoke()`)** - `line 8982`
- What: `self._pred = self._ap.p3sam_poll(self._tok, self._pred)` runs synchronously on every 3-second TIMER tick, and `self._pred = _ap.p3sam_start(tok, glb)` (line 8871) blocks `invoke()`. Only the *download* was moved off-thread — line 9006–9010 says so explicitly: *"the network download … run on a worker thread."* The exception handler at lines 8984–8991 confirms these are network calls (it counts "connection hiccups").
- Trigger: any native-3D scan while the Replicate endpoint is slow or the connection is stalling (as opposed to erroring).
- Impact: a hung request freezes Blender for the full HTTP timeout on each tick, repeatedly, mid-paid-operation — the UI cannot process Esc while blocked.
- Fix: run `p3sam_poll` (and `p3sam_start`) on a worker thread with the same `fetch_wait`-style phase already used for the download, or give the client a short hard timeout (≤2s) for the poll path.

**[MEDIUM] Modal Edit-Mode guard forces OBJECT mode on whatever the user is editing, not just the apply target** - `line 699`
- What: the "modal-gap guard" reads `if bpy.context.mode != "OBJECT"` and then unconditionally does `bpy.context.view_layer.objects.active = self._ps_obj` + `bpy.ops.object.mode_set(mode="OBJECT")`. Its own comment (lines 698–699) scopes the concern to *"the user entered Edit Mode on the TARGET"* — but the code fires for any edit object, and it runs on a 0.01 s timer (line 646), so it lands within ~10 ms.
- Trigger: start any modal apply, then enter Edit Mode on a *different* object while it subdivides.
- Impact: the user is yanked out of their edit session on the unrelated object and their active object is silently reassigned to the apply target (which then stays active after the apply, per line 479–480).
- Fix: gate on identity — `if bpy.context.edit_object is getattr(self, "_ps_obj", None):` before touching `active`/`mode_set`, leaving unrelated edit sessions alone.

**[MEDIUM] `sel_text` never checkpoints partial paid views — a crash or Esc mid-scan re-bills all of them** - `line 8457`
- What: the text-select loop increments `self._i` (line 8457) with no `save_scan_partial` equivalent, and `save_text_select` is only reached at finalize (line 8481) or Esc-during-`finalize_wait` (line 8401). Its sibling `ai_parts` checkpoints after *every* paid view (lines 8163, 8184, 8199) specifically so "a crash now resumes here instead of re-billing". Line 8411 acknowledges the re-bill only as *cancel* behaviour; a crash, file-load or window close hits the same loss with no message at all.
- Trigger: crash / File▸New / window close during views 1..7 of the 8-view text-select (line 8343 `self._nv = 8`).
- Impact: up to 8 paid SAM-3 calls are lost and the identical query bills again on the next attempt — the money-safety class RC-1 (lines 4205–4212) exists to prevent.
- Fix: mirror the `ai_parts` checkpoint — persist the partial job after each `text_assign_mask` (line 8456) and resume from it in `invoke` the way lines 8043–8049 do.

## Missing safeguards

- No test asserts that Apply with `selected_only=False` leaves vertex/edge selection byte-identical — the write-back at lines 208–209 is untested and currently wrong.
- No test drives the seed-only picker (`tool="NONE"`) after a wide selection and asserts all three selection domains agree afterwards.
- No test round-trips `region_tile_mm < 0.5` through `ai_assign_part` → `ai_bake_parts` and compares the baked tile to the requested value (would catch the `min=0.5` clamp).
- No test switches the active object after a scan and asserts `s.ai_parts_count == 0` for an object with no `ps_ai_part` attribute.
- No test runs `ai_parts_native` with a poll endpoint that stalls, asserting the modal stays responsive (Esc deliverable) — the poll at line 8982 is unbounded on the main thread.

## Fixed since last review

- **MEDIUM — `ai_load_scan` claimed `_AI_RUN` before fallible work**: `_ai_begin` now sits at line 9256, immediately before the guarded `try` at 9257; `job` is validated at line 9236 and `thread.start()` at line 9250 both precede the claim, so nothing raise-capable sits between claim and release.
- **MEDIUM — queue drivers dereferenced the RNA ref that caused the exception**: all handlers now go through `_rna()` — lines 5175 (name captured *before* the `try`), 5199, 5317, 5357, 9143–9144, 9181 — so a deleted object/item skips instead of raising inside the handler.
- **MEDIUM — pick modals dereferenced `context.active_object` with no guard**: `_pick` now returns `False` at lines 7435–7436 and `ai_pick.modal` tears down at lines 9749–9751 when the active object is missing or freed.
- **MEDIUM — `sel_text` ran finalize synchronously in `modal()`**: `text_finalize` now runs on a worker thread (lines 8459–8472) polled via `finalize_wait` (lines 8474–8478), matching the `ai_parts` pattern.
- **MEDIUM — `ai_settings` set the WAIT cursor with no `try/finally`**: now wrapped at lines 4097–4100 with `finally: cursor_set("DEFAULT")`.