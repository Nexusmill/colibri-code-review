# Colibri Review - bug (FULL re-audit) - asset-forge/forge/generators/base.py

- **Source path:** `asset-forge/forge/generators/base.py` (twin byte-identical)
- **Reviewer:** claude-fable-5-1 fork (in-session), Colibri G37 protocol, campaign item 1 (AF units), rank 25
- **sha256 reviewed:** `05042d73f88e749fabf6d4c21e299756a25930862a9fb6a5bf2a024f94a2353c` (sha8 `05042d73`)
- **Date:** 2026-09-10 · **Mode:** bug, FULL read (owner ruling: pre-gate audits untrusted)
- **Context pack:** importers patterns.py (DualCanvas, pick_palette, rot_rect) and registry.py (PALETTE_NAMES; `render` filters the palette NAME against it, so no raw colour string from a client ever reaches a primitive); pipeline.py:84-93 writes `to_png` / `to_svg`; the two remediation rows on this file ("validate colour at the choke point", "background() validated before _bg is set") loaded as claims and both verified present at lines 38-42 / 59-61.

## Verdict
Clean. Every colour goes through `hex_to_rgb` (6-hex fullmatch, so no SVG attribute injection and no short/named/8-digit forms), the background is validated before `_bg` is stored, every primitive emits its nine toroidal copies to both the raster and the tile-clipped SVG body, and the SVG numerics are formatted with fixed precision.

## Bugs & vulnerabilities
None confirmed.

## Missing safeguards
- The SVG emits the caller's ORIGINAL fill string (`fill="{fill}"`); a hash-less `rrggbb` passes `hex_to_rgb` (it strips `#`) and would render correctly in the PNG but be an invalid paint value in the SVG. No caller passes a hash-less colour (all ten palettes carry `#`; clients choose names, not colours) - normalising to `#` + lower at emission would make the guarantee structural.
- `hex_to_rgb` on a non-string raises AttributeError, not ValueError; unreachable from the routes.

## Adversarial verification pass (refuted claims)
- "A client-supplied colour injects into the SVG" - clients select palette NAMES (registry filters against PALETTE_NAMES); colours come from the module's own table and are regex-validated anyway.
- "`background()` can leave a bad `_bg` for `to_svg`" - `hex_to_rgb` runs first (line 60), `_bg` is assigned only after it returns.
- "Negative radius crashes PIL ellipse" - every caller derives r from positive uniforms times a positive step.
- "Alpha fills are ignored on the raster" - `ImageDraw.Draw(img, "RGBA")` blends RGBA fills.
