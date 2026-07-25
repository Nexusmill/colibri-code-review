# QUALITY review: PatternSkin\__init__.py

- source: `C:\Users\User\source\repos\Nexusmill\PatternSkin\__init__.py`
- model: moonshotai/kimi-k3
- reviewed: 2026-07-19 19:39
- tokens: in 100024 / out 2946
- est cost: $0.3443

---

# Code Quality Review: `PatternSkin/__init__.py`

## Health score
4/10 — A ~5,800-line god module mixing geometry kernels, IO, licensing, networking, installers, and UI; strong math code is buried under heavy duplication and silent error-swallowing.

## Improvements

**[HIGH] Split the module by responsibility** - whole file
- Issue: One file contains numeric kernels (projections, sweeps), mesh construction (grips/scales/lithophane), preset data, licensing/update networking, pip installers, selection tools, AI-parts orchestration, Spector/Forge bridges, and the entire panel tree. There is already a working pattern (`filmstrip`, `ai_parts`, `selectcore`, `accel`, `printfit`) — most of this file belongs in similar siblings. Navigating, reviewing, and testing any one feature currently requires loading the whole file.
- Better: Carve out `geometry.py` (lines 49–360, 958–1040), `presets.py` (1062–1409), `licensing.py` (1270–1354), `library.py` (557–836), `export.py` (2045–2210), `selection_ops.py` (4318–4716). `__init__.py` keeps only `bl_info`, settings, registration. Each new module should own its state instead of writing this module's globals (see `_previews_reset` note below).

**[HIGH] `apply_pattern` is a 190-line god function** - `apply_pattern` (line 364)
- Issue: It mutates global Blender state (mode, selection, modifiers), subdivides, autofits, projects, anti-aliases, displaces, shades, decimates, and returns a mixed report dict. It cannot be unit-tested without a live Blender scene, and its 14 keyword args are manually re-passed from four different call sites (apply, preview, batch, regions, parts — five, actually), which is already drifting: `PATTERNSKIN_OT_batch_apply` hard-codes `invert=False/gamma=1.0/contrast=1.6` and drops `autofit_tiles`/`smooth_base`.
- Better: Introduce a params dataclass and phase functions:
  ```python
  @dataclass(frozen=True)
  class ApplySpec:
      mode: str = "AUTO"; tile_mm: float = 12.0; depth_mm: float = 0.3
      raised: bool = True; selected_only: bool = True; target_edge: float = 0.3
      ...

  def apply_pattern(obj, tile, spec: ApplySpec, tile2=None): ...
      P, N, sel = _read_vertices(obj.data, spec.selected_only)
      mode, P, N, sel = _resolve_mode(spec.mode, P, N)
      u, v = _PROJECTORS[mode](P, N, spec.tile_mm)
      ...
  ```
  Call sites build `ApplySpec.from_settings(s)` once — eliminates the per-site kwarg drift.

**[HIGH] Four near-identical icon loader functions** - `_brand_icon`, `_section_icon`, `_sec_icon`, `_header_icon`, `_extras_icon` (569–675)
- Issue: Five copies of the same load-into-`_BRAND`-collection pattern, each ~15 lines, differing only in the name and file. `_sec_icon` and `_header_icon` even differ only in which dict they consult.
- Better: One helper: `def _icon(preview_name, filename): ...` and `_sec_icon(key)` = `_icon(name, name + ".png")` after the dict lookup. ~60 lines → ~15, and future icons stop being copy-paste.

**[HIGH] Blanket `except Exception: pass` everywhere** - e.g. lines 25, 54, 543, 580, 688, 898, 943, 1291, 1320, 1800, 2146
- Issue: ~50 silent swallows make real failures (typos, API changes across Blender versions — the file explicitly supports 4.0 through 5.x) invisible. Some are justified and commented (draw-loop safety, optional deps); most are not, e.g. `_punch_holes` countersink failure (2759), `_apply` solver fallback (2588).
- Better: Catch narrow exceptions where you know the cause; elsewhere, log: add a tiny `_dbg(...)` that appends to `s.accel_status`/console in debug builds, and use `except (AttributeError, RuntimeError):` for Blender-API-version shims like the STL exporter (2188, already good).

