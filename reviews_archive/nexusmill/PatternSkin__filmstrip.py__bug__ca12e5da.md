# Colibri Review - bug (DELTA) - PatternSkin/filmstrip.py

- **Source path:** `PatternSkin/filmstrip.py`
- **Reviewer:** claude-fable-5-1 (in-session), Colibri G37 protocol, campaign item 1 (product cores), rank 4
- **sha256 reviewed:** `ca12e5da4bb0e578058499f1109d0bafd75ed22ba7c20a511be31776e340f850` (sha8 `ca12e5da`)
- **Date:** 2026-09-10 · **Mode:** bug, stale-file DELTA against `e01325dc` (2026-08-22 grok round-5 gate)
- **Delta reviewed:** 3 commits / 253 diff lines: 06580c2b (GROK-FILM5 loud persist failure), 462417ae (slot editor retired -> `film_pick` straight to the library browser), 032e10b6 (HY4-FILMCELL-DESELECT all-domain clear, HY4-DRESS-SHARE 0.6 floor, `token_present()` in draw) - every hunk read.
- **Context pack:** the prior review record(s) for the file, `docs/remediation_manifest.json` rows from 2026-07-24 on, `docs/deferred_manifest.json` rows naming the file, `_hunt_plan.json` + `_refuted_ledger.json` loaded; jCodemunch `get_symbol_source` on the call sites each finding depended on.

## Fixed since last review
- Every remediation row dated after the base review was verified present at the bytes (they are the delta).

## Verdict
Clean at the delta. `film_pick.invoke` opens the browser in the library folder and `execute` assigns through `_film_assign`/`s.pattern` only for an existing path; the cell toggle-off clears all three selection domains; the dress floor skips and reports a weak argmax instead of texturing it; the draw path reads the cached `token_present()`.

## Bugs & vulnerabilities
None confirmed at the delta.

## Adversarial verification pass / notes
- Missing safeguard (not a defect): `film_pick.execute` no longer checks the extension the retired `film_use_file` checked - the browser's `filter_glob` filters interactively, a scripted non-image path fails later at bake with the part's clean warning.

---

# FULL re-audit 2026-09-10 (appended - the record above predates the adversarial gate and is kept as history, not as baseline)

# Colibri Review - bug (FULL re-audit) - PatternSkin/filmstrip.py

