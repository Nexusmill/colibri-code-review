# BUG review: PatternSkin\__init__.py

- source: `C:\Users\User\source\repos\Nexusmill\PatternSkin\__init__.py`
- model: xiaomi/mimo-v2.6-pro
- reviewed: 2026-09-24 09:52
- tokens: in 181921 / out 56677
- est cost: $0.1284

---

## Verdict
No new CRITICAL/security issues; the round-3 remediation all verified as landed. The single biggest risk is that **`_write_3mf` interpolates the raw numpy array `tris` instead of the `<triangle>` XML string `trs` it just built**, so every 3MF export silently writes a NumPy `repr` where the triangle list belongs — a corrupt print file with a success message.

## Bugs & vulnerabilities

**[HIGH] `_write_3mf` formats `tris` (numpy array) instead of `trs` (the built XML) — every 3MF export is silently invalid** - `line 3555`
- What: line 3551 builds the real triangle markup into `trs` (`'<triangle v1="%d" v2="%d" v3="%d"/>' …`), but the object template at 3555–3556 interpolates `tris`, the raw `(nt,3)` `np.int64` array from 3548–3550. `'%s' % ndarray` calls `str()` on it, yielding `[[0 1 2]\n [3 4 5]\n …]` — and for `nt > 1000` NumPy truncates to `…`, so even the garbage is incomplete. `trs` is therefore dead code (it is referenced nowhere else in the file).
- Trigger: `patternskin.export_3mf` on any mesh — no special input needed.
- Impact: `<triangles>[[0 1 2] …]</triangles>` contains zero `<triangle>` elements. Bambu/Orca/Prusa either reject the file or import a 0-triangle object, while the operator reports `"Exported 3MF (1 object(s)) + print notes: …"` (3628). A whole print job silently disappears; the STL path is unaffected, so the bug hides behind "STL works fine".
- Fix: `'<triangles>%s</triangles></mesh></object>' % (oid, vtx, trs)`. Add a round-trip test that opens the written zip and asserts `model_xml.count("<triangle ") == nt`.

**[HIGH] Grip/scale height field is sampled at (or below) its own Nyquist rate — the knurl degenerates to a constant or a 1-cell alternation at default settings** - `line 4128`
- What: `_extrude_scale_mask` evaluates `_grip_height(kind, U, V, nu, nv)` on the corner grid with `nu = round(L/pitch)` (4127–4129), while `_build_scale` builds that grid with `res = max(0.3, pitch * 0.5)` and `nx = round(L/res)` (4278–4279), and `_build_scale_from_outline` does the same (4325–4326). So `nx ≈ 2·nu` — exactly Nyquist — and for `pitch < 0.6` the `res` floor makes `nx == nu` exactly.
  - `pitch = 0.3` (the `grip_pitch_mm` minimum): `nx = round(L/0.3) = nu`, `U_i·nu = i`, `cos(2πi) ≡ 1` → `KNURL_STRAIGHT`/`RIB`/`HEX`/`DIMPLE` return a **constant 1.0**, i.e. `ZT = T + depth` — a uniformly raised slab with no pattern at all.
  - `pitch = 0.8` (`PEN` preset) on `FB_STD` (L=127): `nx = 318`, `nu = 159`, `nu/nx = 0.5` exactly → `cos(πi) = (-1)^i` → a 1-cell square wave, not a knurl.
  - `KNURL_DIAMOND` (the default `grip_kind`) at `nx = 2·nu` collapses to a 1-cell checkerboard (`max` of two Nyquist cosines = `0.5 + 0.5·(-1)^(i+j)`); `PYRAMID`'s `tx = |(U·nu) % 1 − 0.5|·2` hits exactly `{0, 1}`.
  - Default `grip_pitch_mm = 1.5` on `FB_STD`: `nx = 169`, `nu = 85` → `nu/nx = 0.503`, a `(-1)^i` zigzag with a slow beat.
- Trigger: "Create blank pair" or "Scales from outline" with essentially any pitch the UI offers.
- Impact: the knife-scale generators silently emit flat (or per-cell noisy) blanks — the grip feature's entire output is wrong and looks like a modeling error rather than a bug. `PRINT`/`_print_reco` then evaluates a depth that isn't in the geometry.
- Fix: resolve each carrier with ≥4 cells per period — `res = max(0.3, pitch / 4.0)`, or clamp `nu = max(2, int(round(L / pitch)))` to `nx // 4` (and likewise `nv` to `ny // 4`) and warn when the requested pitch cannot be resolved. Add a harness assertion that `_extrude_scale_mask`'s `ZT.ptp() > 0.5 * depth` for every `PS_GRIP_PRESETS` entry.

