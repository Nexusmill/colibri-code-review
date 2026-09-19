# Colibri Review - bug (FULL re-audit) - PatternSkin/__init__.py

- **Source path:** `PatternSkin/__init__.py` (junction twin `blender_dev/addons/PatternSkin/__init__.py` = same bytes)
- **Reviewer:** claude-fable-5-1 (fork of the lead session), Colibri G37 protocol, campaign item 1 (product cores), hunt-plan rank 1, round 4
- **sha256 reviewed:** `5f4f0473f347e87aed47b3ead0a8efa26c6b58515a97de69ca08b6988593b325` (sha8 `5f4f0473`) - 8918 lines, every line read
- **Date:** 2026-09-10 · **Mode:** bug, FULL review of the current bytes (owner ruling 2026-09-10: this file's prior audits - 07-21..08-13 rounds, the 08-13 ultra gates, this morning's round-3 delta - predate the adversarial gate and cannot be trusted; no delta against them)
- **Context pack:** jCodemunch `get_file_outline` (708 symbol rows) + `find_importers` (18 importers: ai_parts, filmstrip, heightmap, keystore, keyvault, projections, the bpy harness/probes, test_blender_smoke); the 40 remediation rows, 12 deferred rows and 25 feature-registry rows naming the file loaded as CLAIMS; the prior review records `.colibri_reviews/PatternSkin____init__.py__*` (10 files) read as claims; call sites of `_ps_start`, `_scan_library`, `_verified_fetch`, the register()-time timers traced; `accel.finish_pending_installs_async` callers traced (`_auto_ensure_deps` is its ONLY caller). Blender 5.1.2 facts verified live (timer purge on file load; startup-with-.blend ordering).

## Verdict
Not shippable as-is on the most common launch path: **every startup timer the add-on registers is purged by the .blend a user double-clicks** (HIGH), so on that path the dialled-in settings never come back, the "queued - completes automatically on startup" install never completes, SciPy is never repaired, support replies never surface and the AI model check never runs. Four more CONFIRMED defects (one MEDIUM: headless multi-item bakes bake only their first item and batch leaves objects stuck busy; three LOW: two temp-file leaks / a fixed temp name, a silent picker cap). All five reproduced RED by batteries A-D and watched GREEN on a scratch copy carrying the proposed fixes (`fixes_ps_init.py`, 13 exact replace_in_file pairs); the existing r3 and reveal_and_pick batteries stay green on that copy. The rest of the file - the cancellable apply mixin, the self-update two-phase install + rollback, the pinned/redirect-free fetch, the zip containment, the pip allow-list, the key/vault dialogs, the selection tools, the three paid scans' money-safety streaks, the filmstrip hand-off - holds at the bytes.

## Bugs & vulnerabilities

**[HIGH] Every register()-time startup timer is non-persistent, and the .blend a user double-clicks purges them before they fire** - `line 8829` (`_support_startup_check`), `8842` (`_auto_ensure_deps`), `8846` (`_scipy_reprobe`), `8862` (the model-check lambda), `8870` (`_restore_session_settings`); only `8866` (`_ps_autoload_tick`) is `persistent=True`
- What: `bpy.app.timers.register(..., persistent=False)` timers are removed on every file load (verified in this session on 5.1.2). When Blender is started with a .blend argument - double-clicking a file, the common launch - add-ons register during `WM_init` and the file loads BEFORE the event loop runs a single timer. Verified for real: `blender -b --factory-startup --addons PatternSkin scene.blend --python check.py` (BLENDER_USER_SCRIPTS = blender_dev) reports the add-on registered, the file loaded, and `_restore_session_settings`, `_auto_ensure_deps`, `_scipy_reprobe`, `_support_startup_check` all UNregistered while the persistent `_ps_autoload_tick` survives; in-process `open_mainfile` after `register()` shows the same purge.
- Trigger: any launch of Blender by opening a .blend (file association, recent-files list, `blender file.blend`).
- Impact: on that path, per session: session settings not restored (`_restore_session_settings`); `accel.finish_pending_installs_async()` never runs - its ONLY caller is `_auto_ensure_deps` - so the install_accel promise at line 2957 ("Restart Blender - this install is now QUEUED and completes automatically on startup") is broken and the user loops on the WinError-5 lock; `repair_scipy_async` never runs (a broken SciPy stays broken, the selection tools stay greyed); the model-availability check never runs (AI buttons show "unknown"); unread support replies never surface. Users who start Blender empty never see any of it, which is why it survived every prior round.
- Fix: `persistent=True` on the five registrations (each still runs once - they return None), the model-check lambda becomes a named `_ps_model_check_once` so `unregister()` can remove it, and `unregister()`'s removal tuple gains `_restore_session_settings`, `_support_startup_check`, `_ps_model_check_once` (reload safety). The EV-065 shape the gate accepted this morning for the gen-lib release timer. Row id PS-STARTUP-TIMERS-PURGED.
- Verification: CONFIRMED. Battery `probe_ps_init_3.py` (`PSI_startup_timers_survive_file_load`) RED on the bytes, GREEN on the fixed copy.

