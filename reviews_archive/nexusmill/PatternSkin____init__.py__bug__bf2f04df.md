# BUG review: PatternSkin\__init__.py

- source: `C:\Users\User\source\repos\Nexusmill\PatternSkin\__init__.py`
- model: xiaomi/mimo-v2.6-pro
- reviewed: 2026-09-24 09:09
- tokens: in 181364 / out 33797
- est cost: $0.1083

---

## Verdict
The round-2 remediation all landed correctly (verified line by line — see "Fixed since last review"), and I found no new CRITICAL/HIGH issues. The single biggest remaining risk is that **`PATTERNSKIN_OT_self_update` has no run-guard at all**: two overlapping update runs (trivially started by clicking "Update now" twice during the multi-minute download) concurrently backup/replace/rollback the add-on's own files.

## Bugs & vulnerabilities

**[MEDIUM] `self_update` is re-entrant — two concurrent workers can interleave install/rollback and corrupt the add-on** - `line 6433`
- What: `execute()` does `_SELF_UPDATE.update(phase="start", ..., cancel=False)` (6433) then `threading.Thread(target=_self_update_worker, ...)` (6434) with **no `_INSTALLING`/`_AI_RUN`-style guard**. The panel keeps offering `patternskin.self_update` while a run is live (`_UPDATE["newer"]` never changes, 5197), and each new `execute()` also **resets `cancel=False`**, silently un-cancelling a run the user just Esc'd. Two `_self_update_worker` threads then interleave the two-phase install (1704–1731): `shutil.copyfile(dp, bak)` / `os.replace(new, dp)` / `os.remove(bak)` from thread A can land between thread B's backup and replace, and a rollback (1716–1723) restores `.psbak` files that contain the *other* thread's half-updated version. `_SELF_UPDATE["done"]`/`["ok"]` are shared, so the first finisher makes both modals report "Updated" while the second is still writing files.
- Trigger: click "Update now (one click)" → confirm; click it again while the zip (up to 600 MB) is still downloading; confirm again. Same class of bug in `check_updates` (3391): two clicks = two concurrent `pip list` children racing on `_DEP_UPDATES`.
- Impact: corrupted/rolled-back mixed-version add-on install (fails to import on restart), wrong completion status, and an Esc that stops working halfway. The exact failure mode the `_INSTALLING` gate (2991) was added to prevent, just on the one operator that never got a gate.
- Fix: add a module-level `_SELF_UPDATE_BUSY` flag claimed at the top of `execute()` (before the thread start) and released when the worker sets `done`; refuse the second run with "An update is already running." Do not reset `cancel` on a refused run; gate `check_updates` on the same or `_INSTALLING`.

**[MEDIUM] `_ai_write_colors` is a per-polygon Python loop — multi-second main-thread freeze on scan-sized meshes, fired automatically from a timer** - `line 8610`
- What: `for p in range(len(me.polygons)): ... cols[s:e, 0] = c[0]; cols[s:e, 1] = ...` (8610–8613) does ~5 numpy operations per polygon. On the 1.8M-poly meshes this file repeatedly cites as its design target that is seconds-to-tens-of-sseconds of unyielding work — the exact class of freeze G-HANG-1 (7418–7422) exists to eliminate, and the class `_ai_poly_part` (6977) was rewritten specifically to avoid. It runs inside `bpy.app.timers` via `_ps_autoload_tick` → `_ai_write_colors` (1118), i.e. **with no user action** beyond switching to a saved-parts object, plus after every scan / overlay toggle.
- Trigger: open a saved-parts `.blend` on a 1M+ face mesh (autoload), or finish any AI scan / toggle Show parts on one.
- Impact: Blender appears to hang for seconds per call (recurring: one per object switch), no progress feedback, same "users assumed a crash" symptom the rest of the file treats as a defect.
- Fix: vectorise — `cols = np.ones((len(me.loops),4), np.float32); rgb = np.where((polypart>=0)[:,None], pal[np.clip(polypart,0,None)], 0.5); cols[:,:3] = np.repeat(rgb, lt, axis=0)`, guarded for `polypart.max() < 0`. Add a timing assertion in the harness at 1.8M polys.

