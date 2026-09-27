# BUG review: PatternSkin\__init__.py

- source: `C:\Users\User\source\repos\Nexusmill\PatternSkin\__init__.py`
- model: xiaomi/mimo-v2.6-flash
- reviewed: 2026-09-25 02:38
- tokens: in 193530 / out 83463
- est cost: $0.0505

---

## Verdict

Not safe to ship. The single biggest risk is that `PATTERNSKIN_OT_ai_load_scan` — the "Use saved scan (free)" button — is dead code in practice: it creates its worker thread but never starts it, so the operator fails on its very first timer tick every time.

## Bugs & vulnerabilities

**[HIGH] `ai_load_scan` never starts its worker thread — the free scan-restore path always fails** - `line 9121` (failure surfaces at `line 9150`)
- What: `self._thread = threading.Thread(target=_work_fin, daemon=True)` is created and never `.start()`ed. Every sibling operator in this file does `...Thread(...)` immediately followed by `.start()` (e.g. `line 8060`, `8113`, `8154`, `8337`, `8535`, `8585`, `8640`, `8831`, `8905`). Here it is missing, so `self._fin_res` stays `None`.
- Trigger: any object with `ps_ai_scan_saved` set → panel button "Use saved scan (free)" (`line 6466`) → the first `TIMER` tick at `line 9141` sees `is_alive()` is `False`, `self._fin_err` is `None`, and falls straight through to `labels, n, pl = self._fin_res`.
- Impact: `TypeError: cannot unpack non-iterable NoneType`, caught at `line 9165`, reported as "Saved-scan restore error: …" and `CANCELLED`. The documented free-reuse of a paid scan (never re-bill the user) never works.
- Fix: add `self._thread.start()` after `line 9121` (and add a smoke test that drives `PATTERNSKIN_OT_ai_load_scan` through one timer tick).

**[MEDIUM] `_live_build` deletes the temp PNG that the live-relief Image datablock still points at** - `line 3026` (write at `line 3009`, load at `3021`)
- What: the Displace texture is written to `bpy.app.tempdir/ps_live_*.png`, loaded via `bpy.data.images.load(png)` **without** `img.pack()`, and the file is then removed in `finally`. The datablock's `filepath` permanently references a file that no longer exists.
- Trigger: run "Apply as live modifiers", save the .blend, reopen it.
- Impact: on reload Blender cannot decode the image (missing file) → the texture reads as black/empty → with `mid_level = 0.0` the Displace produces zero displacement, so the entire non-destructive relief silently vanishes while `obj["ps_live"]` is still set — the panel still offers "Commit live / Revert", so the user has no clue the relief is gone.
- Fix: pack the image (`img.pack()`) before deleting the temp file, or write the PNG to a stable per-project path and leave it there (and only then `img.filepath = ...; img.reload()` on subsequent builds).

**[MEDIUM] `live_commit` bakes the live stack with all other modifiers disabled, then re-enables them — silently swapping modifier order** - `line 3130` / `line 3160`
- What: `others = [(m2, m2.show_viewport) for m2 in obj.modifiers if m2.name not in ("PS_Live_Subd","PS_Live_Displace")]` then `m2.show_viewport = False` for all of them, `new_from_object(...)` is evaluated, `obj.data = baked`, and `others` are restored afterwards. The live modifiers are always appended last (`line 3048`, `3060`), so before commit the evaluation is `live(others(base))`; after commit it is `others(live(base))`.
- Trigger: any object that has an existing modifier (Mirror, Subsurf, Boolean, Weld…) and uses "Commit live relief".
- Impact: the committed geometry differs from what the viewport showed immediately before the commit — e.g. a preceding Subdivision now smooths the already-displaced mesh instead of feeding it; a preceding Mirror mirrors the displaced result rather than the source. The change is silent and irreversible once the operator reports "Live relief baked".
- Fix: either evaluate with `others` enabled and *remove* them from the stack as part of the commit (bake everything, like `_punch_holes` now does), or refuse to commit when `others` is non-empty and tell the user why. Reordering them after the bake without rebuilding the base is not equivalent.

**[MEDIUM] `ai_load_scan` bypasses the shared `_AI_RUN` guard while it claims the slot** - `line 9110` (class at `line 9083`)
- What: every other paid/free AI operator declares `poll()` → `_ai_guard_poll(cls)` and re-checks `_ai_busy()` in `invoke()` (`line 7921`, `8460`, `8730`, `8250`). `PATTERNSKIN_OT_ai_load_scan` overrides neither, yet calls `_ai_begin("Load saved scan")` at `line 9110`.
- Trigger: start a paid `PATTERNSKIN_OT_ai_parts` scan (its modal returns `PASS_THROUGH` for every non-`TIMER` event, so the panel stays clickable), then click "Use saved scan (free)".
- Impact: the second operator overwrites `_AI_RUN["op"]`; when the paid scan's `_end()` runs it clears the slot out from under the restore, and both writers race `_AI_PARTS_CACHE[obj.name]`, the `ps_ai_part` attribute and `ps_ai_partcol` — a free restore of stale labels can land on top of a paid scan's fresh result (or vice-versa), leaving `ai_parts_count`, the attribute and the colors mutually inconsistent.
- Fix: add `@classmethod def poll(cls, context): return _ai_guard_poll(cls) and _SelMesh.poll(context)` plus an `if _ai_busy(): return {"CANCELLED"}` guard in `invoke`/`execute`.