**[MEDIUM] `_build_grip_sleeve` hard-caps `na`/`nz` while `nu`/`nv` are unbounded — fine pitch on a large sleeve renders garbage** - `line 4077`
- What: `nu`/`nv` are derived from the real circumference/length (4075–4076) but the tessellation is `na = int(min(256, max(96, nu * 7)))` and `nz = int(min(320, max(48, nv * 5)))` (4077–4078). Past `nu > 36` / `nv > 64` the caps bind and the samples-per-feature ratio falls below 1.
- Trigger: e.g. `grip_fit_mm = 120, grip_wall_mm = 8, grip_clearance_mm = 2, grip_pitch_mm = 0.3, grip_len_mm = 300` (all in-range UI values) → `nu = 1466` ridges on `na = 256` segments (0.17 samples/ridge) and `nv = 1000` on `nz = 320` (0.32 samples/ridge). Even the mild `fit=20, pitch=0.6` case lands at `nu/na = 1.97` — Nyquist.
- Impact: the sleeve's `ro = outer_r + depth * H` (4084) becomes Moiré spikes/dents; the mesh self-intersects (`ro` can dip below `inner_r`, inverting the wall) and prints as noise. Same "silent wrong geometry" class as the previous finding.
- Fix: derive `na`/`nz` from `nu`/`nv` without a ceiling below `8*nu` / `8*nv` (budget-check and refuse with a message instead of capping), or clamp `nu = na // 8`, `nv = nz // 8` and report the achieved pitch.

**[MEDIUM] `ai_parts_semantic` and `ai_parts_native` run their heavy finalize inline in `modal()` — the G-HANG-1 fix applied to `ai_parts` was not carried over** - `line 8141`
- What: `ai_parts` deliberately moved `finalize_job` onto a worker thread (7650–7667, "label lifting + geometric refine + the proxy->full-mesh cKDTree label transfer … belongs on a worker thread, NOT inline in modal()"). The equivalents are still synchronous in one non-yielding tick: `semantic_finalize(...)` at 8141 followed by `_ai_poly_part`/`_ai_store_attr`/`_ai_write_colors`/`_ai_select_polypart`/`save_parts` (8148–8161), and `p3sam_download` + `p3sam_labels_from_glb` + `regranulate` + the same tail at 8303–8317.
- Trigger: run "Scan into named parts" or "Scan into parts (native 3D)" on the 1.8M-face scan mesh this file names as its design target (or a ~2M-triangle GLB coming back from P3-SAM).
- Impact: multi-second to multi-minute freeze with zero feedback in exactly the place the remediation manifest classed as "users assumed a crash"; no Esc is deliverable during it. Only these two of the four AI scan operators are affected.
- Fix: mirror the `ai_parts` pattern — run `semantic_finalize` / `p3sam_download`+`p3sam_labels_from_glb`+`regranulate` on `threading.Thread` with a `finalize_wait` phase, and assert a wall-clock budget for the finalize tick in the 1.8M-face harness.

**[MEDIUM] `install_accel` silently drops a non-allowlisted `--index-url` and installs from PyPI instead** - `line 3025`
- What: `if _h in (…) or _h.endswith(".pythonhosted.org"): args += ["--index-url", self.index_url]` — when the host does not match, execution simply falls through and `args` keeps pip's default index. There is no report, no `accel_status` entry, and no `self.report`.
- Trigger: `patternskin.install_accel(index_url="https://pypi.ngc.nvidia.com/…")` from a script, or any future/recommended tier whose pinned index host is outside the four-name allowlist (the GPU button forwards `rec.get("index_url", "")` verbatim at 6335–6336).
- Impact: a silent supply-chain/behaviour substitution — the pinned ROCm/CUDA/DirectML wheel is replaced by whatever PyPI serves for that name (often a CPU-only build, or a `No matching distribution` failure reported as a plain install error). The surrounding code treats "wheels-only + index allowlist" as hardening (S2, 3016–3019); silently ignoring the second half defeats it without telling anyone.
- Fix: `else: self.report({"ERROR"}, "index host %r not allowlisted - refusing" % _h); return {"CANCELLED"}` instead of falling through.

