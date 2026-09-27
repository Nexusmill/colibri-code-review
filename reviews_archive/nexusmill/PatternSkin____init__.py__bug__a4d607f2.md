# BUG review: PatternSkin\__init__.py

- source: `C:\Users\User\source\repos\Nexusmill\PatternSkin\__init__.py`
- model: xiaomi/mimo-v2.6-flash
- reviewed: 2026-09-25 03:39
- tokens: in 197862 / out 44084
- est cost: $0.0400

---

## Verdict

Not safe to ship yet. The prior HIGH (dead free-scan path) and most MEDIUMs are fixed, but new/remaining error paths can strand session-wide state — the single biggest risk is an exception escaping a queue driver or an AI operator *after* it claims shared state, leaving every AI button greyed out or the batch progress cursor stuck for the rest of the session.

## Bugs & vulnerabilities

**[MEDIUM] `ai_load_scan` claims the shared `_AI_RUN` slot before fallible work, with no guard until 6 lines later — an exception permanently disables every AI operator** - `line 9172`
- What: `_ai_begin("Load saved scan")` runs at line 9172, but the first releasing/containing region is the timer-registration `try` at line 9186. Between them sit two raise-capable statements: the default argument `job=loaded["job"]` (line 9176) evaluated at def-time, and `self._thread.start()` (line 9184). Every sibling operator (`ai_parts` 8070→8073, `sel_text` 8351→8354, `semantic` 8550→8553, `native` 8819→8821) places `_ai_begin` immediately before its guarded `try`; this one does not.
- Trigger: a saved-scan cache file that is present and truthy but from an older/other format without a `"job"` key (only `if not loaded` is checked at line 9161), or `Thread.start()` failing.
- Impact: `KeyError`/`RuntimeError` escapes `execute()` with `_AI_RUN["op"]` still set; `_ai_finish()` never runs, so `_ai_guard_poll` (line 7691) returns False for **every** AI operator until Blender restarts — all AI buttons greyed with "Load saved scan is running".
- Fix: move `_ai_begin` to immediately before the `try` at line 9186 (after building the thread), or wrap lines 9173–9185 in `try/except: _ai_end…; raise`. Add a test asserting `_ai_busy() == ""` after any `execute()` that raises post-claim.

**[MEDIUM] Queue drivers' `except` handlers dereference the same RNA ref that may have caused the exception — a deleted object/item mid-batch aborts the queue and strands the progress cursor** - `line 5182`
- What: `_bq_start_current` catches an exception from the per-item body (line 5181) and then formats `f"{o.name}"` (line 5182); `_ps_item_failed` does `o = self._bq_meshes[self._bq_i]` / `f"{o.name}"` (lines 5194–5195). The region and part queues do the same with `it.vgroup` (lines 5339, 5352) and `a.part` (lines 9105, 9118). Holding a Python reference to a deleted Blender object does not keep the datablock alive — `.name`/`.vgroup` then raises `ReferenceError` *inside the handler*.
- Trigger: run "Batch apply to selected" (or Bake regions / Bake all parts) — all these modals return `PASS_THROUGH` for non-TIMER events, so the panel stays live — and delete the current object (or click "Clear regions") before the next queue tick.
- Impact: the second `ReferenceError` escapes the driver. From `invoke` it aborts the operator after `progress_begin` (line 5152) with `progress_end` never called → stuck mouse progress indicator; from `_ps_item_done` it is caught by `_ps_item_done_safe` (line 733), which stops the timer and returns CANCELLED — again skipping `_bq_finish` (line 5199), so the progress cursor stays stuck **and** every remaining object is left deselected (line 5173 deselected them all; only `_bq_finish` re-selects).
- Fix: capture the name before the `try` (`nm = o.name` inside a nested try, or use `getattr(o, "name", "<deleted>")`), and move `progress_end()`/re-select into a `finally` (or call `_bq_finish` from the `_safe` backstops). Same treatment for the region/part handlers.

**[MEDIUM] Pick modals dereference `context.active_object` with no None/freed guard — exception escapes `modal()` and leaves the modal cursor stuck** - `line 7418`
- What: `PATTERNSKIN_OT_sel_click._pick` does `obj = context.active_object; me = obj.data` (line 7418) and `PATTERNSKIN_OT_ai_pick.modal` does the same (line 9678) *before* any try, and both are called from `modal()` unwrapped (lines 7445, 9678). The P3-4 fix added `context.region_data is None` guards (lines 7443, 9676) and made `_raycast_pick_face` itself total (try/except → −1, lines 7366–7376), but neither covers a missing/freed active object. `sel_strokecut` is safe only because it passes the object *into* `_raycast_pick_face`'s try.
- Trigger: arm "Pick on the model" or AI "Pick on model", delete (or un-set) the active object, then left-click inside the 3D viewport — `region_data` is not None, so the guard passes and `obj.data` raises `AttributeError`/`ReferenceError`.
- Impact: the exception escapes `modal()` instead of the `_ui_teardown()` path, so the `PAINT_BRUSH`/`EYEDROPPER` cursor and the status-bar text stay stuck; `cancel()` cleanup never runs.
- Fix: at the top of both handlers, `obj = context.active_object; if obj is None or obj.type != "MESH": _ui_teardown(context); return {"CANCELLED"}`, and wrap the `_pick`/raycast body in `try/except` falling back to teardown.