**[LOW] Multiview-scan checkpoint counts FAILED views as paid — a resume silently drops them forever** - `line 7540`
- What: on a failed view the code does `self._i += 1` **without** `save_scan_partial` (7538–7542, explicitly commented "the missed view is NOT checkpointed … a resume may retry it"). But the *next* successful view checkpoints `save_scan_partial(self._obj, self._job, self._i)` **after** its own increment (7558–7560, 7572–7574), so `done` jumps past the hole. Resume starts at `self._i = self._resume_done` (7467), i.e. strictly at `done`, so index 5 (failed) is never rendered, never assigned and never retried.
- Trigger: one transient SAM-2 failure mid-scan (tolerated by design), then a crash/quit, then re-open and resume.
- Impact: the checkpoint's "finished views are already paid for and will be reused" guarantee breaks — the resumed scan permanently loses one view's vote (degraded segmentation) and the pre-flight cost message ("Resumes at view N/M …") overstates what will actually be run. The stated resume contract in the 7525–7529 comment is false.
- Fix: checkpoint the *assignment state* (including empty views) at the same counter, or on failure set a `job["missing"]` marker and have `load_scan_partial` retry indexes `< done` with empty assignments.

**[LOW] `_PS_APPLY_BUSY` is keyed by `obj.name` — renaming the object mid-apply defeats the concurrency guard** - `line 562`
- What: the guard is `if obj.name in _PS_APPLY_BUSY: raise` (562) / `_PS_APPLY_BUSY.add(obj.name)` (567) / `discard(name)` (639). Rename the object while its modal apply is running and a second `patternskin.apply` on the same object passes the check (`"Sphere"` ∉ `{"Cube"}`) and starts a second `_subdivide_stepwise` against the same live mesh. (`api_apply` (2281) bypasses the guard entirely.)
- Trigger: start a long modal Apply, rename the object in the Outliner, click Apply again.
- Impact: exactly the lost-work the guard was written for — whichever `bm2.to_mesh(me)` lands last discards the other's subdivision, and `_apply_pattern_rest`'s `foreach_set("co", …)` (445) then runs against a vertex count its stale `co` array no longer matches (length-mismatch error or corrupt positions).
- Fix: key the set on `obj.as_pointer()` (or hold the object reference in a `dict`), and route `api_apply` through the same guard.

**[LOW] `_build_scale_from_outline` leaks the image datablock (and half-built state) when the pixel read fails** - `line 4275`
- What: `bpy.data.images.remove(img)` (4277) only runs on the success path. `img.pixels.foreach_get(arr)` (4276) or `arr.reshape(h, w, 4)` (4278) raising — a decode-tolerant load where `img.size` is set but the pixel buffer is empty/mismatched, or an unsupported-format file Blender "loads" with a 0-length buffer — skips the removal and leaves a `bpy.data.images` entry for every failed attempt. (The `w < 2 or h < 2` path at 4273–4274 does clean up.)
- Trigger: point "Outline" at a file Blender opens but cannot give `w*h*4` floats for, repeatedly.
- Impact: orphaned image datablocks accumulate in the session/.blend; the operator reports only "Outline build failed: …" with no hint that state leaked.
- Fix: wrap 4275–4278 in `try/except` that calls `bpy.data.images.remove(img)` before re-raising.

## Missing safeguards
- `Thread.start()` sits outside the guard-claim invariant the round-2 fix established for registration: `install_ml_worker` (3273 sets `_ML_WORKER_INSTALLING`, 3275 starts the thread) and `generate_default_library` (5600 sets `_GEN_LIB["active"]`, 5604 starts) strand their guard permanently if `start()` raises — unlike registration, the release lives only in the worker's own `finally`. Wrap the start in the same try/except → `cancel(context)` → `raise` pattern used at 3279–3285 / 5608–5614.
- `check_updates` has no single-instance gate (see first finding); add the `_INSTALLING`-style claim or reuse it.
- `_apply_finish`'s thin-band fix now returns `None` silently (2219–2221) — the user asked for a finish, gets none, and no warning is reported. Return a sentinel the operator turns into "finish skipped: no face fully inside the applied region".
- No test for double-invocation of `self_update` (assert the second `execute()` is refused and `cancel` is not reset) — same assertion valuable for `check_updates`.
- `_stamp_stl_header` (1427–1428) reads the entire STL into a `bytearray` (and builds a second copy for `os.replace`) — stream 80-byte patch + copy instead for multi-hundred-MB exports.