**[MEDIUM] The background / window-less branch of `_PSCancellableApply._ps_start` releases the per-object busy guard only AFTER `_ps_item_done`** - `line 556-566`
- What: `_ps_release_busy()` sits in a `finally` around `return self._ps_item_done(...)`. The three multi-item operators (`bake_regions` 4639, `ai_bake_parts` 8016, `batch_apply` 4495) start their NEXT item from inside `_ps_item_done` → the nested `_ps_start` runs while the outer item's name is still in `_PS_APPLY_BUSY` (and overwrites `self._ps_busy_name`, so the outer name is never discarded). The modal TIMER branch (line 624) releases BEFORE the callback - the two branches disagree, and the docstring's "byte-for-byte the old apply_pattern() behaviour" claim is false for any queue longer than one.
- Trigger: `bpy.app.background` or `context.window is None` (headless scripts, the feature harness, any window-less EXEC_DEFAULT call) with ≥2 regions / assigned parts on one object, or ≥2 objects in a batch.
- Impact: same-object queues - `bake_regions` / `ai_bake_parts` - refuse every item after the first with "'X' is already being processed by another Pattern Skin apply" and report "Baked 1 region(s)" (captured verbatim); `batch_apply` finishes but leaves every object except the last in `_PS_APPLY_BUSY` for the session, so a later Apply on any of them is refused. Interactive (modal) runs are unaffected.
- Fix: release before the callbacks in the background branch, mirroring the modal branch (the subdivision-phase exception now also routes through `_ps_item_failed`, which every caller handles identically - apply → `_a_fail`, queues → warn + skip). Row id PS-BUSY-BG.
- Verification: CONFIRMED. Battery `probe_ps_init_1.py` - three checks (regions on one object, batch of two objects then Apply on the first, parts on one object) RED on the bytes with the exact warnings above, GREEN on the fixed copy; `sweep_ps_init_r3_bpy.py` + `reveal_and_pick_bpy.py` still green on the copy.

