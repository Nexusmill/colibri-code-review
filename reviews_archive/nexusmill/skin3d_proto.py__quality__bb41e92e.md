# QUALITY review: skin3d_proto.py

- source: `C:\Users\User\source\repos\Nexusmill\skin3d_proto.py`
- model: moonshotai/kimi-k3
- reviewed: 2026-07-19 19:42
- tokens: in 1628 / out 1303
- est cost: $0.0244

---

## Health score
**7/10** — Compact, readable prototype with clean math; main gaps are unexplained magic numbers, a weak public API (in-place densification hidden inside `apply_skin`), and hardcoded paths/output logic mixed into the library code.

## Improvements

**[HIGH] Extract and name the magic constants in `make_scale_heightmap`** - `lines 9–19`
- Issue: `0.72`, `0.62`, `0.95`, `0.12` and the halo ranges `(-1, …+2)` / `(-2, rows+2)` have no names or rationale. Tuning the pattern requires reverse-engineering the geometry.
- Better: promote them to named module constants or keyword args with a docstring:

```python
# Aspect ratio and per-axis falloff of each scale dome (empirical, tuned for seamlessness)
SCALE_ASPECT_Y = 0.72
DOME_FALLOFF_X = 0.62
DOME_FALLOFF_Y = 0.95
ALT_ROW_DARKEN = 0.12
```

**[HIGH] Separate the CLI/demo from the library** - `lines 50–62`
- Issue: `__main__` block hardcodes a session-specific absolute path (`/sessions/friendly-.../mnt/outputs/...`), which breaks for any other user and couples the module to this machine. The demo is also untestable as-is.
- Better: move it to an `example.py` or accept paths via `argparse`/`pathlib`:

```python
if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    ...
    skinned.export(out / "torus_scaled.stl")
```

**[MEDIUM] Document `apply_skin`'s contract and non-obvious behavior** - `line 41`
- Issue: The function silently re-meshes (potentially exploding vertex count), returns a *new* mesh, and drops any face attributes/colors. `max_edge=0.7` is in mm but doesn't say so. Callers can't discover this without reading the body.
- Better: add a docstring stating units, that the input mesh is not mutated, that attributes are lost, and the performance implications of `max_edge`. Rename `max_edge` → `max_edge_mm` for consistency with `tile_mm`/`amplitude_mm`.

**[MEDIUM] Clarify the seam-hiding wrap loop** - `lines 16–19`
- Issue: The `for dx in (-1.0, 0.0, 1.0)` wrap plus the negative/overflow loop ranges implement periodic boundary conditions, but the strategy (overdraw + wrap) is only hinted at by one comment. The `halo` of 2 is also unexplained.
- Better: a short comment block explaining "draw each scale at 3 x-offsets so the tile wraps; extend row ranges by a halo so edge scales are complete," or extract `_iter_scale_centers(rows, sx, sy)` as a generator to make the triple loop read as iteration rather than logic.

**[MEDIUM] Repeated `1e-9` epsilon and normalization** - `lines 20, 38`
- Issue: Two separate ad-hoc epsilon guards with no shared name; the intent ("avoid divide-by-zero on degenerate input") is implicit.
- Better: `EPS = 1e-9` module constant, and consider a tiny `_normalize01(a)` helper so line 20 reads `return _normalize01(h)`.

**[LOW] Naming consistency and one-statement-per-line** - `lines 3, 25–28`
- Issue: `import numpy as np, trimesh` violates PEP 8; `_sample` packs three statements per line with semicolons, which fights diffs and debugging. `_sample` could also be named `_bilinear_sample_wrap` — its wrap behavior is its key feature.
- Better: split imports; one statement per line.

**[LOW] `sy = sx * 0.72` mixes counts and spacings** - `lines 9–10`
- Issue: `rows` is a count, `sx`/`sy` are spacings, and the row loop upper bound `int(1/sy) + 2` recomputes a count from a spacing. Readable only after careful study.
- Better: compute `n_rows = int(np.ceil(1.0 / sy))` once and loop `range(-1, n_rows + 2)` with a comment.

## Quick wins
- [ ] Split the combined import on line 3.
- [ ] Add `EPS = 1e-9` constant; use at lines 20 and 38.
- [ ] Rename `_sample` → `_bilinear_wrap_sample` and add a one-line docstring.
- [ ] Split semicolon-chained statements on lines 25–28.
- [ ] Add a return-type docstring to `apply_skin` (units, new mesh, attributes dropped).
- [ ] Use `pathlib.Path` and a parameter instead of the hardcoded `/sessions/...` path.
- [ ] Print mesh stats via a small `_describe(mesh)` helper to DRY lines 55–58.
- [ ] Add a smoke test: `apply_skin` on a unit cube preserves face count topology and stays watertight — the pure functions (`make_scale_heightmap`, `_sample`, `triplanar_height`) are already easily testable since they take arrays, not meshes.

## What's done well
- **Pure, testable core**: the math (`_sample`, `triplanar_height`, `make_scale_heightmap`) operates on numpy arrays with no side effects or global state — trivially unit-testable.
- **Good scoping**: `_sample` is correctly marked private; functions are short and single-purpose.
- **Concise, accurate comments**: the triplanar projection comments (`# along Y -> XZ`) and the wrap comment convey exactly the non-obvious intent without noise.