## Fixed since last review
All eight round-2 findings verified remediated in the current bytes:
- **R2-1** `sel_text.cancel()` is now at class-body indent (7856–7870) with the correct teardown (`_png` removal + `_end` fallback); the dead block after `_sem_price`'s `return` is gone (`_sem_price` is a clean one-liner, 7878–7881).
- **R2-2** All nine registration sites now wrap `event_timer_add`/`modal_handler_add` in try/except with per-operator release via `cancel()`/`_end()`/`_cleanup()`, an ERROR report and a re-raise: `install_accel` (3040–3053), `install_ml_worker` (3276–3285), `check_updates` (3417–3425), `generate_default_library` (5605–5614), `self_update` (6436–6444), `ai_parts` (7481–7489), `sel_text` (7747–7755), `ai_parts_semantic` (7943–7951), `ai_parts_native` (8185–8193). Background fail-fast added to `install_accel` (2985–2989) and `check_updates` (3393–3397).
- **R2-3** Selection restore moved into `finally` with the capture hoisted above `try` (454, 467–470).
- **R2-4** Thin-band path returns `None` before `materials.clear()` (2219–2221) — user materials survive.
- **R2-5** `_check_update` URL guard is now `https`-only + dot-boundary host allowlist (1484–1494).
- **R2-6** `_aa_pool` `k` bounded by both tile dims (337) — tall-narrow tiles no longer zero out `w0`.
- **R2-7** `unregister()` resets `_ENUM_CACHE`/`_ENUM_SIG` under a correct `global` (9269, 9290).
- **R2-8** `_live_build` removes the temp PNG in `finally` (2776–2780).

Plus the earlier batch (F1, F2 partial→now complete, F3–F11, F13–F20) all still hold.

---

## In-session verification + remediation (2026-09-24, round 3)

All 5 findings verified; the Preview-path question the adversary raised is resolved EXEMPT:
the 3986 caller bakes onto `dup.data = obj.data.copy()` (its own datablock), so no shared-mesh
race with a modal Apply - no guard routing needed. Adversary gate round 3: APPROVE WITH
MODIFICATIONS, all folded in: the busy release lives ONLY in the worker-tail finally (the
registration-except must NOT clear it - the worker is alive and uncancelled there);
_CU_BUSY claims after a live Popen and releases at modal-completion/cancel; the outline fix
owns a single removal site inside the finally; the SKIP sentinel intercepts BEFORE the caller's
viewport switch and finish_txt; _ai_write_colors gained a one-line canonical-loop-layout guard
with the slice loop as fallback; thread-start wrappers touch only .start(); the checkpoint
comment now states the verifiable claim (prevents the surprise re-bill, cannot recover
already-billed failures).

Fixes (16 edits): R3-1 _SELF_UPDATE_BUSY one-at-a-time claim (refusal keeps cancel intact;
start-failure clears directly; worker-tail finally is the single release) + _CU_BUSY for
check_updates; R3-2 _ai_write_colors vectorised (np.repeat explode, layout guard, fallback);
R3-3 missed views checkpointed-as-missed (resume == live semantics, no re-bill); R3-4 busy
guard re-keyed to obj.as_pointer() + api_apply routed through it; R3-5 outline image removed
in finally (single site); R3-6 start-only try/except for ml_worker/gen_lib thread starts;
R3-7 thin-band returns "SKIP" + caller WARNING (collision-free against the locked finish
table).

Tests: tests/test_hunt_r3_fixes.py 11/11 PASS (refusal semantics incl. cancel-untouched and
claim-retained; _CU_BUSY release; 98304-face vectorized rewrite in 0.02s with byte-color-exact
palette/grey/alpha match; api_apply refusal; SKIP sentinel). r1 21/21 + r2 13/13 re-pass
(r2's thin-band expectation updated to the SKIP contract); test_blender_smoke ALL PASSED.
Unreachable-headless branches (check_updates refusal, outline pixel-read failure) verified
by construction + source assertions. NOT COMMITTED (owner order).
