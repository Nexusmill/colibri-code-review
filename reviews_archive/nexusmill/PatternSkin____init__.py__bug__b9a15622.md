# BUG review: PatternSkin\__init__.py

- source: `C:\Users\User\source\repos\Nexusmill\PatternSkin\__init__.py`
- model: xiaomi/mimo-v2.6-pro
- reviewed: 2026-09-24 07:35
- tokens: in 171183 / out 35188
- est cost: $0.1051

---

## Verdict
Not safe to ship as-is: a modal-teardown path permanently wedges the entire AI feature set, and `send_to_spector` builds a filesystem path straight from `obj.name` (real path traversal / arbitrary-file overwrite). Everything else is mostly robustness, but these two are user-visible breakage / data loss.

## Bugs & vulnerabilities

**[HIGH] Path traversal / arbitrary file overwrite via `obj.name` in export path** - `line 8583`
- What: `path = os.path.join(inbox, "%s_%s.stl" % (obj.name, time.strftime(...)))` uses the Blender object name verbatim as a filename component. Blender ID names may contain `/`, `\` and `..` (glTF/FBX imports routinely produce them). `open(path, "wb")` at line 5885/8585 then truncates whatever it resolves to. Note the sibling operators *do* sanitise (`bpy.path.clean_name(obj.name)` at lines 3395, 3444) — this one was missed.
- Trigger: an object named e.g. `../../../../home/user/.bashrc` (or `..\\..\\AppData\\...` on Windows), select a face, click *Send selection to Spector*.
- Impact: writes an STL blob to an arbitrary user-writable path, silently destroying any existing file there. Reachable from a malicious/imported `.blend` or model file.
- Fix: `safe = bpy.path.clean_name(obj.name) or "part"` and use `os.path.join(inbox, "%s_%s.stl" % (safe, ts))`; additionally assert `os.path.commonpath([os.path.abspath(inbox), os.path.abspath(path)]) == os.path.abspath(inbox)` before opening.

**[HIGH] `_AI_RUN` guard is never released when Blender force-tears-down an AI modal — bricks all AI buttons for the session** - `line 7149` (also 7437, 7613, 7838)
- What: `PATTERNSKIN_OT_ai_parts`, `sel_text`, `ai_parts_semantic` and `ai_parts_native` all claim the global slot with `_ai_begin()` (line 6844) and only release it in `_end()` (line 7425 etc.), which is reached solely from `modal()`. None of these four classes override `cancel()`. Blender calls `Operator.cancel()` on window close / file load / another modal grabbing input, so `_ai_finish()` never runs, `_AI_RUN["op"]` stays set, and `_ai_guard_poll()` (line 6883) greys every AI button forever. The 0.15s event timer also leaks. This is exactly the failure mode the repo already fixed for `install_accel` (see its `cancel()` docstring at line 3030) and for `_PSCancellableApply`.
- Trigger: start any AI scan, then close the window / File▸New / let another modal take over before it finishes.
- Impact: AI texture, AI parts, text-select and named-scan are all dead for the rest of the session, with a misleading tooltip ("…wait for it to finish, or press Esc" — Esc does nothing because the modal is gone). Worker threads and temp PNGs also leak.
- Fix: add to each of the four operators:
  ```python
  def cancel(self, context):
      self._end(context, {"CANCELLED"})
  ```
  and have `_end()` also `os.remove(self._png)` when set.

**[MEDIUM] `_PS_APPLY_BUSY` guard leaks if timer/handler registration raises — object permanently un-appliable** - `line 591`
- What: `_PS_APPLY_BUSY.add(obj.name)` / `self._ps_busy_name = obj.name` happen at lines 552–553, but the only release on this (interactive) branch is via `modal()`/`cancel()`. `wm.event_timer_add(0.01, window=win)` (591) and `wm.modal_handler_add(self)` (593) are outside any `try`. If either raises (closing window, no valid window, WM teardown), the exception propagates to `PATTERNSKIN_OT_apply.invoke`'s `except` → `_a_fail()` (line 2346), which does **not** release the guard.
- Trigger: click Apply while the window/area is being closed, or any WM error during timer creation.
- Impact: `obj.name` stays in `_PS_APPLY_BUSY` for the whole session; every later apply on that object raises *"…already being processed by another Pattern Skin apply"* with no way to clear it short of restarting Blender.
- Fix: wrap lines 588–594 in `try/except`; on failure call `self._ps_close_gen(); self._ps_release_busy(); self._ps_stop_timer(context)` and re-raise.

**[MEDIUM] `check_updates` re-introduces the exact pipe deadlock the file documents, and leaks the pipe** - `line 3269`
- What: `subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)` then `poll()` in `modal()` and only `stdout.read()` after exit (line 3283). `install_accel` deliberately switched to a file for exactly this reason (comment at lines 2915–2917: *"a chatty or failing pip … can exceed the OS pipe buffer and block forever while poll() never returns"*). `pip list --outdated` merges stderr, so a warning/conflict dump can fill the 4–64 KB pipe buffer and block the child forever while `poll()` spins. `self._popen.stdout` is never `.close()`d — not in `modal()`, not in `cancel()` (line 3308) — so each invocation leaks a pipe FD pair.
- Trigger: click *Check for updates* repeatedly; or a pip that emits >pipe-buffer of diagnostics.
- Impact: modal hangs at "checking for updates …" forever (timer keeps firing), plus a permanent FD leak per click.
- Fix: mirror `install_accel` — `tempfile.mkstemp` + `os.fdopen` for stdout, read the file after `poll()` returns, and close/remove it in `cancel()`/`_cleanup`.

**[MEDIUM] Unvalidated user-preset JSON raises inside a property `update` callback and can produce duplicate enum identifiers** - `line 4774`, `line 1329`
- What: `_user_presets()` (line 1290) only checks `isinstance(e.get("settings"), dict)`. `_load_preset` then does `s.autofit_tiles_hint = int(cfg.pop("autofit_tiles", 4))` at line 4774 with no guard (the `setattr` loop below *is* guarded, this line is not). Separately, `_preset_items` (line 1329) emits `("U:" + nm, …)` for every stored name without deduping or rejecting `""`, so two hand-edited entries with the same name yield duplicate enum identifiers.
- Trigger: put `"autofit_tiles": "abc"` (or two identical `"name"` values) in `~/.config/patternskin_user_presets.json`, then pick the preset in the dropdown.
- Impact: `ValueError`/`TypeError` escapes `_on_preset_selected` → persistent Blender update-callback error and a half-loaded preset; duplicate identifiers make the whole `obj_preset` enum callback raise on every redraw (the exact "PERSISTENT draw error" the comment at line 1282 says was fixed).
- Fix: in `_user_presets()` coerce `autofit_tiles` to `int` with a fallback, drop entries whose `name` is empty/duplicate after `_sanitize_preset_name`, and wrap line 4774 in `try/except`.

**[MEDIUM] `_default_library_dir()` returns an unvalidated JSON value that becomes a `StringProperty` default — add-on fails to register** - `line 752`
- What: `_d = _json.load(_fh).get("library_dir")` is returned as-is when truthy. `PatternSkinSettings.library_dir` uses `default=_default_library_dir()` (line 2026), evaluated at class-body time. `StringProperty(default=123)` / `default={}` raises `TypeError` during `register_class`, so the whole add-on fails to load.
- Trigger: `~/.asset-forge/settings.json` containing `{"library_dir": 123}` (corrupt file, or a buggy/compromised Asset Forge build).
- Impact: Pattern Skin does not register at all; the failure surfaces as an opaque traceback in the add-on prefs with no hint that another app's config caused it.
- Fix: `if isinstance(_d, str) and _d.strip(): return _d` at line 753.

**[MEDIUM] `bake_regions` silently textures the WHOLE mesh when a region group is empty** - `line 4655`
- What: `_br_start_current` sets `v.select` purely from group membership. If the vertex group exists but has zero members, every vertex is deselected and `_apply_prepare` (lines 102–107) converts that into `selected_only = False, fallback_whole = True`. `_ps_item_done` (line 4672) ignores `res["fallback_whole"]`, so the "nothing was selected" warning that `PATTERNSKIN_OT_apply` emits (line 2416) never fires here.
- Trigger: add a region, clear its vertices (or bake after a remesh that drops the group's weights), then *Bake all regions*.
- Impact: that region's pattern is destructively baked across the entire model, and the operator reports "Baked N region(s)" as a success.
- Fix: skip when the group has no weighted vertices (`if not any(...)`), or pass `fallback_whole` through and abort the item instead of falling back.

**[MEDIUM] `PATTERNSKIN_OT_grow` crashes on cancelling seed normals** - `line 2832`
- What: `sn = Vector((0,0,0)); for f in seed: sn += f.normal; sn.normalize()`. `mathutils.Vector.normalize()` raises `ValueError` on a zero-length vector. Selecting a closed region (all faces of a cube/sphere, or any selection whose face normals cancel) makes `sn ≈ 0`.
- Trigger: select all faces of a closed mesh, run *Smart-grow selection*.
- Impact: uncaught `ValueError` escapes `execute()`; the operator aborts with a raw traceback and the mesh mode was already switched to Edit.
- Fix: `if sn.length < 1e-6: sn = Vector((0,0,1))\nelse: sn.normalize()`, and only compute `sn` when `s.grow_region > 0` (it is unused otherwise).

**[LOW] Unclosed file handles in three hot paths** - `line 1518`, `line 5209`, `line 5320`
- What: `txt = open(p, encoding="utf-8", errors="replace").read(65536)` (`_zip_addon_version`), `_hl.sha256(open(tmp, "rb").read()).hexdigest()` (`install_default_library`), `hashlib.sha256(open(out, "rb").read())` (`_gen_lib_worker`). All rely on GC to close; the last two also read a 100 MB zip / PNG fully into memory.
- Trigger: every self-update, every library install, every generated-library entry.
- Impact: FD pressure during long runs (the library generator opens one per texture) and avoidable peak memory.
- Fix: `with open(...) as f: …`, and hash in chunks.

**[LOW] Temp `.glb` leaks when the native-3D result fails to download/parse** - `line 7919`
- What: `fd, glb = tempfile.mkstemp(...)` then `p3sam_download` / `p3sam_labels_from_glb` run before the `try: os.remove(glb)`. Any exception between them jumps to the outer handler at line 7945, which never cleans up.
- Trigger: network failure during `p3sam_download`, or a malformed returned GLB.
- Impact: orphaned multi-MB temp file per failure.
- Fix: `try/finally: os.remove(glb)` around the download+parse.

**[LOW] `_live_build` leaks image datablocks and temp PNGs on every re-run** - `line 2682`
- What: `_save_gray_png(tile_arr, png)` writes `ps_live_<name>.png` into `bpy.app.tempdir` (never deleted), then `bpy.data.images.load(png, check_existing=False)` creates a *new* image datablock each call (and `bpy.data.textures.get(...) or new(...)` reuses the texture but repoints it, orphaning the previous image).
- Trigger: click *Apply as live modifiers* more than once, or on several objects.
- Impact: growing `bpy.data.images` and a growing temp dir; on long sessions this is real memory/disk.
- Fix: `check_existing=True`, and `os.remove(png)` after the image is loaded (Blender keeps its own copy).

**[LOW] `ai_parts.modal` dereferences `self._res[0]` without a None check** - `line 7321`
- What: the `wait` branch does `self._ap.assign_view(self._job, self._i, self._res[0])` after only checking `if self._err:`. The sibling `wait_sdf` branch correctly guards with `if not self._err and self._res:` (line 7347). If `_sam2_masks` returns `None` without raising, this is a `TypeError`.
- Trigger: a SAM-2 call that returns an empty/None payload without an exception.
- Impact: the whole scan aborts with "AI Parts error: 'NoneType' object is not subscriptable" after the view was already paid for (the checkpoint at line 7336 is skipped).
- Fix: `if self._err or not self._res:` → treat as a missed vote, matching `wait_sdf`.

**[LOW] Sync-path multi-item queues recurse once per object** - `line 573`
- What: in `bpy.app.background`/windowless mode `_ps_start` drains synchronously and then calls `self._ps_item_done()`, which for `batch_apply`/`bake_regions`/`ai_bake_parts` calls `_ps_start()` again for the next item — one stack frame per object. The comment at line 4500 claims the queue "must not grow the call stack per skip", but only the *skip* path is a loop; the success path is recursion.
- Trigger: `bpy.ops.patternskin.batch_apply()` over ~1000 selected meshes in `--background`.
- Impact: `RecursionError` near the default limit; the remaining items each fail with a warning instead of being processed.
- Fix: make `_bq_start_current`/`_br_start_current`/`_ap_start_current` return a sentinel that the *caller's* loop advances, or have `_ps_start`'s sync branch return without invoking `_ps_item_done` and let an outer `while` drive the queue.

**[LOW] `shade_smooth_by_angle` operates on whatever object happens to be active** - `line 452`
- What: `_apply_pattern_rest` calls `bpy.ops.object.shade_smooth_by_angle(...)` with no active-object guard. The decimate block right below correctly does `bpy.context.view_layer.objects.active = obj` (line 460). In the modal path `_apply_pattern_rest` runs a full event-loop turn after `_subdivide_stepwise`, so the user can have changed the active object.
- Trigger: start a long Apply, switch the active object before the rest phase runs.
- Impact: the wrong object's shading is changed; the target keeps flat shading.
- Fix: `bpy.context.view_layer.objects.active = obj` before the shading call (as line 460 already does).

**[LOW] Silent failure: AI texture is left non-seamless with no warning** - `line 3699`
- What: `make_seamless(load_heightmap(out, …))` + `_save_gray_png(…, out)` is wrapped in a bare `except Exception: pass`. The docstring promises "seamless by default", and `_update_seam_score` is then called on the *unfixed* file, but `generate_ai` reports unqualified success.
- Trigger: any failure in `make_seamless`/`_save_gray_png` (read-only library dir, corrupt decode).
- Impact: a paid texture silently ships with visible grid seams; the user only finds out after baking.
- Fix: catch, and set `s.ps_seam_score` from `tiling_score` of the raw result + report a `WARNING` that seam-fixing failed.

**[LOW] `ai_settings.draw` decrypts the stored API key on every redraw** - `line 3513`
- What: `have = bool(secret_get(kn))` materialises the secret just to test presence; `token_present()` / `secret_is_plaintext` already exist for this. `draw()` runs on every UI repaint.
- Trigger: open the *AI provider key* dialog and leave it open.
- Impact: the plaintext key is repeatedly decrypted into Python memory (and on macOS may re-prompt the keychain), widening the window for a memory/dump exposure.
- Fix: use `token_present()` (or a `secret_exists()` that never decrypts) for the `have` flag.

**[LOW] Unbounded numeric properties allow memory exhaustion from scripts** - `line 1946` (also 1759, 1822, 1843)
- What: `litho_res: IntProperty(min=40, soft_max=800)` has no `max`, and `PATTERNSKIN_OT_lithophane` allocates `2·nx·ny` Python tuples (line 4437). Likewise `tile_mm`/`grip_tile_mm`/`scale_len_mm` use `soft_max` only.
- Trigger: `bpy.context.scene.pattern_skin.litho_res = 200000` then *Make lithophane*.
- Impact: multi-hundred-GB allocation → OOM kill of Blender. Self-inflicted via script, but `soft_max` is not a limit and nothing else bounds it.
- Fix: add hard `max=` to these properties (e.g. `litho_res` `max=2000`) and clamp in the operator.

**[LOW] `_check_update` reads the version manifest with no size cap and opens a server-supplied URL** - `line 1429`
- What: `data = json.loads(r.read().decode("utf-8"))` — unbounded body from `nexusmill.com`. `info.get("url")` / `zip_url` are then handed to `bpy.ops.wm.url_open(url=…)` (lines 5011, 5015, 6217) with no scheme check (contrast `_verified_fetch`, which pins https + host).
- Trigger: a compromised or MITM'd `nexusmill.com` response.
- Impact: memory blowup on a huge body; `url_open("file:///…")` or a phishing URL rendered as a first-party "What's new" button.
- Fix: cap the read (`r.read(65536)`), and only pass `url` to `url_open` when `urlparse(url).scheme in ("https", "http")` and the host is `nexusmill.com`.

## Missing safeguards
- No `cancel()` override on `PATTERNSKIN_OT_ai_parts`, `sel_text`, `ai_parts_semantic`, `ai_parts_native`, `PATTERNSKIN_OT_self_update` — every other modal operator in the file has one. Add a test that force-cancels each modal operator and asserts the corresponding global guard (`_AI_RUN`, `_INSTALLING`, `_PS_APPLY_BUSY`, `_GEN_LIB`, `_ML_WORKER_INSTALLING`) is empty afterwards.
- `_punch_holes._apply` (line 4001) does `bpy.data.meshes.remove(old)` with the default `do_unlink=True`; on a multi-user mesh (linked duplicate) this destroys the other objects' data. Guard with `if old.users == 0` or `remove(old, do_unlink=False)` after rebinding, and add a linked-duplicate test.
- `_safe_extract_zip` and the library installer both use `os.path.commonpath` without `os.path.normcase`; add a case-mismatch traversal test on Windows.
- Self-update trusts `zip_sha256` from the network `version.json` (TOFU), whereas the default library uses a hardcoded pin (line 1413). Consider shipping an offline public-key signature over the update manifest.
- `_apply_pattern_rest`'s `except Exception: pass` blocks (feathering line 441, UV-collapse line 385, `make_seamless` line 3699) swallow real failures with no log line — at minimum `_log.warning(...)` each.
- No validation that `obj.data` is still the mesh `_apply_pattern_begin` prepared when `_apply_pattern_rest` finally runs (object deleted/re-meshed during the modal gap) — a `ReferenceError`/shape-mismatch here is caught generically and reported as a confusing apply error.
- Missing tests: empty vertex-group region bake; object-name with `/` through `send_to_spector`; corrupt `~/.asset-forge/settings.json`; corrupt/duplicated `patternskin_user_presets.json`; batch apply over >1000 objects in `--background`; force-cancel of every modal operator.

---

## In-session adversarial verification + remediation (2026-09-24, colibri Phase 3/4)

**Verification:** 17 of 19 findings CONFIRMED against current bytes; 1 REFUTED (F12: ai_parts._sam2_masks
returns `(label, len(masks))` or raises - never None, so `self._res[0]` behind the `_err` check is safe;
the adversary independently confirmed); 1 SPLIT (F16: litho_res hard-capped at 2048; blanket hard max= on
tile_mm/grip_* refused - the file's own PSK-TILEFLOOR comment records hard property bounds locking out
legitimate values, and no allocation hazard exists behind them). The advisory _punch_holes do_unlink
destruction verified real, promoted to a fix (F18).

**Adversary gate (owner-ordered):** the remediation plan went to an independent adversary subagent
(feature-dev:code-reviewer, 49 tool reads) BEFORE any edit. Verdict APPROVE WITH MODIFICATIONS; all five
MODIFYs folded in: F3 += _ps_stop_timer in the failure cleanup; F4 execute-path file cleanup; F10 the
invoke-side glb leak; F11 an ownership gate on image reuse (mimo's check_existing=True advice REJECTED -
same-path overwrite returns the stale datablock without re-reading); F13 += select_set. Plus one scope
add: self_update.cancel() (F20, its 0.2s timer leaked on teardown the same way).

**Fixes applied** (28 safe_replace edits, py_compile-clean; post-remediation sha256
efdea57421b07c7dc75fda8b982df169b7aa0fe3d0ed97fe1564eecbf9bda948): F1 clean_name; F2 cancel() on the four
AI modals + guarded areas loop in each _end; F3 registration try/except; F4 pip stdout to temp file;
F5 preset sanitize/dedupe + guarded int; F6 library_dir type guard; F7 empty-region skip; F8 zero-normal
guard; F9 with-blocks + streamed _sha256_file; F10 glb try/finally (both paths); F11 tag-gated image
reuse/reload; F13 scoped active+selection (EXTENDED mid-verification: the probe caught the drifted decoy
still being smoothed - the op is selection-scoped, not active-scoped; neither reviewer nor adversary had
that); F14 seam-failure disclosure; F15 per-provider key cache; F16 max=2048; F17 read cap + url scheme
guard; F18 old.users guard; F19 _PS_SYNC_QUEUED trampoline; F20 self_update.cancel().

**Tests:** new tests/test_hunt_r1_fixes.py (headless blender 5.1.2) 21/21 PASS - includes the trampoline
re-entrancy path (2 real regions + 1 empty), hostile-preset load, traversal probe, dead-context cancel
drive, linked-duplicate punch, decoy-drift shading. tests/test_blender_smoke.py ALL PASSED.
F3/F4/F20 verified by construction + adversary only (background mode cannot reach them) - flagged for a
windowed teardown smoke. Remediation manifest: 19 rows appended (3 honestly labeled by-construction).
**NOT COMMITTED** - owner order: this experiment bypasses the gate until the three agents clear.
