# BUG review: PatternSkin\__init__.py

- source: `C:\Users\User\source\repos\Nexusmill\PatternSkin\__init__.py`
- model: moonshotai/kimi-k3
- reviewed: 2026-07-19 19:37
- tokens: in 100066 / out 5585
- est cost: $0.3840

---

## Verdict
Ship with fixes. Nothing here is remotely exploitable (no injection/traversal — the zip install path is properly guarded at line 3719, and pip installs are wheel-only with an index allowlist), but there are three real correctness defects: the viewport ray-pick math subtracts an already-relative coordinate (wrong face selected whenever the region isn't at origin), the selection-geometry cache key ignores vertex positions (stale selections after relief is applied), and a persistent timer survives `unregister()`.

## Bugs & vulnerabilities

**[HIGH] Ray-pick coordinates double-offset by region origin** - `lines 4581, 4679, 5471`
- What: `co = (event.mouse_region_x - region.x, event.mouse_region_y - region.y)` — `event.mouse_region_x/y` are *already relative to the region*. Subtracting `region.x/y` again shifts the ray.
- Trigger: any pick (`sel_click`, `sel_strokecut`, `ai_pick`) in a viewport whose region is not at window origin — i.e. almost always, once the sidebar (N) or toolbar (T) is open.
- Impact: ray-cast hits the wrong face (or misses the mesh) by the region's pixel offset; users select the wrong part / get spurious "clicked off the model" warnings. Since the add-on's whole UX lives in the N-panel, the offset is non-zero in the default configuration.
- Fix: use `co = (event.mouse_region_x, event.mouse_region_y)` in all three sites.

**[HIGH] Selection context cache key ignores geometry changes** - `lines 4329–4334`
- What: `_sel_ctx` keys the cached `MeshCtx` on `obj.name + vertex count + triangle count` only. `apply_pattern` (line 531–532) displaces every selected vertex *without changing counts*.
- Trigger: Apply a pattern, then run Smart Select / region grow / AI parts on the same object without adding geometry.
- Impact: curvature fields, geodesic distances, and harmonic cuts are computed on the pre-displacement mesh — selections land in the wrong places, silently.
- Fix: include a cheap geometry fingerprint in the key (e.g. hash of the `co` buffer, or a per-mesh dirty counter bumped after `foreach_set("co", ...)`), or invalidate the cache in `apply_pattern`.

**[MEDIUM] Persistent timer leaks across unregister()** - `lines 905–945, 5819, 5824–5840`
- What: `_ps_autoload_tick` is registered with `persistent=True` and returns `1.0` (runs forever), but `unregister()` removes none of the timers.
- Trigger: disable/re-enable the add-on (or reload scripts F8).
- Impact: the old timer keeps firing against the stale module copy after unregister; re-registering adds a *second* autoload timer, and they accumulate on every reload. Both mutate scene state (`ai_parts_count`, overlays) and force redraws forever.
- Fix: in `unregister()`, call `bpy.app.timers.unregister(_ps_autoload_tick)` inside a try/except (same for any other non-one-shot timers).

**[MEDIUM] `_parallel_transport_frames` crashes on a 1-node path** - `lines 186–187`
- What: `T[0] = path[1] - path[0]` and `T[-1] = path[-1] - path[-2]` index `path[1]`/`path[-2]` unconditionally.
- Trigger: `project_swept3d` where the NN-walk breaks immediately (`nxt is None` on the first iteration, line 318) leaves `order` of length 1; `_resample_polyline` returns short paths unchanged (line 224–225), so a length-1 path reaches this function.
- Impact: `IndexError` on degenerate skeletons — the very meshes the SWEPT3D fallback logic is supposed to rescue.
- Fix: guard `if m < 2: return` early in `project_swept3d` (fall back to `project_swept`), or make `_parallel_transport_frames` handle `m == 1` with a default tangent.

**[LOW] Unclosed file handles** - `lines 685, 2145, 2205, 5638`
- What: `_json.load(open(sp, ...))`, `open(...).write(note)`, and `open(path).read()` never close the handle (relying on CPython refcounting).
- Trigger: normal use; under non-CPython or heavy churn the descriptor lingers.
- Impact: resource leak; on Windows a lingering handle can also block a subsequent overwrite of the same notes file.
- Fix: use `with open(...) as f:` everywhere.

**[LOW] Shared fixed temp filename for SVG rasterization** - `lines 60–63`
- What: `_rasterize_svg` always writes `bpy.app.tempdir/_patternskin_svg.png`.
- Trigger: two pattern loads in one session (e.g. `tile` and `tile2` both SVG, or batch apply over multiple objects with SVG patterns) — the second rasterization overwrites the first before/while it's loaded.
- Impact: `load_heightmap` may read the wrong image (wrong relief) or a partially written file.
- Fix: use `tempfile.mkstemp(suffix=".png")` per call (or include a counter/pid in the name).

**[LOW] Autofit warning hardcodes "~6 tiles"** - `lines 400, 1786`
- What: the actual tile count is `autofit_tiles` (preset-tunable, 1–12), but the report string says "~6 tiles" unconditionally.
- Impact: misleading user-facing message whenever a preset overrides the hint (several presets use 1, 2, 3, 8).
- Fix: format the actual `autofit_tiles` value into the message.

## Missing safeguards
- No unit tests for the pure-numpy cores that are explicitly designed to be testable (`_parallel_transport_frames`, `_resample_polyline`, `sample_tiled`, `_depth_falloff`, `make_seamless`, `_combine_heights`) — degenerate inputs (empty/1-point paths, constant tiles, zero-span meshes) are exactly where the crashes above live.
- `load_heightmap` never validates `img.size != (0, 0)` after load (line 78) — a corrupt/undecodable image raises an opaque reshape error instead of "couldn't read image".
- `PATTERNSKIN_OT_choose_pattern.execute` (line 3755) silently returns `FINISHED` when the file path is invalid — should report an error.
- `PATTERNSKIN_OT_export_stl.execute` (line 2183–2185) clears the whole selection and never restores it; restore prior selection/active object in a `finally`.
- The pip-install operator accepts arbitrary `packages` strings via `bpy.ops` with no allowlist — wheel-only + index pinning is good, but a package-name allowlist (`scipy`, `torch`, `cairosvg`, …) would close the last supply-chain gap for scripted invocations.
- `_check_update_async` thread writes the global `_UPDATE` dict with no synchronization and swallows all exceptions into a 80-char string — at minimum log failures; consider posting the result via `bpy.app.timers` instead of mutating shared state from a thread.