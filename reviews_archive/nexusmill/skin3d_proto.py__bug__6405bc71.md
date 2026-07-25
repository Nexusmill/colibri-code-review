# BUG review: skin3d_proto.py

- source: `C:\Users\User\source\repos\Nexusmill\skin3d_proto.py`
- model: moonshotai/kimi-k3
- reviewed: 2026-07-19 20:56
- tokens: in 3464 / out 2171
- est cost: $0.0430

---

## Verdict
Mostly solid for a prototype — input validation in `apply_skin` is unusually good — but not fully safe to ship as a CLI: several CLI-facing parameters (`--rows`, `--sharpness`, `--amplitude-mm`) are unvalidated and produce crashes or silently flat output. Biggest single risk: `--rows 0` / negative `--rows` crashes or silently emits a featureless tile.

## Bugs & vulnerabilities

**[MEDIUM] `--rows 0` crashes, `--rows < 0` silently produces an empty pattern** - `line 33` (validated nowhere; entry at `line 150`)
- What: `sx = 1.0 / rows` raises `ZeroDivisionError` when `rows == 0`. For `rows < 0`, `range(-2, rows + 2)` is empty, so `h` stays all-zeros and `_normalize01` returns a flat zero tile — relief silently disappears.
- Trigger: `python skin3d_proto.py in.stl out.stl --rows 0` (or any negative value).
- Impact: unhandled traceback, or worse, a successful export with *no pattern applied* — a silent failure, the exact failure class the docstring at line 98–99 says is the worst outcome.
- Fix: validate at the top of `make_scale_heightmap` (`if rows < 1: raise ValueError`) and/or add `if a.rows < 1: ap.error(...)` in `main`.

**[MEDIUM] Negative `--sharpness` produces inf/NaN weights and a misleading error** - `line 87`
- What: `w = np.abs(normals) ** sharpness`. Normal components are frequently exactly `0.0`, and `0.0 ** -k` is `inf`; then `inf / inf` at line 88 yields NaN weights → NaN heights → NaN displacement. It is *eventually* caught by the finite check at line 123, but the raised message ("degenerate input?") points at the mesh, not the parameter.
- Trigger: `--sharpness -1`.
- Impact: confusing failure; a user debugging their mesh when the real fault is the CLI flag.
- Fix: validate `sharpness > 0` and finite alongside `tile_mm`/`max_edge_mm` in `apply_skin` (lines 100–103).

**[MEDIUM] `--amplitude-mm` never validated; NaN/inf only caught indirectly** - `lines 122–123`
- What: unlike `tile_mm` and `max_edge_mm`, `amplitude_mm` has no explicit check. `NaN` amplitude is caught by the generic check at line 123, but the error message again misattributes the cause; `inf` behaves the same.
- Trigger: `--amplitude-mm nan` (argparse `float` accepts `nan`/`inf`).
- Impact: late, misattributed failure instead of a clear parameter error.
- Fix: add `if not np.isfinite(amplitude_mm): raise ValueError(...)` next to the other guards. (Decide explicitly whether negative amplitude is legal and document it.)

**[LOW] Demo mode silently ignores `--tile-mm` and `--sharpness`** - `line 157`
- What: the demo path hardcodes `tile_mm=5.0` and omits `sharpness` entirely, while the flags are still accepted.
- Trigger: `--demo out --tile-mm 20`.
- Impact: user experiments produce results that don't reflect the flags they passed — silent wrong output.
- Fix: pass `tile_mm=a.tile_mm, sharpness=a.sharpness` in the demo call.

**[LOW] Tile built before argument completeness check; error ordering masks usage errors** - `lines 150 vs 164`
- What: `load_heightmap` / pattern construction runs before the `input`/`output` required-args check. A bad `--heightmap` path (or `--rows 0`) raises before the user is told their invocation is missing required arguments.
- Fix: move the `if not a.input or not a.output: ap.error(...)` check (and the demo branch) before line 150.

**[LOW] `trimesh.load(..., force="mesh")` result used without checking for None/failure** - `line 166`
- What: for an unreadable or empty file, `trimesh.load` can return `None` (or raise its own opaque error); `mesh.vertices` at line 167 then fails with `AttributeError: 'NoneType'`.
- Trigger: corrupt/empty STL passed as `input`.
- Impact: unhandled traceback instead of a clean "could not load mesh" message.
- Fix: wrap in try/except and check `mesh is None or len(mesh.vertices) == 0` before proceeding.

**[LOW] `np.load` without explicit `allow_pickle=False`** - `line 60`
- What: current NumPy defaults to `allow_pickle=False`, so this is safe today, but the safety depends on the installed NumPy version; on very old versions a crafted `.npy` is a pickle-deserialization (code-execution) vector.
- Fix: pass `allow_pickle=False` explicitly to make the guarantee version-independent.

## Missing safeguards
- No validation of `--rows`, `--sharpness`, `--amplitude-mm` at the CLI layer (all other params are validated — the gap is conspicuous).
- No test covering the degenerate inputs the code itself warns about: `rows=0`, NaN CLI floats, empty/corrupt mesh, constant (flat) tile.
- Subdivision budget (line 110) is an area-based heuristic; there is no post-subdivision guard on actual vertex/face count or memory before displacement, so small-featured meshes can still explode past `MAX_FACE_BUDGET`.
- `main` has no top-level error handling: `export()` failures (unwritable path, existing file at `out` in demo mode → `FileExistsError` from `mkdir`) surface as raw tracebacks for a user-facing CLI.