- **Source path:** `PatternSkin/filmstrip.py` (junction twin `blender_dev/addons/PatternSkin/filmstrip.py`, same bytes)
- **Reviewer:** claude-fable-5-1 (fork of the lead session), Colibri G37 protocol, campaign item 1 (product cores), rank 4
- **sha256 reviewed:** `ca12e5da4bb0e578058499f1109d0bafd75ed22ba7c20a511be31776e340f850` (sha8 `ca12e5da`) - the PRE-fix bytes
- **Date:** 2026-09-10 · **Mode:** bug, FULL review of the current bytes (owner ruling 2026-09-10: this file's 07-20..08-31 audits predate the adversarial gate and cannot be trusted - no delta against them)
- **Context pack:** all 730 lines read; jCodemunch `find_importers` (only `__init__.py`, names `_film_draw`/`_film_thumbs_ensure`/`_film_thumb_dir`/`_film_fit`/`_film_assign`) + `search_text` for every call site; `get_symbol_source`-equivalent reads of `_ai_select_polypart`, `_ps_apply_face_selection`, `_ai_polypart_read`, `_ai_palette`, `_sel_ctx`, `_part_names_read`, `_pat_icon`, `_model_status`, `keystore.token_present`, `ai_parts.mesh_signature`, `prepare_job`, `render_view_png`, `load_text_select`, `text_finalize`, `render_part_thumbs`, and the panel caller `PATTERNSKIN_PT_pattern.draw` (line 5461); the 6 remediation rows and 6 deferred rows naming the file loaded as CLAIMS and each fix re-verified present at the bytes (GROK-FILM5 log-loud persist :318, HY4-FILMCELL-DESELECT :50-52, HY4-DRESS-SHARE :321-329, FS-1 :54, the 07-20 None-object / colour-format / obj.name sanitising :467/:491/:500).

## Verdict
Not shippable at these bytes: the Pattern-step panel's draw() dereferences the active object's vertex buffer with no type or emptiness guard, so after a scan (parts count is persistent scene state) selecting the camera or a light takes the whole Pattern panel down, and on a mesh the same call copies every vertex coordinate per redraw (G29). The dressing modal, the cell toggle, export, fit-fix and pick hold end to end.

## Bugs & vulnerabilities

**[HIGH] The Pattern panel errors out whenever a non-mesh (or empty-mesh) object is active after a scan** - `_film_draw` `line 677` -> `_film_thumb_dir` `line 607-610` -> `ai_parts.mesh_signature` (`obj.data.vertices`)
- What: `PATTERNSKIN_PT_pattern.draw` calls `_film_draw` whenever `scene.pattern_skin.ai_parts_count > 0` (`__init__.py:5460`). `_film_draw` takes `ob = context.active_object` and calls `_film_thumb_dir(ob, n)` guarded only by `if ob`. `_film_thumb_dir` calls `mesh_signature(obj)` which reads `obj.data.vertices` and raises `RuntimeError` on an empty mesh. Nothing in the chain checks `obj.type`.
- Trigger: scan any model into parts (sets the count), then click the camera, a light, an empty, a curve, or a new empty mesh in the outliner / viewport. Reproduced headless: `AttributeError: 'Camera' object has no attribute 'vertices'` and `RuntimeError('mesh has no geometry ...')` from the exact draw-time call.
- Impact: Blender aborts the panel draw - the whole "2 - Pattern" panel (library folder, pattern picker, everything below the strip) renders as a red error box with a console traceback, on every redraw, until a non-empty mesh is active again. The parts count survives save/reload, so this is the file's steady state whenever the camera is selected.
- Fix: guard in `_film_thumb_dir` (`obj is None or obj.type != "MESH"` or zero verts/polys -> `None`); `_film_draw` already handles `tdir is None`; `_film_thumbs_ensure` gets an `if d is None: return None` for the empty-mesh case (its `render_part_thumbs` raises on empty anyway). Probe `probe_ps_filmstrip_1.py` checks `FILM_draw_chain_survives_non_mesh_active` / `..._empty_mesh_active`: RED at these bytes, GREEN with the fix monkeypatched onto the live package.
- Verification: CONFIRMED (call chain traced from the panel to the raise; headless reproduction).

**[MEDIUM] Heavy work in draw(): the strip copies the entire vertex buffer on every redraw (G29)** - `_film_thumb_dir` `line 610` -> `mesh_signature` `ai_parts.py:973`
- What: the thumb-dir key is `mesh_signature(obj)`, which does `me.vertices.foreach_get("co", V)` over ALL vertices plus a stride-sampled sha1, and `_film_draw` calls it unconditionally per redraw (the module docstring at :634 claims "Read-only in draw()").
- Trigger: any redraw of the Pattern panel (mouse move over the N-panel) with a scanned mesh active.
- Impact: measured 47.9-50.9 ms per redraw at 491k vertices (a 700x700 grid; scanned print STLs are routinely larger) - the panel and viewport stutter on every mouse move, and the copy allocates 12 MB per redraw.
- Fix: memoise the dir in `_film_thumb_dir` keyed by `(obj.name, n_verts, n_polys, n)` with a 1 s TTL (draw hits the memo; operators after a scan compute the same signature anyway - the scan does not move vertices; a within-1-s edit that keeps counts is at worst a 1 s stale dir in draw). Probe check `FILM_draw_thumb_dir_lookup_cheap` asserts the repeat lookup < 5 ms: RED (48 ms) -> GREEN (0.00 ms).
- Verification: CONFIRMED (measured).

## Missing safeguards (not fixed)
- Dress-from-one-line has no partial checkpoint: Esc during a clause's SAM-3 views discards the views already billed for that clause (up to 7 of 8 calls, ~1 cent each); the AI-Parts scan mirrors its partial results (PS-MIRROR-STALE-CHECKPOINT), the dressing modal does not.
- The known Esc-mid-call temp-PNG leak (round 38 note on the modal scans) applies here too: `os.remove(self._png)` at :251 fails with PermissionError while the worker thread still has the file open for base64 - swallowed, file leaks in the temp dir.
- `_dress_majority_part` indexes the part attribute with a stale triangulation only through the modal's outer try -> the user sees "Dressing error: index ..." rather than "re-scan the model" (the export operator has the explicit check at :482).
- `_dress_find_library` walks the whole library tree per clause inside `invoke()` (UI thread); fine for a few hundred files, not for a multi-thousand-file library.

## Adversarial verification pass (refuted claims - deleted from findings)
- "Esc during `wait` leaks the per-view PNG" - real but ALREADY RECORDED (round 38, pre-existing across the modal scans); not re-flagged as new.
- "`film_cell` toggle-off fires when another operator set `ai_parts_active` without selecting" - refuted: `depress` needs `ps_film_sel` too, and only `_ai_select_polypart` (`__init__.py:8371`) sets it.
- "`_dress_parse` splits 'sandblasted' on `and`" - refuted: `\band\b` needs word boundaries.
- "`export_parts` palette shorter than the part count" - refuted: `_ai_palette(int(tri_part.max()) + 1)` covers every id; `_ai_palette` clamps n >= 1.
- "`token_present()` / `_model_status()` do vault reads / network in draw()" - refuted: 5 s presence cache (`keystore.py:193-203`); `_model_status` is the cached wrapper that never networks.
- "`_part_names_read(ob)` crashes for a non-mesh active object" - refuted: `obj.get(...)` works on any ID and the function is wrapped in try/except.
- "Cancel loses the paid match" - refuted as a defect: the in-flight generation is deliberately left to finish (comment :254); the missing partial checkpoint is listed above as a safeguard, not a bug.

## Remediation postscript (same session)
The fixes were applied after this review hashed the bytes above; the file is now `0ec896205742a9e5f872a903bee644d3b34f9117641799aaf94122b4799f98df`. Rows PS-FILM-DRAW-GUARD, PS-FILM-DRAW-MEMO in `docs/remediation_manifest.json`, same commit.

