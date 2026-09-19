# Colibri Review - bug (DELTA) - PatternSkin/__init__.py

- **Source path:** `PatternSkin/__init__.py` (8884 lines; the paid Blender add-on's core)
- **Reviewer:** claude-fable-5-1 (in-session), Colibri G37 protocol, campaign item 1 (product cores)
- **sha256 reviewed:** `6b3a5138d2d35386a051df9318af69c2bff268d1f52af808467d6e57ed7dd9bd` (sha8 `6b3a5138`) - the PRE-fix bytes at HEAD 63ff21e9
- **Date:** 2026-09-10 · **Mode:** bug, stale-file DELTA against the last full-scope review (`dbb85879`, 2026-07-27) plus the 2026-08-13 ultra gate (`f3282eca`)
- **Delta reviewed:** 45 commits since 2026-07-24 (`92a88525..63ff21e9`), +2843/-539 lines, the whole 4393-line diff read end to end: PSK-2 cancellable apply mixin, per-loop sampling + uv-collapse guard, selected-only finish slot, flat library + Reship #30 pin, generate-library operator, preset auto-load, AMD ML-worker installer, key vault, AI-run guard + error store, support inbox, named (semantic) scan, HY4 streak tolerance, reveal law + canonical selector, part naming, companion gating, unbundling removals.
- **Context pack:** jCodemunch `find_importers` (16 importers: the package's own modules, 9 harness probes, `test_blender_smoke.py`), `search_symbols`/`get_symbol_source` on `_ai_polypart_read`, `_dispatch_projection` (projections.py:524-556), `_sel_restore`, `PATTERNSKIN_OT_apply._ps_item_done`, `PATTERNSKIN_OT_sel_text.invoke`, `generate_default_library.cancel`; `search_text` for the `wait_sdf` branch, `_GEN_LIB["active"]` readers, the zip installer loop, `_name_part_from_selection` callers, harness Blender launch conventions. `docs/remediation_manifest.json` rows for this file (2026-07-20 .. 2026-08-31, incl. HY4-MV-STREAK, HY4-G19-SELTEXT, PSK-AISEL-EXCLUSIVE) and `docs/deferred_manifest.json` rows (PSK-1/3/4/5/7/8/9/10/11/15, PSK-CURSOR-IBEAM, PSK-STRIP-HANDOFF, LIB-*, HY4-*). `.colibri_reviews/_hunt_plan.json` (rank 1, rounds 1-2) and `_refuted_ledger.json` loaded. Prior reviews read: `dbb85879` (07-27 scoped), `c64c9ba6_r2` (07-24 re-bill contract), `f3282eca` ultra gate (08-13).

## Fixed since last review
- `dbb85879` MEDIUM timer leak / double `modal_handler_add` -> **fixed, verified present**: `_ps_start` calls `_ps_stop_timer` before every new timer and registers the modal handler once (`_ps_modal_registered`).
- `dbb85879` MEDIUM concurrent apply on one object -> **fixed, verified present**: `_PS_APPLY_BUSY` name-keyed set, released on every exit path (background `finally`, modal success/failure, Esc, `cancel()`).
- `dbb85879` LOW three stale seam-score sites -> **fixed, verified present**: `_update_seam_score` at `generate_ai`, `generate_grip`, `_load_preset` (outside the enum try/except).
- Ultra gate `bug_001`/`bug_004` -> present (`lay.box()` banner, `SEL_STD` default). `bug_005` PSK-ULTRA-5 -> **closed** by `_ai_cache_hydrate` (every restore-path consumer hydrates first). `bug_006` PSK-ULTRA-6 -> **closed** by `_ap_start_current` re-reading the polypart attribute per entry.
- No prior finding is still open on this file.

## Verdict
Shippable after the three fixes below (all applied in this same session, RED-first). The single biggest risk found is an as-a-user one: every text-select ended with the faces it had just selected INVISIBLE, because part naming dropped the mesh back to Object Mode after the reveal - the 2026-08-29 reveal law could not catch it because the flip happens after the reveal, and the headless batteries asserted the reveal, never what ran next.

## Bugs & vulnerabilities

**[HIGH] Text-select ends in Object Mode after part naming - the revealed selection is invisible** - `7409-7417` (cache hit), `7497-7499` (finalize), helper `8174-8179`
- What: both `PATTERNSKIN_OT_sel_text` result sites call `_sel_write` (-> `_ps_apply_face_selection` -> `_ps_reveal_selection`: Edit/face mode, framed) and THEN `_name_part_from_selection`, which reads the part attribute via `_ai_polypart_read` - a helper that does `mode_set(OBJECT)` when not in Object Mode and never returns. `_part_name_set` -> `_part_count_of` reads it again. The operator returns `FINISHED` with the mesh in Object Mode.
- Trigger: any text-select on a scanned model (the attribute exists, so naming runs) - the cached-FREE path and the paid path alike. Present since the naming landed (2026-07-25); the reveal law (2026-08-29) did not cover it.
- Impact: the user pays ~1 cent, reads "Selected N faces for 'tree'", and sees no selection (Object Mode shows none) - the exact "nothing happened" report class G-TEXTSEL-2 tried to fix from the other side (overlay).
- Fix (applied): `_name_part_from_selection` restores Edit Mode on exit when that is where it found the mesh (`try/finally`); both sel_text sites now name BEFORE `_sel_write`, so the normal path reads the attribute in Object Mode and never pays a mode round trip. Battery `tests/harness/probes/sweep_ps_init_r3_bpy.py` A1 (behavioural: reveal, name, still `EDIT_MESH`, selection intact, name stored) watched RED (`mode=OBJECT`) then GREEN; A2 asserts the call order at both sites. Wired into the specs tier (`specs:probes-bpy-sweep-r3`).
- Verification: CONFIRMED by trace and by the headless reproducer. The LOOK (selection visible in a real viewport) is rig-lane only and was not captured this session.

**[MEDIUM] Library-generation guard sticks after a forced cancel** - `PATTERNSKIN_OT_generate_default_library.cancel` `5400-5405`, `_finish` `5389`, `invoke` `5304`
- What: `_GEN_LIB["active"]` is cleared only in `_finish()`, reached from `modal()` once the worker reports `finished`. `cancel()` (Blender tears the modal down on File > New/Open or window close) sets the cancel flag and removes the timer but never clears `active`, and `_finish()` can never run afterwards. The comment says it mirrors the ML-worker guard fix, but the ML worker clears its guard on the worker thread; this one had no such path.
- Trigger: File > New/Open (or closing the window) while a paid library generation is running.
- Impact: every later click refuses with "A library generation is already running" until Blender restarts; the daemon thread meanwhile finishes into the old library folder unobserved.
- Fix (applied): `_gen_lib_release_when_done()` - a `bpy.app.timers` callback scheduled from `cancel()` that returns 0.5 while the worker is still running and clears `active` once it has stopped (never earlier: two runs must not write the same files); falls back to clearing immediately if no timer can be registered. Battery section B (helper semantics + cancel wiring), RED -> GREEN.
- Verification: CONFIRMED by structure (the only writer of `active=False` is unreachable after `cancel()`).

**[LOW] Named scan setup raises raw** - `PATTERNSKIN_OT_ai_parts_semantic.invoke` `7586`
- What: `_ap.prepare_job(...)` runs unguarded inside the cursor try/finally; the multiview twin (`7250-7253`) wraps the same call and reports "setup failed".
- Trigger: any failure preparing the render job (proxy build, render setup).
- Impact: a raw traceback popup instead of a clean report; the cursor is restored, the AI slot is not yet claimed, so no stuck state - cosmetic/consistency.
- Fix (applied): wrapped -> `report({"ERROR"}, "Named scan setup failed: ...")` + `CANCELLED`. Battery section C (un-shadowed `invoke` with a raising `prepare_job`), RED (RuntimeError escaped) -> GREEN.
- Verification: CONFIRMED (reproduced headless).

## Missing safeguards
- Background-mode apply (`bpy.app.background` or no window): `_ps_start` runs `_ps_item_done` INSIDE `PATTERNSKIN_OT_apply.invoke`'s rollback `try`, so an exception in the post-apply steps (`print_check`, `_save_session_settings`, `_apply_finish` are unguarded) would route to `_a_fail`, which deletes a fully applied "keep original" duplicate or reports "the mesh was subdivided" after a completed apply. Interactive mode is unaffected (post-steps run from `modal()`). PLAUSIBLE only - no concrete raising input found; scripted/headless path. Not fixed this pass.
- The three modal scans (`ai_parts`, `sel_text`, `ai_parts_semantic`) leak the current view's temp PNG when Esc lands while a call is in flight (`_end` removes the timer, not `self._png`); pre-existing, one file per cancel.
- The flat library installer treats a basename collision across zip folders as "already installed" (`5199`), so two different files with one name would silently keep the first and under-report `count`. The shipped zip is our own flat build; unverified for user-supplied zips.
- `bl_info` is 1.12.0 while CLAUDE.md's durable block still says v1.10.0 (doc drift, not code).

## Adversarial verification pass (refuted -> `_refuted_ledger.json`)
- "The deep-mode thickness (SDF) pass still hard-cancels the paid scan on a single transient failure" - REFUTED: the `wait_sdf` branch (`7267-7275`) is best-effort (`if not self._err and self._res: assign_view_sdf`), then advances and checkpoints; no cancel path.
- "The flat installer opens zip directory entries as files" - REFUTED: `if m.endswith("/"): continue` (`5183`) precedes the flatten.
- "Per-loop sampling can receive per-vertex u/v from the UV fallback and crash `np.bincount(lv, weights=h)`" - REFUTED: `_dispatch_projection` runs every mode over the P it is given (`Pl`); the UV fallback re-dispatches TRIPLANAR on the same per-loop arrays.
- "`_ai_polypart_read` may return a list, so `pp == part` / `pp[...]` in `_ap_start_current` and `_name_part_from_selection` fail silently" - REFUTED: it returns an `np.int32` ndarray or `None` (`8181-8184`); both callers null-check.
- Considered and dropped without a ledger row (not defects): `_has_seq` with an empty `prefer` token list (guarded by `if pwant`), `_PS_LOADING` re-entrancy around `s.library_item` writes (single-threaded, guarded), `_ai_poly_part` tie-breaking (stable lexsort == old argmax-first), a double `generate_default_library` dialog (Blender keeps one props dialog).

## Gate record
- Round 1 BLOCK (glm-5.3-flash, `gate_20260910-073917`), REAL: the guard-release timer was registered non-persistent, and Blender removes non-persistent timers when a file is loaded (verified against this build's `bpy.app.timers.register` docstring: "persistent: Don't remove timer when a new file is loaded") - File > New/Open is the headline trigger of the very defect, so the first cut died with the modal it was meant to outlive while the manifest row called it fixed. Fixed with `persistent=True`; the battery now asserts the flag in `cancel()`. Docket row EV-065.

## Remediation postscript (same session)
The three fixes were applied after this review hashed the bytes above; the file is now `f1a44404c967b5d211171dbda82f8d0427dce3e4a3cfbfd6b6cb875844021e2a` (45 insertions / 7 deletions, junction twin `blender_dev/addons/PatternSkin/__init__.py` byte-identical). Rows PS-TEXTSEL-REVEAL-NAMING, PS-GENLIB-GUARD-STUCK, PS-SEMSCAN-SETUP-RAW in `docs/remediation_manifest.json`, same commit. Regression: `reveal_and_pick_bpy`, `ai_select_exclusive_bpy`, `spec_ps_ai_selection_bpy` all rc 0 after the change.
