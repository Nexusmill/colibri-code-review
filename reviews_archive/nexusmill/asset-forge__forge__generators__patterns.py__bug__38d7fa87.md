<!-- source: asset-forge/forge/generators/patterns.py | reviewer: claude-fable-5 (colibri-review G37, verify-first over deepseek-v4-pro batch) | sha256 38d7fa870278 | 2026-07-22 | mode: bug | context pack: jcodemunch (callers app.py:426 int(seed) pre-render, pipeline.py:61 generate_set int seed; base.py::DualCanvas + pick_palette), marketing claims, prior GLM 2026-07-19 palette verdict, DESIGN doctrine (judge by eye) -->

## Verdict
NO code change. Every DeepSeek finding is refuted after verification — most importantly the headline
CRITICAL "families are not seamless," which is a VERIFIED FALSE POSITIVE: DeepSeek reviewed patterns.py
in isolation and never saw `DualCanvas` (base.py), whose EVERY primitive already emits all 9 toroidal
copies (`_wrap()`, dx/dy in {-SIZE,0,+SIZE}) to BOTH the PNG raster and the tile-clipped SVG body, so
the tiles wrap by construction. This is the exact blind-single-file failure mode the colibri protocol
exists to catch — and it nearly caught ME too (my first-pass junction-crop eyeballing misread plaid's
*bands* as a *seam*; the objective edge-continuity test corrected it).

## Adjudication

**[CRITICAL] "families are not tileable" — VERIFIED FALSE POSITIVE**
- Ground truth = edge-wrap continuity. Measured across all 8 families (junk, seed 777): the toroidal
  edge junction |col0-col_last| / |row0-row_last| is 0.00-0.58, versus the sharpest INTERIOR shape
  edge of 120-155 — i.e. the tile boundary is smoother than any interior contour. Roll test (shift the
  tile by SIZE/2 so the wrap seam lands at centre): plaid/terrazzo/waves/geometric show NO line at
  centre (junk/_u7_roll_*.png) — definitionally seamless. SOURCE confirms why: base.py DualCanvas.circle
  /ellipse/polygon/line/rect_rot each loop `for dx,dy in self._wrap()` drawing the element at all 9
  offsets, and to_svg wraps the body in a `clipPath` tile rect — so an element crossing any border
  reappears on the opposite side in both formats. DeepSeek's premise ("draw strictly inside [0,SIZE]
  with no wrapping") is false at the canvas layer it never read. `scales` isn't "the only seamless one";
  it merely ALSO over-draws its lattice, redundant with the canvas wrap.

**[HIGH] non-numeric seed crash (line 20) — REFUTED (no such caller)**
- `_rng` int()s the seed; both real callers pass an int (app.py:426 `int(d["seed"])` at the route;
  pipeline.generate_set validates `int(base_seed)` then passes int). No caller forwards a raw string.

**[HIGH] <2-colour palette IndexError/ZeroDivisionError — REFUTED / verified-stale**
- `pick_palette` only ever returns a builtin PALETTE (unknown/empty name -> random builtin), and all 10
  builtins have exactly 5 colours. `pal[1+integers(0,len-1)]` / `%(len-1)` are always safe. Same finding
  GLM raised 2026-07-19, adjudicated identically then; re-flag of closed reasoning.

**[MEDIUM] waves top-strip background gap (84-101) — REFUTED**
- Checked directly: 0 all-background rows on seeds 1/42/777/2026, top rows covered. The band drawn at
  b=bands (base=SIZE) is also emitted by `_wrap` at dy=-SIZE, covering y=0. The toroidal wrap fills any
  would-be top strip.

**[LOW] botanical axis-aligned leaves / plaid edge stripe — REFUTED as defects (cosmetic taste only)**
- Leaves: `ellipse` has no rotation param by design; leaf orientation is a stylistic choice, not a bug,
  and the sprig tiles fine. Plaid "missing edge stripe": the stripe at x=0 IS the period boundary and its
  wrapped copy covers x=SIZE; edge metric 0.00/0.00 = perfectly seamless. No gap exists.

## Missing safeguards
- "No seam test" is the one fair point: the wrap is correct but untested, which is how a blind reviewer
  (and nearly this one) could doubt it. A tiny junction-continuity assertion (edge-wrap << interior-max,
  the metric used here) in tests/ would lock the invariant and pre-empt this exact false positive next
  time. Logged as a NICE-TO-HAVE (not a defect); not landed this unit to keep the review a pure
  no-code-change adjudication. Determinism spot-checked (same seed -> byte-identical PNG).