**[LOW] `_self_update_worker` creates its download zip before the try/finally that removes it** - `line 1549-1552` vs `1555/1634`
- What: `mkstemp` + `_verified_fetch` run above the inner `try:`, whose `finally` is the only removal. Any raise from the fetch - the user's Esc (`raise RuntimeError("cancelled")` at 1452), a sha mismatch, a network error - jumps to the outer `except` at 1638 with the partial file still on disk.
- Trigger: Esc during the download (the operator's advertised cancel), or any failed download.
- Impact: up to the 600 MB cap left in the user's temp dir per attempt, silently; repeated cancels accumulate.
- Fix: wrap the fetch in try/except that removes `tmp` and re-raises. Row id PS-UPDATE-TMP-LEAK.
- Verification: CONFIRMED. Battery `probe_ps_init_2.py` check 1 (`_verified_fetch` monkeypatched to write bytes then raise "cancelled") RED: `ps_self_update_*.zip` left behind; GREEN on the copy.

**[LOW] `install_default_library` downloads to a FIXED temp name and leaves a mismatched download behind** - `line 5167`, `5173-5176`
- What: `os.path.join(tempfile.gettempdir(), "ps_default_library.zip")` - the exact hazard `_self_update_worker`'s own comment at 1550 names ("a FIXED name in a shared temp dir is a symlink target for another local user") and avoids with `mkstemp`; `open(tmp, "wb")` follows a pre-planted symlink. The integrity-mismatch `return {"CANCELLED"}` at 5176 is inside the first try (5166-5180), not the later one whose `finally` (5215) removes `tmp`, so the ~100 MB bad download stays on disk.
- Trigger: any download (multi-user machines with a shared /tmp for the symlink case; every integrity mismatch for the leak - the pin comment at 1387 says the served zip is currently expected to mismatch).
- Impact: a local co-user can redirect the 100 MB write over a file the victim owns; a refused download leaves 100 MB behind (bounded by the fixed name).
- Fix: `mkstemp(prefix="ps_default_library_", suffix=".zip")` and a `finally` on the download try that removes the file when it was not accepted. Row id PS-LIBDL-FIXED-TMP.
- Verification: CONFIRMED. Battery `probe_ps_init_2.py` check 2 (urlopen monkeypatched, canary file pre-placed at the fixed name) RED: the canary was overwritten and left; GREEN on the copy (no `ps_default_library_*.zip` remains, canary untouched).

**[LOW] The pattern picker silently truncates at 300 files, and the shipped library is exactly 300** - `line 761` (`_scan_library(folder, limit=300)`), `850` (`_library_items`), `5483` (icon view)
- What: `_scan_library` stops at 300 in walk/name order and nothing records that it stopped; `default_library_checksums.json` carries 294 images + the 6 curios = the 300-texture shipped zip, all flattened into `heightmap/` by the installer. The very first texture the user generates ("Generate one texture" lands in `heightmap/`) or adds pushes the library to 301 and whichever file sorts last is gone from the grid - no status, no row, `Refresh library` doesn't help; `_library_item` can never point at it.
- Trigger: shipped library installed + any added texture.
- Impact: the user's own textures (the BYO-key headline feature) can be invisible in the browser; the active pattern still works because `generate_ai` sets `s.pattern` directly, so it reads as "the library lost my file".
- Fix (UI honesty, R1-legal alert paired with the existing 'Use an external image...' action): scan one past the cap, record `_LIB_CAPPED`, draw an alert row under the icon view when it is set. Raising the cap is a separate call (icon-view thumbnail cost). Row id PS-LIBRARY-CAP-SILENT.
- Verification: CONFIRMED. Battery `probe_ps_init_4.py` (300 + 1 files → 300 items, the user's file absent, no cap flag) RED; GREEN on the copy.

## Missing safeguards
- `ai_parts` / `sel_text` / `ai_parts_semantic` modal Esc while a paid SAM call is in flight: the result lands after `_end()` and is discarded without checkpoint, and that view's temp PNG leaks (pre-existing; the parent's round-3 record notes the PNG).
- `_self_update_worker` never removes files the new version dropped - stale modules from an older release keep importing.
- `install_default_library` downloads ~100 MB synchronously on the main thread (Blender frozen, no progress), with no size cap and redirects honoured - `_verified_fetch` has all three protections; this path should share it (URL/host pin permitting).
- Background-mode queues in `_ps_start` recurse ~3 frames per item (`_ps_item_done → _bq_start_current → _ps_start`); a batch of several hundred objects headless would hit Python's recursion limit.
- `PATTERNSKIN_OT_support_send.execute` without `invoke` (EXEC_DEFAULT) raises AttributeError on `self._payload` (INTERNAL, button-only today).
- `_save_user_presets` / `_save_license` / `_save_session_settings` write their JSON in place (a crash mid-write truncates the file; `_user_presets` tolerates a corrupt file, the others fall back to {}).
- `PATTERNSKIN_OT_check_updates` still runs pip on a PIPE read only after exit - fine at today's output size (see refuted), fragile if the tracked set grows.

## Adversarial verification pass (refuted claims - to `_refuted_ledger.json`)
- "check_updates has the install_accel pipe-buffer deadlock" - refuted: `pip list --outdated --format=json --path <modules>` emits a few hundred bytes for the handful of tracked packages; it cannot fill the 64 KB pipe.
- "`_library_items`' empty-library fallback is a separator item (the PSK-11 preset-enum bug)" - refuted as a live path: the panel draws the icon view only when `_library_empty()` is False, so reaching it needs every scanned file to fail preview loading.
- "apply_live leaks an Image datablock per run" - refuted: the previous image is unlinked from the texture and dropped on save/reload with 0 users; cosmetic.
- "TRIPLANAR bake displaces nothing on a 20-unit cube" (a fixture run showed zmax unchanged) - refuted: sampling alignment of the synthetic 8-px stripe tile at a 5-unit tile / 2-unit edge; a noise tile or a finer edge displaces normally.
- "'Selected faces only' on a coarse cube spreads to the whole mesh" - refuted as a regression: `subdivide_edges` tags the new verts on the side faces adjacent to the selected edges, so the selection legitimately grows with the cut geometry (documented anisotropic subdivision behaviour).
- "the update / self-update worker threads race draw() on `_UPDATE` / `_SELF_UPDATE`" - refuted: whole-value dict writes under the GIL, draw() reads whole values; no torn state.

## Notes for the lead
- Batteries: `probe_ps_init_1..4.py` (suggested repo names `tests/harness/probes/sweep_ps_init_r4_bpy.py`, `_r4b_`, `_r4c_`, `_r4d_`; they honour `PS_REPO_ROOT`); `run_probes.py` runs them; `fixes_ps_init.py` holds the 13 exact (old, new) pairs keyed by row id; `fixcopy/PatternSkin/__init__.py` is the proven fixed copy (py_compile clean).
- jCodemunch's index of `blender_dev/addons/PatternSkin/__init__.py` is stale (line numbers trail the junction source by 34) - reindex before trusting hits there.
- Pre-existing rows re-verified PRESENT in the bytes (not re-listed): PSK-9/10/11 clusters, the SVG guards (now in heightmap.py), the self-update two-phase install, KS-1, FS-1, PSK-ULTRA-2/5/6, PSK-AISEL-EXCLUSIVE, HY4-G19-SELTEXT, HY4-MV-STREAK, PS-TEXTSEL-REVEAL-NAMING, PS-GENLIB-GUARD-STUCK, PS-SEMSCAN-SETUP-RAW.

## Remediation postscript (same session)
The fixes were applied after this review hashed the bytes above; the file is now `5dfcd8c217838db95fb978793a96615e299128b1c7d7bdf0600a56d1bb859aa3`. Rows PS-STARTUP-TIMERS-PURGED, PS-BUSY-BG, PS-UPDATE-TMP-LEAK, PS-LIBDL-FIXED-TMP, PS-LIBRARY-CAP-SILENT in `docs/remediation_manifest.json`, same commit.

## Gate record (same session)
Round 1 of the batch gate (gate_20260910-124259, glm-5.3-flash) BLOCKed on two findings the change itself introduced,
both accepted: the PS-BUSY-BG rewrite of the background branch dropped the old unconditional `finally` release, so a
BaseException mid-apply (Ctrl+C on a `-b` batch, SystemExit) left the object in `_PS_APPLY_BUSY` - the early releases
stay and the section is wrapped in try/finally again (the release is idempotent); and two new batteries
(`sweep_accel_worker_r4_token.py`, `sweep_accel_r4_bpy.py`) were bound to this machine with no SKIP path. Docket EV-066.