**[LOW] `_library_items`' empty-library placeholder uses an empty enum identifier, which Blender treats as a SEPARATOR** - `line 918`
- What: `items = [("", "(no textures — set folder or generate a library)", "", 0, 0)]`. Per this file's own documented rule at 1223–1225 ("an EMPTY enum identifier means SEPARATOR, not a selectable item" — the reason `_PS_NO_PRESET = "__none__"` exists), a 5-tuple with `""` identifier is a separator: its label is never rendered and it is not selectable.
- Trigger: point `library_dir` at an empty folder, or a folder where every `_PREVIEWS.load` fails (912–915 `continue`), then read `s.library_item` (done by `_eff_pat` at 968 on every Apply/Preview/draw).
- Impact: the enum ends up with no selectable item — `s.library_item` reads back `""` so `_eff_pat` silently falls through to `s.pattern`, and the advertised hint text ("set folder or generate a library") never appears; `s.library_item = found` at 5013 fails and is only survivable because it happens to sit in a `try/except`.
- Fix: use a real identifier, e.g. `("__none__", "(no textures — set folder or generate a library)", "", 0, 0)`, mirroring `_PS_NO_PRESET`.

**[LOW] `_load_preset` writes hand-edited preset-JSON keys into the settings with `setattr` and no `_PRESET_KEYS` filter** - `line 5030`
- What: `for k, v in cfg.items(): setattr(s, k, v)` applies every surviving key verbatim. `save_user_preset` (5077) and `recipe_from_object` (2619) both filter through `_PRESET_KEYS`, and `_preset_is_modified` (1275–1277) skips non-`_PRESET_KEYS` keys — but the load path does not. The schema validator at 1322–1347 checks only the envelope (`name`/`settings` types), not `settings`' keys.
- Trigger: add `"settings": {"ui_section": "SYSTEM", "loaded_preset": "U:x", "ai_parts_active": 999, "last_error": "…", "ps_seam_score": 0.0}` to `patternskin_user_presets.json` and pick the preset.
- Impact: hidden/runtime-only and diagnostic properties (`ui_section`, `loaded_preset`, `ai_parts_active`, `ai_parts_count`, `last_error`, `ps_seam_score*`) are set from an unvalidated file, so a corrupted/hand-edited preset can wedge the UI state (e.g. `ai_parts_active = 999` with `ai_parts_count = 0`) and `_preset_is_modified` will not report the drift it caused. No privilege boundary is crossed (the file is the user's own), so this is validation, not a vulnerability.
- Fix: `for k, v in cfg.items(): if k not in _PRESET_KEYS: continue` before `setattr`.

## Missing safeguards
- No samples-per-feature assertion anywhere in the grip generator path (`_grip_field`/`_grip_height`/`_extrude_scale_mask`/`_build_grip_sleeve`). Both HIGH/MEDIUM geometry findings would be caught by a single invariant: `nx >= 4*nu` and `ny >= 4*nv` (and `na >= 4*nu`, `nz >= 4*nv`), with a harness sweep over `PS_GRIP_PRESETS`.
- `_write_3mf` has no validation of its own output. A 10-line test that unzips the result and asserts `<vertex ` / `<triangle ` counts match `nv` / `nt` would have caught the `tris`/`trs` mix-up at build time.
- `ai_parts_semantic` / `ai_parts_native` have no wall-clock budget assertion for a single `modal()` tick at 1.8M faces (the one `ai_parts` got as part of G-HANG-1).
- `_ps_start` claims `_PS_APPLY_BUSY` at 568–569 but the release-on-failure wrapper only starts at 619; 570–618 (`context.window_manager`, `wm.windows`, the background branch dispatch) is unprotected, so an exception there strands the object busy for the session with no registered modal to `cancel()`. Move the claim inside the 619 `try` (or wrap 568–618 in the same `except → _ps_release_busy(); raise`).

## Fixed since last review
All seven round-3 findings verified remediated in the current bytes:
- **R3-1** `_SELF_UPDATE_BUSY` one-at-a-time claim present (declared 1519, checked 6481–6488 without touching `cancel`, released only from `_self_update_worker`'s tail `finally` at 1750–1753); `_CU_BUSY` added for `check_updates` (3403, claimed after a live child at 3445, released at 3477 and in `cancel` 3517).
- **R3-2** `_ai_write_colors` vectorised: `cols = np.ones(...)`, `rgb[vis] = pal[np.clip(pp[vis],0,None)]`, canonical loop-layout guard at 8688, `cols[:, :3] = np.repeat(rgb, lt, axis=0)` at 8692, per-polygon slice loop retained only as the corrupt-mesh fallback (8693–8697).
- **R3-3** Missed views are now checkpointed-as-missed: the failure branch does `self._i += 1` **then** `save_scan_partial` (7606–7613), so resume == live semantics and the already-paid view is never re-billed.
- **R3-4** `_PS_APPLY_BUSY` re-keyed to `obj.as_pointer()` (562, 568, 640) and `api_apply` routed through the same guard with `add`/`try`/`finally: discard` (2300–2309).
- **R3-5** `_build_scale_from_outline` image removal moved into a single `finally` site (4310–4318), covering the failed-pixel-read path.
- **R3-6** Start-only `try/except` around `Thread.start()` for both `install_ml_worker` (3290–3298, clears `_ML_WORKER_INSTALLING` and re-raises) and `generate_default_library` (5643–5652, clears `_GEN_LIB["active"]` and re-raises).
- **R3-7** Thin-band path returns the `"SKIP"` sentinel before `materials.clear()` (2225–2227) and the caller intercepts it *before* the viewport switch / `finish_txt` use with an explicit WARNING (2565–2567).

The earlier batches (R2-1…R2-8 and F1–F20) remain in place unchanged.

---

## In-session verification + remediation (2026-09-24, round 4)

Lead verification: the round's #1 HIGH (_write_3mf interpolating the numpy array) is REFUTED
against current bytes - the template interpolates trs (the XML string built from tri); no
variable named tris exists in that scope. The adversary attacked the refutation four ways
and upheld it ("a fabricated top finding; the lead's verification is a G11 process win").
The round-trip test was added anyway as the permanent pin. The #2 HIGH confirmed with a
corrected boundary: flatness occurs iff nu/nx is an integer (pitch=0.3 on FB_STD, and
pitch=0.6 at the 500-cap on long scales); the DEFAULT pitch renders a Nyquist checkerboard.
All MEDs + LOWs confirmed; the _ps_start claim-gap safeguard promoted.

Adversary gate round 4: APPROVE WITH MODIFICATIONS, folded in: achieved-pitch trades must
reach the USER (operators report WARNING; _extrude_scale_mask returns (obj, nu, nv)); the
sleeve REFUSES unresolvable pitches with the honest minimum (a budget, not silent
coarsening - the na//8 clamp would have coarsened 46x); the native glb removal is deferred
until after the main-thread import (a download-thread finally would race it into a missing
file); an "importing..." status tick precedes the slow gltf import; the index refusal names
the refused host.

Fixes: R4-2 res=pitch/4 in both scale builders + carrier clamp + operator WARNINGs;
R4-3 sleeve 4-samples-per-feature + 1.2M-vertex budget + refuse-with-minimum; R4-4
semantic_finalize threaded (finalize_wait), native re-phased poll->fetch_wait->import->
finalize_wait (download + regranulate threaded; gltf import on main; _cleanup_glb helper;
cancels also remove _glb); R4-5 allowlist else-refusal; R4-6 "__none__" placeholder;
R4-7 _PRESET_KEYS filter; R4-8 busy claim moved after the wm/win computation.

Tests: tests/test_hunt_r4_fixes.py 16/16 PASS - 3MF round-trip (12/12 triangles, mm unit),
knurl depth preserved at default/pen/UI-min pitches WITH honest achieved-pitch numbers,
sleeve refusal + healthy build, placeholder identifier, hostile-preset key filter,
BEHAVIORAL claim-order probe (a raising window_manager leaves _PS_APPLY_BUSY empty),
thread-target ast pin. r1 21/21 + r2 13/13 + r3 11/11 + smoke re-passed. install_accel
index refusal pinned by source assertion (headless-unreachable behind the background
fail-fast). NOT COMMITTED (owner order).
