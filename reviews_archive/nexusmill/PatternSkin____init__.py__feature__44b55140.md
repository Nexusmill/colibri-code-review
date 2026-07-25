# FEATURE review: PatternSkin\__init__.py

- source: `C:\Users\User\source\repos\Nexusmill\PatternSkin\__init__.py`
- model: moonshotai/kimi-k3
- reviewed: 2026-07-19 19:40
- tokens: in 100023 / out 1849
- est cost: $0.3278

---

## What this module does

It's the entire Pattern Skin Blender add-on in one file: it loads SVG/PNG patterns as normalized heightmaps, projects them onto meshes via five projection modes (planar/cylindrical/swept/swept-3D/triplanar), displaces vertices as raised/engraved relief, and wraps that in a large UI (presets, pattern library browser, AI texture generation via Replicate, AI part segmentation, grip/knife-scale generators, lithophanes, export to STL/3MF, and a dependency-installer panel).

## Suggested add-ons

**Apply as modifier stack / non-destructive relief** — Value: High · Effort: L
- What: Offer "Apply as modifier" that builds the relief via a Displace modifier + generated texture instead of destructively subdividing and displacing the mesh in `apply_pattern`.
- Why: Today every Apply is a one-way commit (subdivide up to 700k faces, displace, optional decimate). Users iterating on tile size/depth must undo or re-import. A non-destructive path matches the existing Preview operator's spirit but keeps it editable.
- How: In `PATTERNSKIN_OT_apply.execute`, add an `as_modifier` branch: reuse `load_heightmap` + the projection chosen in `apply_pattern` to bake a UV-free displacement texture (or write per-vertex weights to a vertex group), then add a `DISPLACE` modifier referencing it. The existing `ps_preview_of` custom-prop machinery (`_clear_previews`, `PATTERNSKIN_OT_preview`) is the template for lifecycle management.

**Per-application timing + stats log** — Value: High · Effort: S
- What: Record elapsed time, vertex/face counts, chosen projection, autofit decisions per Apply/Preview/Batch into a ring buffer, shown in the Print/Apply panel and optionally written to a log file.
- Why: `apply_pattern` already returns a stats dict (mode, verts, faces, autofit) but it's only surfaced as one-off `report()` toasts that vanish. On heavy meshes (max_faces=700k, 40 subdivide iterations) users have no idea why an apply took 90 seconds, and support requests ("Get help on Superhive") have no diagnostics attached.
- How: Wrap the `apply_pattern` call in `PATTERNSKIN_OT_apply.execute` with `time.perf_counter()`, append `{ts, obj, res, ms}` to a module-level deque; add a collapsible "Recent applies" row in `PATTERNSKIN_PT_apply` drawing the last few entries. Extend `s.last_error` handling to include the log tail.

**Heightmap / pattern cache keyed by (path, mtime, tone params)** — Value: High · Effort: M
- What: Memoize `load_heightmap` results (and the `_aa_pool` output) so Preview → tweak depth → Apply doesn't re-decode the same 1024px image, and batch/region bakes don't reload the same tile per object.
- Why: `PATTERNSKIN_OT_batch_apply` already hoists one `load_heightmap` out of the loop, but Preview-then-Apply (the guided workflow) decodes the image twice, and `PATTERNSKIN_OT_bake_regions` reloads per region even when two regions share a pattern. SVG rasterization via cairosvg is especially expensive and deterministic.
- How: Module-level dict `_HM_CACHE[(abspath, mtime, invert, gamma, contrast, black, white)] = array`; check in `load_heightmap`. Cap at ~4 entries LRU. Invalidate in `_previews_reset`.

**Auto-save/restore scene settings** — Value: Med · Effort: S
- What: Persist key PatternSkinSettings (mode, tile_mm, depth_mm, resolution, library_dir, nozzle/layer) across Blender sessions via a JSON in the CONFIG dir, like `_user_presets()` already does.
- Why: Presets exist, but a user who dialed in a recipe without saving it as a preset loses everything on restart; `library_dir`, nozzle, and layer height are workflow constants users re-enter every session.
- How: Mirror `_user_presets_path()`/`_save_user_presets()`: a `_session_settings.json` written on Apply (debounced) and read in `register()` after `PointerProperty` creation, skipping FILE_PATH props that no longer exist.