**[HIGH] Duplicated reset/cache logic scattered with different behavior** - `_previews_reset` (808) vs inline resets (2308, 2882, 3022, 3040)
- Issue: Four places duplicate the "remove `_PREVIEWS` if set" dance; only `_previews_reset` also clears `_LIB_EMPTY_CACHE`. So `refresh_library`, `generate_ai`, `generate_grip`, `make_seamless` each leave the empty-cache stale in a way `choose_pattern` doesn't. This is exactly the kind of divergence a shared helper exists to prevent. (Also, line 809 puts a statement *before* the docstring, so `_previews_reset` has no docstring at all.)
- Better: All call `_previews_reset()`; delete the four inline copies.

**[MEDIUM] Module-level mutable globals as hidden coupling** - `_PREVIEWS`, `_ENUM_CACHE`, `_LIB_EMPTY_CACHE`, `_LICENSE`, `_UPDATE`, `_DEP_UPDATES`, `_INSTALLING`, `_AI_PARTS_CACHE`, `_SEL_WAS_EDIT`, `_REPROBE_COUNT`
- Issue: State is spread across ~15 globals; submodules mutate this module's `_PREVIEWS` across boundaries (comment at 810 acknowledges the problem). `apply_pattern` reads `bpy.context` directly, coupling geometry to UI state. This kills testability and makes add-on reload behavior fragile.
- Better: Group into small state objects owned by their feature module (`class PreviewCache`, `class DepManager`), pass context explicitly into pure functions. The projection/geometry functions are already pure — keep that boundary sharp by pushing every `bpy`/`context` touch outward.