**[MEDIUM] `sel_text` runs its finalize + selection write synchronously inside `modal()` — the exact G-HANG-1 freeze the sibling operators were moved off of** - `line 8418`
- What: `tribool, score, nsel = self._ap.text_finalize(self._job, self._ctx)` (line 8418) plus `_name_part_from_selection` / `_sel_write` / `_ps_apply_face_selection` all execute in one non-yielding timer tick. `ai_parts` (line 8193), `semantic` (line 8684) and `ai_load_scan` (line 9176) all moved their equivalent finalize to a worker thread specifically because it "measured several seconds with ZERO on-screen feedback" on dense meshes.
- Trigger: any dense/scan-sized mesh → "Select by name" → the finalize tick.
- Impact: Blender appears hung for seconds with a frozen progress bar mid-paid-operation, the failure mode the codebase's own remediation notes record as a hang report.
- Fix: mirror the `finalize_wait` pattern from `ai_parts` (lines 8193–8211): spawn a thread for `text_finalize`, poll it on subsequent ticks, and do only the bpy-touching `_sel_write` on the main thread.

**[MEDIUM] `ai_settings` sets the WAIT cursor around `_validate_provider_key` with no try/finally** - `line 4096`
- What: `cursor_set("WAIT")` (4096) → `_validate_provider_key(...)` (4097) → `cursor_set("DEFAULT")` (4098). If the validation call raises anything it does not itself catch (a network-stack exception escaping the client), the restore never runs and the exception escapes `execute()`.
- Trigger: key validation against the provider while the network/endpoint misbehaves in a way the client doesn't wrap.
- Impact: cursor permanently stuck on WAIT plus a raw traceback instead of the intended `"Key not saved - %s"` report.
- Fix: `context.window.cursor_set("WAIT")` / `try: ok, msg = …` / `finally: context.window.cursor_set("DEFAULT")`.

## Missing safeguards

- No test drives any queue operator (batch apply, bake regions, bake parts) with an item deleted or the collection cleared mid-run — that is precisely the path where the `except` handlers themselves raise (line 5182 et al.).
- No test asserts the `_ai_begin`/`_ai_finish` pairing invariant: that `_ai_busy()` is empty after any AI operator's `execute()` raises after claiming the slot.
- No test exercises the pick modals with `context.active_object is None` after invoke.
- `_dep_installed` (lines 1385–1392) is documented as never importing lockable packages, but its `__import__` fallback fires whenever `accel.dep_status()` returns `None`, and it is called from `draw()` (line 6860). Nothing guarantees `dep_status` never returns `None` for `cairosvg` during the async-probe window — if it does, draw() locks the very files the Install button needs, recreating the WinError-5 failure the design says must be impossible. Add an assertion/test that tracked packages always return a tuple.
- `PATTERNSKIN_OT_ai_parts_native` (class line 8772), `PATTERNSKIN_OT_ai_parts_semantic` (line 8494) and `PATTERNSKIN_OT_sel_text` (line 8287) define no `execute()`, unlike `PATTERNSKIN_OT_ai_parts` which routes `execute → invoke` (lines 2513–2518 pattern); scripted/EXEC_DEFAULT invocation of the three cannot run them.

## Fixed since last review

- **HIGH — `ai_load_scan` never started its worker thread**: `self._thread.start()` now present at line 9184 (with the "P3-high fix" comment); the free scan-restore path runs.
- **MEDIUM — `_live_build` deleted the temp PNG the live image pointed at**: `img.pack()` now runs at line 3031 *before* the `finally` removes the file, so the relief survives a .blend reload.
- **MEDIUM — `live_commit` silently swapped modifier order**: the order change is now disclosed via a WARNING (lines 3173–3182) instead of reporting plain success.
- **MEDIUM — `ai_load_scan` bypassed the `_AI_RUN` guard**: the class now has `poll()` → `_ai_guard_poll` (lines 9144–9146) and an `_ai_busy()` refusal in `execute()` (lines 9149–9151).
- **MEDIUM — pick modals raycast without confirming a 3D region**: `_raycast_pick_face` is now total (try/except → −1, lines 7366–7376) and all three modals guard `context.region_data is None` (lines 7443, 7545, 9676).
- **MEDIUM — modals dispatched on bare `event.type == "TIMER"`**: every modal handler now filters with `event.timer != self._timer` (lines 684, 3391, 3782, 6168, 7020, 8088, 8369, 8568, 8843, 9197).