**Retry with backoff for AI generation + pre-flight cost confirm** — Value: Med · Effort: M
- What: `_replicate_generate` calls in `_gen_texture_to_library` and the SAM polling in `PATTERNSKIN_OT_ai_parts.modal` currently fail hard on any transient error (the native scan's `_poll_errs` 5-strike tolerance is the exception — it exists only there because it's paid). Extend that retry pattern to texture generation, and add an invoke-time confirmation showing the estimated cost before any paid call.
- Why: A network blip mid-generation wastes a paid call and dumps a raw error into `s.last_error`. Users already see prices in the enum labels ("flux-dev ($0.025)") but get no "this will cost ~$X, continue?" gate.
- How: Extract the poll-retry logic from `PATTERNSKIN_OT_ai_parts_native.modal` into a shared `_retry(fn, attempts, backoff)` helper in this module; use it in `_gen_texture_to_library`. Add `invoke()` to `PATTERNSKIN_OT_generate_ai` showing `invoke_props_dialog` with the cost from `_REPLICATE_MODELS`.

**Headless / scriptable API entry point** — Value: Med · Effort: S
- What: A documented `patternskin_apply(obj, pattern_path, **kwargs)` public function usable from Blender's scripting console or `--background` mode without the panel.
- Why: `apply_pattern` is already UI-free (pure mesh math), but it takes a pre-loaded tile array and no scene settings; batch-processing a folder of STLs with a texture (a natural fit given the existing batch operator and export operators) currently requires reimplementing `load_heightmap` plumbing.
- How: Thin wrapper: `def api_apply(obj, pattern, mode="AUTO", tile_mm=12, depth_mm=0.3, ...)` that calls `load_heightmap` + `apply_pattern` and returns the stats dict. Register a `patternskin.api_apply` operator with properties so it also appears in F3/macros.

**Structured error diagnostics bundle** — Value: Med · Effort: S
- What: A "Copy diagnostics" button next to the support button that assembles: version, platform, `accel.capabilities()`, `accel.dep_status()` for all deps, `s.accel_status`, `s.last_error`, recent log entries — onto the clipboard.
- Why: Support flows through Superhive (`PATTERNSKIN_OT_support`) with zero context; the user must manually transcribe what the Technology Stack panel already computes.
- How: New operator in `PATTERNSKIN_PT_system`; use `bpy.context.window_manager.clipboard = text`. All data sources already exist (`_dep_installed`, `accel.tech_status`, `bl_info`).

## Nice-to-haves

- **Seam-score badge in the library browser**: `tiling_score()` exists but is only used inside Make Seamless; computing it lazily per library item and flagging poor tiles would guide users before they apply.
- **Duplicate `af = res.get("autofit")`** at lines 1782 and 1788 — dead second fetch, trivial cleanup.
- **`_RESAMPLE`/KD-tree quality metrics for SWEPT3D**: `project_swept3d` silently falls back to `project_swept` when the skeleton is too small (`m < 4`); surface that fallback in the result dict like `planar_fallback` so the user knows.
- **Unit-scale guardrail**: the autofit warning already detects unit mismatch; add a one-click "Set scene to mm" operator when detected.
- **Cancel support for long applies**: subdivision loop (up to 40 iterations to 700k faces) has no cancel; a modal apply with Esc (like `PATTERNSKIN_OT_ai_parts`) would help on big meshes.
- **Preset thumbnails**: presets reference library textures (`_find_library_type`); showing the pattern's existing `_PREVIEWS` thumbnail beside the preset dropdown would make preset choice visual.
- **`_scan_library` async**: 300-file walk runs inside the enum callback on redraw; a background scan populating a cache (like `accel.probe_scipy_async`) would keep the panel snappy on network drives.