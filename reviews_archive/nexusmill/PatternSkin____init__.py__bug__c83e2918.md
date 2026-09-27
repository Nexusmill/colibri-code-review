# BUG review: PatternSkin\__init__.py

- source: `C:\Users\User\source\repos\Nexusmill\PatternSkin\__init__.py`
- model: xiaomi/mimo-v2.6-pro
- reviewed: 2026-09-24 12:05
- tokens: in 187565 / out 55789
- est cost: $0.1301

---

## Verdict
Not safe to ship as-is: the round‑6 fix to `grip_pattern`'s grid introduced a **shape regression** — two of the seven grip kinds now return a degenerate `(size,1)`/`(1,size)` array instead of the promised square heightmap, silently corrupting (or hard‑failing) four of the twelve shipped grip presets. Everything else is medium/low robustness around stale caches and uncontained modal callbacks.

## Bugs & vulnerabilities

**[HIGH] `grip_pattern` collapses to a degenerate 2‑D shape for `RIB` and `KNURL_STRAIGHT` after the broadcast‑ramp change** - `line 1226`
- What: R6‑4 replaced `yy, xx = np.mgrid[0:size, 0:size] / size` (both `(size, size)`) with broadcast 1‑D ramps — `yy = _u[:, None]` shape `(size, 1)` and `xx = _u[None, :]` shape `(1, size)` (1223–1225) — then calls `_grip_field(kind, xx, yy, n, n, hex_int=True)` (1226), i.e. `U` is `(1,size)`, `V` is `(size,1)`. Every branch that touches **both** `U` and `V` broadcasts to `(size, size)` (`KNURL_DIAMOND` 1178, `CROSSHATCH` 1181, `HEX` 1183–1193, `DIMPLE` 1195, `PYRAMID` 1197–1199) — those are fine. But two branches use **only one** operand and therefore never broadcast:
  - `RIB`: `a = 0.5 + 0.5 * np.cos(tp * V * nv)` (1176–1177) → shape **`(size, 1)`**
  - `KNURL_STRAIGHT` / default: `a = 0.5 + 0.5 * np.cos(tp * U * nu)` (1200–1201) → shape **`(1, size)`**
  
  `np.clip(a, 0.0, 1.0)` (1202) preserves the degenerate shape and `grip_pattern` returns it with no shape check. Previously the full `mgrid` guaranteed `(size, size)` for every kind, so this is a regression in the fix itself.
- Trigger: pick any of the shipped presets **PEN**, **KNOB**, **BIKE** or **RIBBED** (all map to `KNURL_STRAIGHT`/`RIB`, 1805–1813) or set Grip = *Ribbed* / *Straight knurl*, then **Generate grip texture** (`PATTERNSKIN_OT_generate_grip.execute`, 4538–4557). The three `grip_mode == "SCALES"`/`SLEEVE"` paths are unaffected — `_grip_height` feeds `_grip_field` genuine 2‑D grids.
- Impact: `grip_pattern`'s documented contract ("perfectly-seamless grip heightmap", 1205–1208) is violated. Downstream, `a = make_seamless(a, margin=0.06)` at **4542 runs outside the `try`** (which starts at 4545), so any shape‑sensitive operation there (a `margin = int(min(H,W)*margin)` slice becomes `int(1*0.06) == 0`, and `a[:, -0:]` degenerates to the whole array) raises straight out of `execute` as a raw traceback. If it survives, `_save_gray_png` writes a **1‑pixel‑wide/1‑pixel‑tall PNG** into `<library>/grips/`, which then renders as a sliver in the library icon grid, makes `tiling_score`/`_update_seam_score` (4554) measure a meaningless seam, and disables `_aa_pool`'s anti‑alias pooling entirely (`k = int(min(shape) // (1.6*spt))` is `0` for `min(shape) == 1`, 337–339), re‑opening the "glitter"/aliasing defect the pooling exists to fix.
- Fix: force the output back to the promised square after the call, without re‑introducing the mgrid cost:
  ```python
  a = _grip_field(kind, xx, yy, n, n, hex_int=True)
  return np.ascontiguousarray(np.broadcast_to(a, (size, size)), dtype=np.float32)
  ```
  (or make each single‑operand branch broadcast explicitly). Pin with a parametrized test asserting `grip_pattern(k, n).shape == (size, size)` **for all seven kinds**.