**[MEDIUM] Pick modals raycast on every event without confirming the event came from a 3D viewport region** - `line 7338` (callers `line 7384`, `7477`, `9614`)
- What: `_raycast_pick_face(obj, context.region, context.region_data, event)` calls `view3d_utils.region_2d_to_origin_3d(region, rv3d, co)`, which dereferences `rv3d`. `PATTERNSKIN_OT_sel_click.modal` (`line 7404`), `PATTERNSKIN_OT_sel_strokecut.modal` (`line 7504`) and `PATTERNSKIN_OT_ai_pick.modal` (`line 9610`) do not test that `event` originated in a `VIEW_3D` `WINDOW` region, and none of the three wrap `_raycast_pick_face` in a `try`.
- Trigger: while "Pick on the model" / "Split with a stroke" / AI "Pick on model" is armed, left-click anywhere outside the 3D viewport — the add-on's own N-panel sidebar, the Outliner, or the Properties editor (all yield `context.region_data is None`, and other areas yield a different `context.area` entirely).
- Impact: `AttributeError`/`TypeError` escapes `modal()` instead of taking the `_ui_teardown()` path, so the operator dies with a Python traceback and the modal cursor (`EYEDROPPER` / `PAINT_BRUSH`) and the status-bar text stay stuck until Blender restarts; `cancel()` cleanup never runs.
- Fix: early-return `{"PASS_THROUGH"}` when `context.area is None or context.area.type != "VIEW_3D" or context.region_data is None`, and wrap the raycast in `try/except` falling back to `face = -1`.

**[MEDIUM] Modal state machines dispatch on bare `event.type == "TIMER"` — foreign timers drive them** - `line 691` (worst case `line 8868`)
- What: no operator in this file checks `event.timer is self._timer`. Blender posts one `TIMER` event per registered timer to the window's handler stack; `_PSCancellableApply` arms a **0.01 s** timer (`line 646`) while `PATTERNSKIN_OT_ai_parts_native` arms a **3.0 s** one (`line 8772`).
- Trigger: start a long Apply on a large mesh (its modal returns `PASS_THROUGH` for non-`TIMER`, so the panel stays live), then start a Native-3D scan — both modals are in the handler list at once.
- Impact: the scan's `p3sam_poll` (`line 8868`) is driven by Apply's 100 Hz timer instead of its own 3 s timer — a burst of polling that trips the Replicate rate limit; after 5 consecutive failures (`line 8874-8878`) the operator `raise`s and aborts a **paid, still-running** prediction. (In the alternative dispatch ordering the inverse happens: Apply's subdivision and the scan each stop receiving their own `TIMER` events and hang.) The same unfiltered pattern affects `_PSCancellableApply.modal`, `install_accel`, `check_updates`, `generate_default_library` and `self_update`.
- Fix: `if event.type == "TIMER" and event.timer is not self._timer: return {"PASS_THROUGH"}` in every modal handler (store the handle returned by `event_timer_add`).

## Missing safeguards

- No test exercises `PATTERNSKIN_OT_ai_load_scan` past its first modal tick — that is precisely why a missing `.start()` shipped (see HIGH above). The AI operators' modal state machines (`render`/`wait`/`finalize`/`fetch_wait`/`import`/`poll`) have no coverage that asserts `_fin_res`/`_res` were actually populated before unpacking.
- `_find_library_type` (`line 936`) omits the `os.path.basename(root) == "previews"` exclusion that `_scan_library` applies (`line 885`), so a preset's texture can resolve to a file inside a `previews/` folder that the browser deliberately hides — the pick then can't be re-clicked from the icon view.
- `index_url` allowlisting (`line 3311-3313`) validates only `urlparse(...).hostname`; the scheme is never checked, so `http://download.pytorch.org/...` (cleartext pip index → MITM on an optional-dependency install) passes the allowlist that exists specifically to harden the supply chain.
- `_safe_extract_zip` (`line 1700`) sizes its bomb guard from the attacker-controlled central-directory `file_size` and then does `src.read()` (whole member in RAM), whereas the library installer counts *actual* decompressed bytes (`line 5913`). Only sha256-pinned zips reach it today, but the guard should not depend on that.
- `apply_pattern` / `api_apply` perform no input validation on `tile_mm`, `obj.type`, or view-layer membership before mutating (`line 235-245`): `tile_mm=0` reaches `_dispatch_projection` (divide-by-zero → NaN UVs), a non-mesh or an object outside the view layer raises an opaque `AttributeError`/`ValueError` deep inside rather than a user-facing error.
- `_AI_PARTS_CACHE` (keyed by `obj.name`, `line 7522`) and `_AI_SHADE_PREV` are never evicted; renaming objects strands entries and the overlay shading restore for the session.