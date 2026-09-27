# BUG review: PatternSkin\__init__.py

- source: `C:\Users\User\source\repos\Nexusmill\PatternSkin\__init__.py`
- model: xiaomi/mimo-v2.6-pro
- reviewed: 2026-09-24 11:40
- tokens: in 188256 / out 42188
- est cost: $0.1186

---

## Verdict
The previous round's eight findings are all genuinely fixed. One **new HIGH** concurrency defect shipped alongside those fixes: `PATTERNSKIN_OT_self_update.execute` resets the shared `_SELF_UPDATE` state **after** starting the worker thread, which defeats the Esc-cancel of the download and — on a fast failure — permanently wedges the modal while silently re-opening the "one worker at a time" gate that protects the add-on's own file replacement. Everything else new is low-severity robustness around unvalidated on-disk JSON and one allocation bound.

## Bugs & vulnerabilities

**[HIGH] `self_update` resets `_SELF_UPDATE` *after* starting the worker — defeats Esc-cancel and wedges the modal** - `line 6584`
- What: `threading.Thread(...).start()` runs at 6578; `_SELF_UPDATE.update(phase="start", msg="starting...", done=False, ok=False, cancel=False)` runs at **6584, after the thread is live**. `_self_update_worker`'s first statement is `_SELF_UPDATE.update(phase="download", msg="downloading...")` (1677), and its `finally` sets `_SELF_UPDATE["done"] = True` / `_SELF_UPDATE_BUSY = False` (1780–1782). Two ordering outcomes, both wrong:
  1. **Worker wins the write race** (its first dict write lands before 6584): `phase` is clobbered back to `"start"` for the whole download. `modal()` only honours Esc while `phase == "download"` (6600) and `cancel()` likewise (6624), so **Esc silently does not cancel the download** — the exact documented behaviour ("Esc cancels during download") and the same guard `cancel()` relies on when Blender tears the modal down.
  2. **Worker fails fast and finishes before 6584** (e.g. `_verified_fetch`'s host check raises at 1558–1559): the worker already set `done=True, ok=False` and released `_SELF_UPDATE_BUSY`. Line 6584 then resets `done=False, ok=False`. `modal()` at 6607–6608 does `if not _SELF_UPDATE.get("done"): return {"RUNNING_MODAL"}` **forever** — the modal handler and its 0.2 s timer never terminate, `s.accel_status` sticks at `"Update: starting..."`, and because `_SELF_UPDATE_BUSY` is already `False` a second click starts a *second* worker + *second* modal writing the same `_SELF_UPDATE` dict and replacing the add-on's own files concurrently — the invariant `_SELF_UPDATE_BUSY` exists to enforce (1548: *"one worker at a time: two installs interleave the add-on's own file replacement"*).
  3. In case 2 with a *successful* fast worker, `ok=False` at 6584 also turns a completed update into `modal()`'s `"Update failed: ..."` branch (6617).
- Trigger: press **Update now** when `version.json` advertises a verified zip. The download takes seconds and releases the GIL, so 6584 routinely lands inside the worker's window; a failed/refused `zip_url` reproduces case 2 deterministically.
- Impact: documented cancellation of a 600 MB download is dead; a failed update leaves a permanent `RUNNING_MODAL` handler for the session; concurrent self-updates can interleave backup/replace/rollback on `__init__.py` itself.
- Fix: hoist the reset **above** the thread start:
  ```python
  _SELF_UPDATE.update(phase="start", msg="starting...", done=False, ok=False, cancel=False)
  _SELF_UPDATE_BUSY = True
  try:
      threading.Thread(target=_self_update_worker, args=(info,), daemon=True).start()
  except Exception as e:
      ...
  ```
  and change `modal()`'s Esc test to a whitelist of cancellable phases (`in ("start", "download")`) so a stale phase can never suppress it. Pin with a test that monkeypatches `_self_update_worker` to set `done=True` before returning and asserts `modal()` terminates and `phase` is never `"start"` after `execute()` returns.

**[LOW] `_load_license` accepts any JSON value — a non-object `patternskin_license.json` breaks the Settings panel, Export STL, and the Activate dialog that would fix it** - `line 1434`
- What: `_load_license` does `_LICENSE = json.load(f)` with only a parse guard (1430–1436) and **no shape check**, then caches it forever. `_license_line()` (1446–1450) calls `lic.get("name")`; `PATTERNSKIN_OT_activate.invoke` (6501–6502) calls `lic.get("name", "")`. Valid JSON that is not an object (`null`, `[]`, `"x"`, `123`) yields `AttributeError` from `.get`. The parallel writer/reader `_user_presets()` *did* get this hardening (1345–1347 `if isinstance(raw, dict)`, PSK-11) — `_load_license` was missed.
- Trigger: `~/.config/patternskin_license.json` containing `null` or `[]` (hand edit, editor artefact, or a partially-restored config).
- Impact: three separate failures. (a) `_stamp_stl_header` calls `_license_line()` at **1453, outside** its `try` (which starts at 1456), and `PATTERNSKIN_OT_export_stl.execute` calls `_stamp_stl_header(fp)` at **3727, outside** the notes `try` (3716–3726) — so Export STL writes the file and then dies with a raw `AttributeError` instead of the success report at 3728. (b) `PATTERNSKIN_PT_system.draw` (6373) raises every redraw; `_sec`'s catch-all (5371–5374) renders the whole Settings section as *"(could not draw this section)"* until the file is deleted by hand. (c) `PATTERNSKIN_OT_activate.invoke` raises too, so **the user cannot repair it from the UI**.
- Fix: mirror `_user_presets()` — `raw = json.load(f); _LICENSE = raw if isinstance(raw, dict) else {}`. Also move `line = _license_line()` inside the `try` at 1456 (or wrap `_license_line` itself) so a licence problem can never fail an export that already succeeded.

**[LOW] `PATTERNSKIN_OT_recipe_from_object` trusts the shape of a `.blend`-stored custom property — uncaught `AttributeError`** - `line 2646`
- What: only `_json.loads(raw)` is guarded (2640–2643). The next two accesses are not: `data.get("settings")` (2646) raises if `data` is a JSON list/scalar, and `(… or {}).items()` raises if `data["settings"]` is any non-empty non-object (`{"settings": [1]}` → `list.items`). `ps_recipe` is a plain custom property inside the `.blend`, i.e. fully attacker-/corruption-controlled input from a downloaded scene file — the exact class `_user_presets()` was hardened against.
- Trigger: an object carrying `ps_recipe = "[1,2,3]"` or `ps_recipe = '{"v":1,"settings":[1]}'`, then **Load settings from object**.
- Impact: the operator aborts with a raw traceback instead of the intended `"Stored recipe is unreadable."` (2643). No data loss (the `setattr` loop is `_PRESET_KEYS`-filtered at 2647), but the clean-error path is dead for malformed input.
- Fix: `if not isinstance(data, dict): raise/report`; `settings = data.get("settings"); if not isinstance(settings, dict): settings = {}` before the loop.

**[LOW] `grip_pattern`'s grid is a 2×N×N `int64` `mgrid` re-cast to `float64` — ~2 GB transient at the 8192 bound, reachable from the UI because `grip_tile_mm` has no hard `max`** - `line 1217`
- What: `yy, xx = np.mgrid[0:size, 0:size].astype(np.float64) / size` (1217) materialises `np.mgrid` as one `(2, size, size)` **int64** array (1.07 GB at `size=8192`), then a `float64` copy (another 1.07 GB), then the divide (another 1.07 GB) — ~2.1 GB peak before `_grip_field` adds several more `(size, size)` float64 temporaries (`np.maximum` of two `cos` chains in `KNURL_DIAMOND`, three in `HEX`). `size = min(8192, max(512, ceil(4n/16)*16))` (1212) hits 8192 at `n ≳ 3272`, i.e. `grip_tile_mm / grip_pitch_mm ≳ 3272`. `grip_tile_mm` is `FloatProperty(min=0.5, soft_max=80)` with **no `max=`** (1931) and `grip_pitch_mm` `min=0.3` (1914), so typing `grip_tile_mm = 1000` is accepted by Blender and reaches `size=8192` from the panel.
- Trigger: set *Grip tile (mm)* to 1000 (typed past the soft slider), *Feature size* to 0.3, click **Generate grip texture**.
- Impact: multi-GB allocation on the main thread with no progress and no Esc (`generate_grip` is a plain synchronous `execute`, 4517–4536) — can OOM the session exactly like the (now fixed) lithophane tuple spike, and `make_seamless`/`_save_gray_png` (4521–4527) then churn the same array twice more. The 8192 clamp itself is sound; the *representation* is what costs.
- Fix: add `max=` to `grip_tile_mm` (and/or a `count` ceiling that produces a warning, matching `grip_pattern`'s own clamp-and-log at 1213–1216), and build the grid by broadcasting 1-D ramps — `U = np.arange(size, dtype=np.float32) / size`, `V = U[:, None]`, `U = U[None, :]` — so `_grip_field` allocates one output plane instead of two full index planes plus a dtype copy. A float32 pipeline halves it again.

## Missing safeguards
- `_load_license` needs the same `isinstance(raw, dict)` schema gate `_user_presets()` has (1345–1347), plus a test that a `null`/`[]`/`123` licence file leaves `_license_line()` returning `""`, `PATTERNSKIN_OT_export_stl` reporting success, and `PATTERNSKIN_OT_activate` still invokable.
- `_SELF_UPDATE` needs an ordering test: after `PATTERNSKIN_OT_self_update.execute` returns, `phase` must never be `"start"` once the worker has written its first phase — or simply assert `_SELF_UPDATE["phase"] == "start"` is observable at thread entry. Same shape as the `_ps_start` claim-order pin (R4-8).
- `_check_update` (1509) uses plain `urllib.request.urlopen`, which **follows redirects**, while `_verified_fetch` deliberately installs `_NoRedirect` (1560–1563). A compromised or open-redirecting `nexusmill.com/version.json` can therefore bounce the fetch to an arbitrary host (SSRF / internal-metadata read). The 256 KB cap (1510) bounds the read and `zip_url`/`url` are host-checked downstream, so impact is limited — but the two fetchers should share one redirect-pinning helper.
- `_apply_pattern_rest` guards `len(P)` for the feather path (436) but not for `_depth_falloff(P, …)` at 429–430; `_depth_falloff`'s `P[:, ax].min()` / `d.max()` (1049, 1053) raise `ValueError` on an empty selection. Unreachable through today's callers (they all skip empty selections), but the guard is inconsistent — add `and len(P)` there too.
- `PATTERNSKIN_OT_generate_scales` still warns off a single axis (`_ach = s.scale_len_mm / nu`, 4458) while `PATTERNSKIN_OT_scale_from_outline` measures both (`_ach_x`/`_ach_y`, 4423–4428). The uniform `pitch_eff` clamp (4181–4183) makes the two near-equal in practice, but `nu = max(2, int(round(L / pitch_eff)))` can round up to ~5% coarser than `pitch_eff` at small `nu`, exactly the margin of the `> s.grip_pitch_mm * 1.05` threshold. Fold both operators onto one helper that reports `max(_ach_x, _ach_y)`.

## Fixed since last review
All previous findings verified resolved in the current bytes:
- **`sel_strokecut` polygon/triangle index-space mix** — `_cut` now converts once via the `tp` map (`ta = np.where(tp == fa)[0]`, 7093), anchors on `np.unique(ctx.F[ta].ravel())` (7097), orients on `sel[ta].mean()` (7109), and guards a missed mesh (7094–7096).
- **`grip_pattern` Nyquist violation** — grid now derived from `count` (`size = min(8192, max(512, ceil(4n/16)*16))`, 1212) with `n = min(n, size // 4)` clamp and an honest `_log.warning` (1213–1216). (A residual on the grid *representation* is reported above.)
- **Scale `res = max(0.3, pitch/4)` floor** — now `res = max(1e-3, pitch / 4.0)` (4337, 4384); the only ceiling is the uniform cross-axis `pitch_eff` clamp (4181–4183) with a `_log.warning` (4184–4186).
- **Lithophane O(res²) Python-tuple spike** — rebuilt as numpy buffers written via `foreach_set` (4728–4752), winding preserved.
- **`install_accel` accepting `.` / `..` as pip tokens** — explicitly refused plus a PEP-503 leading-alnum requirement (3064–3065).
- **Truncating-in-place config writes** — `_atomic_write_text` (1370–1377) now backs `_save_user_presets` (1384), `_save_license` (1442), `_save_session_settings` (2289) and `_save_forge_path` (4554).
- **Promotions:** `PATTERNSKIN_OT_grow` calls `bm.faces.index_update()` (2965); `_AI_SHADE_PREV` is keyed by `sp.as_pointer()` (9023) and cleared in `unregister()` (9572); `generate_default_library`'s `EXEC_DEFAULT` paths report loudly (5709–5715); `_PSCancellableApply.modal` re-asserts active object + Object Mode across the modal gap (670–677).

---

## In-session verification + remediation (2026-09-24, round 6)

All 4 findings verified; the HIGH was a REAL bug in the lead's own r3 restructure (the
_SELF_UPDATE reset placed after the thread start: worker-first write clobbered -> Esc dead;
fast-fail worker -> done reset -> permanent RUNNING_MODAL with BUSY released -> second
worker possible). The adversary independently confirmed the full trace byte-by-byte and
confirmed the lead's original "cancel untouched" rationale was misplaced (the refusal
early-return protects cancel, not the reset's position - now stated in the code comment).

Adversary gate round 6: APPROVE WITH MODIFICATIONS, folded in: the hoist anchored BETWEEN
the claim and the thread start (never above the refusal check); the ordering test rewritten
as the Event-synchronized thread-entry assertion (the lead's first formulation asserted the
opposite of the fixed code); R6-3's non-dict settings coerce (not error); grip grid rebuilt
as broadcast float32 1-D ramps (the adversary verified every _grip_field branch is dtype-
and broadcast-safe); _depth_falloff guarded at function level; the r1/r2 test seams updated
for the new build_opener path in _check_update.

Fixes: R6-1 reset hoisted + Esc/cancel phase whitelist ("start","download"; the two-phase
install stays non-cancellable); R6-2 _load_license isinstance gate + the license line
inside _stamp_stl_header's try; R6-3 ps_recipe dict guards (non-dict data -> the existing
"unreadable" report; non-dict settings -> coerced); R6-4 grip_tile_mm max=250 + float32
ramp grid (~2.1GB -> O(N) ramps); promos: _check_update redirect-pinned opener,
_depth_falloff empty-P guard, generate_scales both-axis warning.

Tests: tests/test_hunt_r6_fixes.py 14/14 PASS (thread-entry ordering, done-not-clobbered,
whitelist source pin, the hostile-license triad incl. Export STL success, hostile recipes,
float32 grid shape/dtype/ptp, tile cap, falloff guard, opener pin). r1-r5 probes + smoke
re-passed after the seam updates. NOT COMMITTED.