**[MEDIUM] `_AI_PARTS_CACHE` `tp`/`labels` are never invalidated when the mesh changes — wrong part selections, or `IndexError` on the decimate path** - `line 7225`
- What: `_AI_PARTS_CACHE[obj.name]` (7158) stores `"tp"` (tri→poly map) and `"labels"` captured at scan time. `_ai_select_part` does `acc = np.zeros(npoly)` with `npoly = len(me.polygons)` (**current** mesh) and then `np.add.at(acc, tp, trisel)` (7225) with the **stale** `tp`; `_ai_poly_part` does `best = np.full(npoly, -1)` then `best[best_polys] = …` (7192) with stale polygon indices. `_ai_cache_hydrate` is supposed to be the guard, but its very first statement short‑circuits on the populated cache: `if ent.get("tp") is not None and ent.get("labels") is not None: return True` (**8787**) — with **no geometry check**. Compare `_sel_ctx`, which deliberately folds a `sha1(V.tobytes())` fingerprint into its key (6675–6678) precisely because "a name+counts key served a stale ctx and selections landed on pre‑relief geometry". `_AI_PARTS_CACHE` never got that treatment.
- Trigger: run an AI part scan → run **Apply Pattern Skin** (subdivides; the `ps_ai_part` attribute correctly survives per PSK‑ULTRA‑6, but `ent["tp"]`/`ent["labels"]` do not) → click **Pick a part on the model** (`PATTERNSKIN_OT_ai_part_pick.execute`, 8817) or **Fewer/More** (`PATTERNSKIN_OT_ai_detail.execute`, 9170) or **Re‑derive detail** (8848). With **Decimate to faces** enabled on the Apply, the face count *shrinks*.
- Impact: on the grow path the selection silently lands on the wrong (pre‑subdivision) face indices — `polysel` is `> 0.5` over `new_npoly` rows of which only the first `old_npoly` carry votes, so the revealed "part" is an arbitrary subset of the subdivided mesh. On the shrink path `best_polys`/`tp` exceed `npoly` and `best[best_polys]` / `np.add.at` raise an uncaught **`IndexError: index N is out of bounds for axis 0 with size M`** out of `execute`.
- Fix: store `ent["sig"] = sha1(V.tobytes())[:12] + ":" + str(len(me.polygons))` at cache‑write time and have `_ai_cache_hydrate` drop (and re‑derive `tp` for) any entry whose signature no longer matches **before** returning `True`; alternatively make `_ai_poly_part`/`_ai_select_part` clamp/validate `tp` against `npoly` and return a clean failure instead of indexing blindly.

**[MEDIUM] `_PSCancellableApply.modal` invokes `_ps_item_done` / `_ps_item_failed` outside any `try` — one exception strands the event timer and the modal handler for the session** - `line 688`
- What: in `modal()`'s TIMER branch, `_apply_pattern_rest(**self._ps_rest_kwargs)` is wrapped (682–686) but the completion callbacks are not:
  ```
  687	                self._ps_release_busy()
  688	                return self._ps_item_done(context, res)
  ```
  and symmetrically `return self._ps_item_failed(context, e)` (686) re‑raises whatever *it* throws. For the single‑item operators this is partly mitigated (`PATTERNSKIN_OT_apply._ps_item_done` calls `_ps_stop_timer` first, 2537) — but the **queue** operators do not: `batch_apply._ps_item_done` (4849–4852), `bake_regions._ps_item_done` (5002–5005) and `ai_bake_parts._ps_item_done` (8697–8700) immediately call `_*_start_current()`, which only stops/replaces the timer *inside* `_ps_start` (624) or `_*_finish`. Any raise before that point leaves `self._ps_timer` armed and `self._ps_gen = None` (set at 681), so every subsequent TIMER tick hits `if self._ps_gen is None: return {"PASS_THROUGH"}` (668–669) **forever**. `PATTERNSKIN_OT_apply._ps_item_done` also has ~100 lines of unguarded work after its timer stop — `_apply_finish` → `bpy.data.images.load(pattern_path)` (2238), `_APPLY_LOG.append({… "obj": obj.name …})` (2584), `obj["ps_recipe"]` (2597) — that escapes `modal()` as a raw traceback and skips the undo push.