**[MEDIUM] `PatternSkinSettings` has ~75 properties across 7 unrelated features** - line 1411
- Issue: One PropertyGroup for pattern, grip, scales, litho, batch, regions, AI parts, selection, print, licensing-adjacent fields. The triplicated enum sets (`batch_mode`, `region_mode`, `mode` at 1421/1593/1607) and (`batch_relief`, `region_relief`, `relief`) are literal copy-paste — a new projection mode (and you've added `SWEPT3D` recently) must be edited in 3+ places.
- Better: One shared `_PROJECTION_ITEMS` / `_RELIEF_ITEMS` constant; split settings into `PatternSettings`, `GripSettings`, `LithoSettings`, `AISelectionSettings` sub-PropertyGroups with `PointerProperty`s. Presets then only touch the relevant group.

**[MEDIUM] `_build_scale_from_outline` duplicates `_extrude_scale_mask`** - 2681–2761 vs 2509
- Issue: ~60 lines of identical vertex/face/wall construction. The helper `_extrude_scale_mask` already exists and is used by `_build_scale`; the outline builder inlines the same logic instead of computing `cell` + grids and delegating.
- Better: End `_build_scale_from_outline` at `cell = inside_img[np.ix_(yi, xi)]` and `return _extrude_scale_mask(context, gx, gy, cell, kind, pitch, depth, T, name="PS_Scale")`, then handle countersink. Removes the risk of the two watertightness fixes (loose-vert delete, normal recalc) drifting apart — they already have.

**[MEDIUM] Dead or vestigial code** - several symbols
- Issue:
  - `PATTERNSKIN_OT_ai_parts_regran._ctx_of` returns `None` and `_ap_regran` wraps a one-liner — dead scaffolding (5308–5332); the class isn't even registered in `_classes`.
  - `_SelMesh` import of `view3d_utils` at module top (32) is shadowed by function-local imports (4575, 4676).
  - Duplicate `af = res.get("autofit")` at 1782 and 1788.
  - `PATTERNSKIN_PT_extras`/`_PSExtra` panels are registered structurally but the accordion calls `draw` via `_PSShim`, so the extra panel classes' own registration path is half-unused.
  - `import view3d_utils` (32), `import re` inside `_sanitize_preset_name` (1244) shadows the top-level `re`.
- Better: Delete dead operators/helpers; keep one import site per name; use `from bpy_extras.view3d_utils import region_2d_to_origin_3d, region_2d_to_vector_3d` once.

**[MEDIUM] Duplicated operator boilerplate: paired copies and mode-flip dances** - many operators
- Issue: `PATTERNSKIN_OT_generate_scales` and `_scale_from_outline` share the whole "copy, offset, reselect, report" tail (2782–2792 vs 2811–2821). Export operators duplicate the print-notes sidecar block (2138–2147 vs 2198–2207). Nine operators repeat `if context.mode != "OBJECT": bpy.ops.object.mode_set(...)` plus the mesh-type guard.
- Better: Extract `_spawn_pair(a, gap)` helper, `_write_print_notes(fp, s, faces)`, and a decorator/context manager for the mode guard:
  ```python
  with object_mode(context):
      ...
  ```

**[LOW] Naming and local style** - various
- Issue: Single-letter names dominate the math (`P, N, u, v, cs, sv, nin, bin_`) — tolerable in kernels but they leak into long bodies (`apply_pattern`, `_write_3mf`). `_nv0`, `_co0`, `_s0` (389–397) are non-idiomatic throwaway names; `import math as _math` inside `apply_pattern` (538) despite top-level `math`; `import numpy as _np`/`as np` function-local re-imports (925, 4327, 4725...) though `np` is module-global.
- Better: Rename scratch vars to intent (`verts_sel`, `extent`, `ratio`); drop all function-local `import numpy`/`import math` where the module already imports them.

**[LOW] Comment/docstring hygiene**
- Issue: Section banners (`# ──…──`) help, but there are orphan banners (1043 "slicer notes" precedes unrelated content). Some docstrings document history rather than contract ("used to hard-error", "the old trailing arrow floated..."). History belongs in git/changelog; a comment at 3584's level ("could not draw this section") explains nothing about recovery.
- Better: Keep "why" comments for non-obvious geometry/Blender quirks (these are genuinely good, e.g. enum-stability notes), move war stories to docs/CHANGELOG.

## Quick wins
- [ ] Merge `_brand_icon`/`_section_icon`/`_extras_icon` into one `_icon(name, file)` helper.
- [ ] Replace all inline `_PREVIEWS` resets with `_previews_reset()`; move the stray statement at line 809 below the docstring.
- [ ] Extract `_PROJECTION_ITEMS`/`_RELIEF_ITEMS` constants; delete the 3 duplicate enum definitions.
- [ ] Make `_build_scale_from_outline` delegate to `_extrude_scale_mask`.
- [ ] Delete `PATTERNSKIN_OT_ai_parts_regran` (unregistered, stub methods) or finish wiring it.
- [ ] Remove duplicate `af = res.get("autofit")` (1788).
- [ ] Remove function-local `import numpy`/`import math`/`import re` where already top-level; remove shadowing `import re` in `_sanitize_preset_name`.
- [ ] Extract `_write_print_notes(fp, s, faces)` used by both export operators.
- [ ] Fix the four blank-line gap at 1865–1868; add a module docstring.
- [ ] Convert the `accel` try/except import (43–46) to a single `importlib`-based helper shared with `keystore`-style fallbacks.

## What's done well
- The math kernels (`_parallel_transport_frames`, `_resample_polyline`, `project_*`, `grip_pattern`) are pure numpy, well-documented with the *why*, and explicitly testable — the author knows where the testable boundary is.
- Blender-API pitfalls (enum reference stability, preview-collection GC, Edit-Mode attribute sizing, pip file locking on Windows) are handled deliberately with explanatory comments and the right abstractions (`_PSShim`, modal pip with timers).
- User-facing robustness is thoughtful: autofit/planar/selection fallbacks warn instead of failing, and paid-API calls get idempotent caching and tolerant polling.