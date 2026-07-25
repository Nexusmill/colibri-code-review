# Colibri review — PatternSkin/__init__.py — bug

- **Source:** PatternSkin/__init__.py (C:\Users\User\source\repos\Nexusmill\PatternSkin\__init__.py)
- **Model:** claude-fable-5 (in-session, max)
- **sha256:** c09725612401db7be76895a23b27ace91e236979dedcc2f32bfdec0d2cfda09f
- **Date:** 2026-07-22 · **Mode:** bug · 6111 lines / 308078 bytes, read end-to-end
- **Context pack:** jCodemunch outline (358 symbols) + full def/class map; import-seam proof against projections.py / heightmap.py / presets_data.py / accel.py / selectcore.py / ai_parts.py / filmstrip.py / keystore.py / replicate_client.py / printfit.py / spector_bridge.py (every imported name located at its definition line); docs/deferred_manifest.json PSK-1..15; G35 exclusion list honoured (fixes verified present, not re-reported).

## Verdict
Shippable for the established flows — the seams of the fresh PSK-13 decomposition are clean (all re-imports/re-exports verified complete both directions, `_HM_CACHE` shared by mutation only, filmstrip's late package import fully bound). The single biggest risk is the accelerator-install pipe deadlock: exactly the verbose pip failures the installer was built to surface can instead hang it forever with a zombie pip mid-write in the shared modules dir.

## Bugs & vulnerabilities

**[HIGH] pip install can deadlock on a full stdout pipe; no user cancel** - `line 2078` (read at 2098-2106)
- What: `PATTERNSKIN_OT_install_accel.execute` starts pip with `stdout=PIPE, stderr=STDOUT`, but nothing reads the pipe until `poll()` returns non-None (modal L2098 polls, L2106 reads only after exit).
- Trigger: any pip run whose combined output exceeds the OS pipe buffer before exit — likeliest on the GPU path (panel L4471 passes `no_deps=False`, so torch/torch-directml resolve full dep trees), with `--force-reinstall` per-package output, and above all on failures (resolver/conflict output is multi-KB). Windows pipe buffers are small (~4-64KB).
- Impact: pip blocks writing → `poll()` never completes → status animates "Installing (Ns)…" forever, `_INSTALLING` stays set (all install buttons disabled), pip child hangs mid-write into the shared `--target` modules dir (partial package tree). The modal handles only TIMER events — there is no ESC/cancel — so recovery is restarting Blender. The design goal "nothing fails silently" (docstring L2033-2035) is defeated precisely in the verbose-failure case.
- Fix: redirect stdout to a temp file (`stdout=open(tmp,"w")`) and read it after exit, or drain the pipe from a reader thread; add an ESC branch in `modal()` that terminates the child via the existing `cancel()` logic. (`check_updates` L2190 shares the pattern but `pip list --outdated --format=json` output is reliably tiny.)
- Verification: CONFIRMED (mechanism traced end-to-end; trigger is output-volume dependent).

**[MEDIUM] `_previews_reset()` leaves `_ENUM_CACHE`/`_ENUM_SIG` pointing at freed preview icons** - `line 537` (vs 495-515; trigger 3199)
- What: `_previews_reset` removes the `_PREVIEWS` collection (freeing every loaded thumbnail's icon_id) but never clears `_ENUM_CACHE`/`_ENUM_SIG` (grep: only `_library_items` ever writes them).
- Trigger: any `_previews_reset()` call after which the library file list is unchanged — the "Refresh library" button itself (L3199), `choose_pattern` picking an external file (L3935), `make_seamless` on a file outside the library folder (L3187). Next redraw: `_library_items` recreates `_PREVIEWS` empty, `sig == _ENUM_SIG` → returns the cached tuples whose icon_ids reference the freed collection.
- Impact: the big `template_icon_view` pattern picker (L3960) renders dead/blank thumbnails until the folder's file list actually changes (new/removed file) — i.e. clicking "Refresh library" with nothing new breaks the browser it is meant to refresh.
- Fix: in `_previews_reset`, also `_ENUM_CACHE = []; _ENUM_SIG = None` (module-global rebind), forcing the next items call to reload previews.
- Verification: CONFIRMED (code path traced; no other reset site exists).

**[MEDIUM] apply_pattern failure after subdivision silently leaves the mesh densified** - `line 181` (failure window 215-300; operator catch 1592-1604)
- What: subdivision is committed to the mesh (`bm2.to_mesh(me)` L181) before projection/sampling/displacement run. An exception in the later phase (realistic: GPU/`cupy` OOM or `MemoryError` inside `accel.sample_tiled_xp` at L256/266 on meshes near the 700k budget) aborts the apply after the mesh has gained up to `max_faces` of geometry.
- Trigger: Apply on a large mesh with a failing/overloaded accel backend, or any unexpected error between L184 and L323.
- Impact: operator reports the error and returns CANCELLED (no undo push), so the user's mesh is silently subdivided (often massively) with no relief and no message that it changed; a save afterwards makes it permanent. (Ctrl+Z does restore the previous pushed state, but nothing tells the user to press it.)
- Fix: cheapest honest fix — in the operator's except path, detect that face count changed and extend the error report ("mesh was subdivided for the apply — press Ctrl+Z to restore"); a fuller fix snapshots the mesh (or wraps phase 2 and restores from the pre-subdiv bmesh copy) on failure.
- Verification: CONFIRMED mechanism (half-modified state guaranteed for any phase-2 exception); the specific GPU-OOM trigger is environment-dependent.

**[LOW] Preview failure path orphans the duplicated mesh datablock** - `line 2630` (dup created 2605)
- What: `PATTERNSKIN_OT_preview` copies the mesh (`dup.data = obj.data.copy()` L2605); the exception path removes only the object (`bpy.data.objects.remove(dup)` L2630), orphaning the copied Mesh — unlike the two PSK-11-fixed sites which explicitly remove it (`_clear_previews` L2569-75, apply rollback L1595-98).
- Trigger: preview apply raises (bad pattern, memory, etc.).
- Impact: 0-user mesh datablocks accumulate per failed preview until save/reload purge. Residual gap of the closed PSK-11 cluster (distinct line, not a regression of the landed fixes).
- Fix: mirror the apply rollback: capture `_m = dup.data` before removal, then `bpy.data.meshes.remove(_m)` when `users == 0`.
- Verification: CONFIRMED.

**[LOW] Modal operators without cancel(): cursor/status/timer leak on forced termination** - `line 4810` (cluster)
- What: `sel_click` (cursor_modal_set + status_text at 4831-4832), `sel_strokecut` (4926-4927) and `ai_pick` (5701-5702) restore cursor/status only on their explicit RET/RMB/ESC exits; none defines `cancel()`, which is what Blender calls when it force-cancels a modal (file load, window close mid-modal) → the window cursor stays PAINT_BRUSH / PAINT_CROSS / EYEDROPPER. Likewise `check_updates` (timer L2195 + pip child), `ai_parts` (L5083), `sel_text` (L5230) and `ai_parts_native` (L5326) leak their `event_timer_add` timers (and check_updates its subprocess) on forced cancel. `install_accel` L2163-2173 implements exactly the right `cancel()` — the pattern exists in-file but was applied once.
- Trigger: File > New / Open (or closing the window) while one of these modals is live.
- Impact: stuck modal cursor until something else calls cursor_modal_restore; orphaned timers/child process until quit.
- Fix: add `cancel(self, context)` to each: restore status/cursor (pickers) / remove timer + terminate child (pollers).
- Verification: CONFIRMED (Blender modal-operator API contract).

**[LOW] `load_heightmap` uncaught in lithophane and batch apply → raw traceback instead of report** - `line 3218` (also 3275)
- What: `PATTERNSKIN_OT_lithophane.execute` (L3218) and `PATTERNSKIN_OT_batch_apply.execute` (L3275) call `load_heightmap` outside any try; it raises RuntimeError on corrupt/unsupported images, >64MB or external-ref SVGs, and SVG-without-CairoSVG.
- Trigger: pick a bad/SVG file as litho photo or batch texture.
- Impact: unhandled-exception popup with traceback instead of the clean `self.report({"ERROR"})` every sibling operator produces; no mesh is touched (raise precedes mutation). Error-path inconsistency only.
- Fix: wrap in try/except and report, as `PATTERNSKIN_OT_apply` L1558-1604 does.
- Verification: CONFIRMED.

## Missing safeguards
- `install_accel` modal has no ESC/user-cancel affordance at all (compounds the HIGH finding: a wedged install cannot be aborted from the UI).
- `_live_build` (L1750-53) silently falls back to the whole mesh when `selected_only` finds nothing selected — the bake path warns (`fallback_whole` L1610-11); live mode says nothing.
- Live re-apply leaks Image datablocks: each run `bpy.data.images.load(..., check_existing=False)` (L1849) creates a fresh image while the old `PS_Live_<obj>` orphans; `live_revert` removes modifiers/UV/vgroup but not the texture, image, or temp PNG.
- Stale comment L6044: "defined below register()" — `PATTERNSKIN_OT_copy_diagnostics` is defined at L4483, above `register()`.
- `_ps_kick_model_check` (L638) can stack multiple concurrent redraw timers on repeated rechecks (each self-terminates after 10 ticks; benign but untracked).

## Adversarially refuted during verification (not findings)
- Import seams: every name `__init__` imports from projections/heightmap/presets_data/filmstrip exists at the cited definition lines; every name filmstrip imports back from the package (14 names, L14-17) is bound before the L5956 import; `_HM_CACHE` is only mutated (never rebound) on both sides, so `_previews_reset()`'s `.clear()` reaches heightmap's cache.
- `accel.nearest(_outs, P)` argument order matches accel's contract (index into first arg per row of second) — feather math at L295-297 is correct.
- `_validate_provider_key` cannot raise (all paths return a tuple), so the unguarded cursor_set pair at L2447-2449 cannot strand a WAIT cursor.
- `_dispatch_projection` changes mode only for UV-missing/unknown inputs, both handled before dispatch in `_live_build` — no silent live-mode fallback path.
- sys.path hygiene: L21-26 removes the per-user modules dir at import; `accel.ensure_dep_path()` re-APPENDS it (Blender's numpy stays first) — invariant holds.
- G35 exclusions verified present in current bytes: PSK-9 lookahead L153-158, PSK-10 global gate L2051-57, PSK-11 cluster (atomic STL stamp L961-967, preset schema-validate L859-871, ai_pick −1 guard L5720-22, preview/apply mesh cleanup, SVG temp ordering heightmap.py L53-57), live crumple guards L1780-1837, `_build_scale_from_outline` → `_extrude_scale_mask` L2924, shared `_raycast_pick_face` L4796 (call sites 4841/4931/5715), deliberately-unregistered sub-panels (only `PATTERNSKIN_PT_panel` in `_classes`; drawn via `_PSShim`).