- Trigger: select 2+ meshes, run **Batch apply to selected**, and delete the second object from the Outliner while the first is subdividing. When item 1 completes, `_bq_start_current` reaches `o.select_set(True)` (4837) on the freed RNA and raises `ReferenceError: StructRNA of type Object has been removed`. Same for `bake_regions` (4975, `obj.vertex_groups[…]` after the object is removed) and `ai_bake_parts` (8680, `obj.data.polygons[int(i)].vertices` when the stale `self._ap_pp` fallback at 8665 indexes past a decimated mesh).
- Impact: a permanent 0.01–0.5 s TIMER pump plus an unremovable `modal_handler_add` registration per incident (they accumulate across runs), `bl_options` UNDO never pushes, and for `PATTERNSKIN_OT_apply` a 'Keep original' duplicate can be left hidden with its source rolled back inconsistently (`cancel()` may not run on an exception‑terminated modal).
- Fix: contain the callbacks the same way the rest phase is contained, and always release resources on the way out:
  ```python
  self._ps_release_busy()
  try:
      return self._ps_item_done(context, res)
  except Exception as e:
      self._ps_stop_timer(context)
      self.report({"ERROR"}, str(e)[:160])
      return {"CANCELLED"}
  ```
  (mirror for `_ps_item_failed`), and have every queue's `_ps_item_done`/`_ps_item_failed` call `self._ps_stop_timer(context)` as its **first** statement, like `PATTERNSKIN_OT_apply` does at 2537.

**[MEDIUM] `install_default_library` fetches with an unbounded, redirect‑following `urlopen` — the one download path that bypasses `_verified_fetch`'s discipline** - `line 5542`
- What: 
  ```
  5540	                req = urllib.request.Request(DEFAULT_LIBRARY_URL, headers={"User-Agent": "patternskin/1.0"})
  5541	                with urllib.request.urlopen(req, timeout=60) as r, open(tmp, "wb") as f:
  5542	                    f.write(r.read())
  ```
  `urlopen` uses the default `HTTPRedirectHandler`, so it follows up to 10 redirects to **any** scheme/host (including `http://169.254.169.254/…` cloud‑metadata or internal RFC1918 services), and `r.read()` with no argument buffers the **entire** body in memory and then in the temp file with **no size cap**. `_verified_fetch` (1567–1595) exists precisely to prevent this and enforces all three: `pr.scheme != "https" or pr.hostname != _DOWNLOAD_HOST` (1573), `_NoRedirect` opener (1575–1578) and `cap = max_mb * 1024 * 1024` with per‑chunk checks (1580–1591). The sha256 pin (5543–5547) is checked only **after** the whole body has been buffered.
- Trigger: click **Install the included pattern library** while `downloads.nexusmill.com` (or anything in front of it) serves a 30x to a huge/internal URL — a compromised edge, a stale DNS record, or an open redirect.
- Impact: SSRF to internal hosts from the Blender process, and unbounded memory + temp‑disk growth on the **main thread** (this runs synchronously inside `execute`, 5519–5599) → Blender OOM/freeze before the integrity check can reject the payload. The temp file *is* cleaned up (5553–5557) but only after the damage is done.
- Fix: route this through `_verified_fetch(DEFAULT_LIBRARY_URL, DEFAULT_LIBRARY_SHA256, tmp, max_mb=400)` (drop the bespoke `urlopen` block and the separate `_sha256_file` compare), or at minimum install the same `_NoRedirect` opener and stream `r.read(1 << 20)` against a running total with a hard cap.

**[LOW] `_load_license` gates the container but not the leaf values — a hand-edited licence file still breaks the Activate dialog** - `line 6523`
- What: R6‑2 added `_LICENSE = raw if isinstance(raw, dict) else {}` (1443), which fixes the `.get` `AttributeError`. But the **values** are still unvalidated, and `PATTERNSKIN_OT_activate.invoke` assigns them straight into `StringProperty`s:
  ```
  6522	        lic = _load_license()
  6523	        self.name = lic.get("name", ""); self.order = lic.get("order", "")
  ```
  `{"name": 123}` / `{"name": null}` / `{"order": ["a"]}` passes the isinstance gate and then raises `TypeError` from the RNA string setter. `_license_line` (1454–1459) is immune (it only `%s`-formats), so the Settings panel and Export STL now work — but the one dialog that could rewrite the file is the one that still dies, exactly the "user cannot repair it from the UI" tail of the original finding.
- Trigger: `~/.config/blender/<ver>/config/patternskin_license.json` containing `{"name": 123, "order": null}`, then **Activate / personalise**.
- Impact: the operator aborts with a raw `TypeError` instead of opening; recovery still requires deleting the file by hand.
- Fix: coerce at the load boundary — `_LICENSE = {str(k): str(v) for k, v in raw.items() if isinstance(v, (str, int, float))}` (or simply `lic.get("name", "") or ""` passed through `str(...)` at 6523), mirroring the leaf sanitisation `_save_license` already applies via `_sanitize_license` (1447–1449).

