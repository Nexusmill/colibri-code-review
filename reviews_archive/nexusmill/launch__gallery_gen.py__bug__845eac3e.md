# BUG review: launch\gallery_gen.py

- source: `C:\Users\User\source\repos\Nexusmill\launch\gallery_gen.py`
- model: moonshotai/kimi-k3
- reviewed: 2026-07-20 00:58
- tokens: in 5778 / out 1753
- est cost: $0.0436

---

## Verdict
Mostly safe to run in its controlled environment (hardcoded paths, no untrusted input), but it has one real rendering defect: `fit_cover` truncates instead of rounding, which can silently paste a 1px black edge into every "beauty shot". The biggest risk is silent visual corruption in the marketing assets it produces.

## Bugs & vulnerabilities

**[MEDIUM] `fit_cover` truncates resized dimensions → crop overflows → black edge column/row** - `line 49`
- What: `int(iw*s)` / `int(ih*s)` truncates toward zero. If `iw*s = 1600.97`, the resized width is `1600`, but if it's `1599.97` the width becomes `1599` while the crop box on line 51 still asks for `l+tw` (=1600), exceeding the image. PIL's `crop` silently pads out-of-bounds regions with black.
- Trigger: any source aspect ratio where `iw*s` or `ih*s` falls just below an integer (common with arbitrary render sizes).
- Impact: every gallery/hero image can get an unrequested 1px black strip on the right or bottom edge — silent corruption in shipped assets.
- Fix: `im.resize((math.ceil(iw*s), math.ceil(ih*s)), Image.LANCZOS)`.

**[MEDIUM] Chip wrap logic overlaps chips instead of moving to a new row** - `lines 221-223`
- What: after drawing a chip, `if fx>700: fx=74` resets the x cursor but never advances `y` (still 440). The next chip is drawn back at x=74, y=440, overlapping chips already drawn there. Also, the reset happens *after* the overflowing chip is already drawn, so a chip extending past x=700 is never prevented.
- Trigger: `"Raised","Engraved","Gradient depth","Adjustable mm"` — by the 3rd/4th chip, cumulative width exceeds 700.
- Impact: overlapping/garbled chip row in `05_relief.png`.
- Fix: check before drawing (`if fx + chip_w > 700: fx=74; y += 56`) and increment the row y, not just x.

**[LOW] Gallery 05 right-side image can paste at negative x / off-canvas** - `lines 214-215`
- What: `gp` is scaled to height 720 with no width cap; if `gp.width` after scaling exceeds `W-90-40`, `W-gp.width-90` goes negative and PIL silently clips the paste. There's no assertion the text block (ending ~x=600) doesn't overlap the image either.
- Trigger: a `PatternSkin_grip_demo.png` with aspect ratio wider than ~1.9:1.
- Impact: silently cropped product shot.
- Fix: cap width: `gp.thumbnail((W-90-640, 720), Image.LANCZOS)` or assert `gp.width <= 1470`.

**[LOW] File handles leaked in verification loop and for `mark`** - `lines 135, 249`
- What: `Image.open(...)` at line 249 is never closed (called per file in the loop); `mark` at line 135 keeps its `fp` open for the script's lifetime since only `.convert()` (which doesn't close the source) is used.
- Trigger: always.
- Impact: leaked FDs until process exit — harmless here, but bad pattern; on Windows, open handles can also block later overwrite/cleanup.
- Fix: use `with Image.open(...) as im:` and copy/convert inside the block.

**[LOW] `spaced` computes wrong origin for empty text when right-anchored** - `line 35`
- What: `tot = sum(...) - ls` yields `-ls` for empty `text`, shifting x by `+ls` and returning an inconsistent cursor.
- Trigger: `spaced(d, xy, "", font, fill)` with `anchor_left=False`.
- Impact: minor mispositioning; currently never called with empty text.
- Fix: early-return `x` when `not text`.

## Missing safeguards
- No existence/type validation of the five input PNGs (lines 131-135); a missing or truncated render crashes mid-run after earlier outputs were already written, leaving a half-generated gallery. Wrap opens in a preflight check that fails fast *before* any writes.
- No font fallback: `F()` hard-fails if DejaVu fonts aren't at the hardcoded path (line 12-13); check `os.path.isfile(FD+name)` once and raise a clear error.
- `fit_cover` divides by `iw`/`ih` with no guard against zero-size or 1px source images (line 48).
- No output verification: the script prints sizes but never asserts all expected files (featured_hero, 01-06) exist and are 1600x800; add a final assertion block.
- `caption_bar` (lines 53-64) assumes the passed image is exactly `W x H`; it pastes the band at fixed global coordinates. Assert `img.size == (W, H)` or derive from `img.size`.
- No atomic writes: a crash mid-`save` leaves corrupt PNGs that a later step may pick up; save to temp file then `os.replace`.
- No tests at all for the pure helpers (`fit_cover` sizing invariant `resized >= target`, `chip` cursor monotonicity, `knurl_h` range) — these are cheap to test and would catch the truncation bug.