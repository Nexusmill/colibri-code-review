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

---

# FULL re-audit 2026-09-10 (appended - the record above predates the adversarial gate and is kept as history, not as baseline)

# Colibri Review - bug (FULL re-audit) - asset-forge/forge/generators/patterns.py

- **Source path:** `asset-forge/forge/generators/patterns.py` (twin `asset-forge-user/forge/generators/patterns.py` byte-identical)
- **Reviewer:** claude-fable-5-1 fork (in-session), Colibri G37 protocol, campaign item 1 (AF units), rank 23
- **sha256 reviewed:** `38d7fa870278fce291648b1653f0bba34707840b963291a62eba1d0467a5b84f` (sha8 `38d7fa87` - identical to the 2026-07-22 record, which is kept as history, not baseline)
- **Date:** 2026-09-10 · **Mode:** bug, FULL read of the current bytes (owner ruling: pre-gate audits untrusted)
- **Context pack:** jCodemunch outline + importers (registry.py is the only consumer via HIERARCHY[...]["fn"]; pipeline.generate_set and app.py:770 call registry.render with an int seed and a palette NAME filtered against PALETTE_NAMES); base.py DualCanvas contract read in the same pass; the 2026-07-22 adjudication record (five DeepSeek claims refuted, tileability measured) loaded as claims; no remediation or deferred rows name the file.

## Verdict
Clean. Every family is a pure function of (seed, palette, density); the canvas layer draws each primitive at nine toroidal offsets so the tiles wrap by construction (re-verified in base.py, not assumed from the July record); every palette index is bounded (all ten builtin palettes have five colours and `pick_palette` never returns anything else); densities default to 1.0 on an unknown word; `np.linspace(..., leaves)` accepts the numpy integer `rng.integers` returns.

## Bugs & vulnerabilities
None confirmed.

## Missing safeguards
- Reproducibility across numpy releases is a policy, not a guarantee: `np.random.default_rng` Generator method streams may change between numpy versions (NEP 19), so a seed reproduces a tile only on the same pinned numpy - true today because the shipped build is pinned (G17), but a numpy bump changes every historic seed's tile. Worth a note in the recipe doctrine, not a code change.
- `pick_palette(rng, name)` draws from the rng only when the name is unknown, so the same seed yields a different layout depending on whether a palette name was given - deliberate (callers always pass a validated name or None).

## Adversarial verification pass (refuted claims)
- "A non-numeric seed crashes `_rng`" - every caller passes an int (app.py:770 parses it at the route, pipeline.generate_set validates `int(base_seed)`).
- "The `%` / `1 + integers(0, len-1)` indexing breaks on a short palette" - `pick_palette` only returns builtin palettes and all ten have exactly five entries.
- "Bands in `waves` leave a background strip at the top" - the first band's polygon starts at y = base + amp*sin(...) which can exceed 0, but the band at b = 0 is preceded by the wrap copy of band `bands` drawn at dy = -SIZE; the canvas wrap closes the strip (the July record measured it).
- "`density` strings other than the three crash" - `.get(density, 1.0)`.