## Missing safeguards
- `grip_pattern` needs a shape/contract assertion (and a parametrized test over **all seven** `_grip_field` kinds) that the result is `(size, size)` float32 in `[0,1]`; R6‑4's test only covered the grid's dtype/ptp, not `_grip_field`'s output shape per branch — which is exactly where the regression landed.
- `_AI_PARTS_CACHE` entries need the same geometry fingerprint `_sel_ctx` uses (6675–6678), validated in `_ai_cache_hydrate` **before** its early return at 8787 and before `_ai_poly_part`/`_ai_select_part` index current‑mesh arrays with `tp`.
- `modal()`'s completion path needs a single containment wrapper around `_ps_item_done`/`_ps_item_failed` that guarantees `_ps_stop_timer` + busy release + a user‑visible report on any exception; there is currently no test that a raising `_ps_item_done` terminates the modal.
- `install_default_library` should not have its own fetch implementation at all — one shared bounded/no‑redirect/hash‑pinned helper used by `_verified_fetch`, `_check_update` (1513, now pinned) and the library installer would close the last divergence.
- `_load_license` should validate/coerce leaf value types the way `_user_presets()` validates entry shape (1363–1373), and a test should assert `PATTERNSKIN_OT_activate` still opens with `null`/`int`/`list` values in the licence file.

## Fixed since last review
All four round‑6 findings verified resolved in the current bytes:
- **`self_update` `_SELF_UPDATE` reset ordering** — the reset now sits at **6603, between the `_SELF_UPDATE_BUSY = True` claim (6597) and `threading.Thread(...).start()` (6605)**, with the explanatory comment; `modal()`'s Esc test is a phase whitelist `in ("start", "download")` (6626) and `cancel()` mirrors it (6650).
- **`_load_license` non‑dict JSON** — `isinstance(raw, dict)` gate at 1443; `line = _license_line()` moved **inside** `_stamp_stl_header`'s `try` (1463–1466). (A residual on leaf value types is reported above.)
- **`recipe_from_object` untrusted `ps_recipe` shape** — `isinstance(data, dict)` + `raise ValueError("not an object")` (2657–2658) and `if not isinstance(settings, dict): settings = {}` (2660–2661).
- **`grip_pattern` allocation spike** — `grip_tile_mm` now has `max=250` (1946) and the grid is built from broadcast float32 1‑D ramps (1223–1226). (A **new shape regression** from this change is reported above.)

Promotions from the previous round also confirmed in place: `_check_update` now builds a redirect‑refusing opener (`_NR`, 1519–1523); `_depth_falloff` guards empty `P` at function level (1045–1046); `PATTERNSKIN_OT_generate_scales` warns off `max(_ach_x, _ach_y)` (4478–4482), matching `scale_from_outline`.

---

## In-session verification + remediation (2026-09-24, round 7)

All 5 findings verified; the HIGH was a shape regression from the lead's own r6 ramp change.
Adversary gate round 7: APPROVE WITH MODIFICATIONS, folded in: the AI-cache signature keys
TOPOLOGY (loop-triangle vertex indices + counts), NOT vertex positions - a vertex-hash would
falsely kill the cache on every displacement-only Apply and force PAID rescans, while a
same-counts re-triangulation would slip through; the pick degrade path (attribute-based
selection) did not exist and was wired; detail got the honest "mesh changed - re-run AI
Parts" message; the modal backstop is preceded by widening each queue driver's per-item try
to the WHOLE item body (a deleted object among twenty now skips ONE item instead of
aborting nineteen); _verified_fetch's _SELF_UPDATE coupling (cancel poll + progress writes)
is opt-in per call - a stale Esc'd update would otherwise kill every later library install
on its first chunk; the license leaf filter drops bools ("Licensed to True" into exported
STLs) and non-scalars rather than coercing.

Fixes: R7-1 ascontiguousarray(broadcast_to(a,(size,size))) in grip_pattern (both
single-operand branches square again; all seven kinds pinned) + make_seamless moved inside
generate_grip's try; R7-2 _ai_cache_sig (triangulation hash) at all six write sites +
hydrate gate before its early return + pick degrade + detail message; R7-3 _ps_item_done/
_failed_safe backstops (timer stopped, busy released, ERROR reported, CANCELLED) +
stop-timer-first in all six queue callbacks + three whole-item try widenings; R7-4 the
library install routes through _verified_fetch (max_mb=400, progress_key="" decoupled)
with the hash prefix kept in the integrity message; R7-5 license leaves filtered at the
load boundary (str/int/float, bools excluded).

Tests: tests/test_hunt_r7_fixes.py 15/15 PASS - all-seven-kinds square/float32/non-constant
sweep; displacement KEEPS the cache (no paid rescan) while a subdivide DROPS it; the
backstop contains a raising _ps_item_done (timer stopped, CANCELLED); the decoupled fetch
survives a stale cancel flag while the coupled one honours it; hostile license leaves
filtered. r1-r6 probes + smoke re-passed. NOT COMMITTED.
