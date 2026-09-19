# Colibri Review - bug (FULL re-audit) - PatternSkin/heightmap.py

- **Source path:** `PatternSkin/heightmap.py`
- **Reviewer:** claude-fable-5-1 (in-session fork), Colibri G37 protocol, campaign item 1 (product cores), rank 11
- **sha256 reviewed:** `9b08c502e3d1d0773755789d9346783a2e902446878641924d15e4f9d1809497` (sha8 `9b08c502`) - the PRE-fix bytes
- **Date:** 2026-09-10 · **Mode:** bug, FULL review of the current bytes (owner ruling 2026-09-10: the file's prior audits - 07-29 K3, 08-14 GROK-HM, 08-15 residuals, 08-26 GLM-R2, this morning's delta - predate or lean on pre-gate records and are CLAIMS here, not a baseline)
- **Context pack:** all 302 lines read; importers (only `__init__.py:80`, which pulls `_rasterize_svg`, `_HM_CACHE`, `load_heightmap`, `tiling_score`, `make_seamless`, `_save_gray_png`); remediation rows PS-SVG-ESCAPE-SCOPE + the GROK-HM/HM-PS-NORM/PS-HM-PCT dockets; feature rows PS-GLM-R2, PS-PRESET-LOAD, PS-QOL-API-APPLY; the cairosvg 2.9.0 `image()` handler Blender actually loads (`%APPDATA%\Blender Foundation\Blender\5.1\scripts\modules\cairosvg\surface\image.py`) read for the nested-data: claim; Blender 5.1.2 headless for the colour-management claim.

## Verdict
One CONFIRMED correctness defect (a 16-bit source bakes a different relief than the same picture in 8-bit); the SVG security belt holds at the bytes - every bypass class I could construct dies at `_svg_url_fetcher`, and cairosvg's own content sniffing does not weaken it.

## Bugs & vulnerabilities

**[MEDIUM] 16-bit height maps are read LINEARISED while 8-bit ones are read RAW - the same picture yields two different reliefs** - `_load_heightmap_uncached`, `line 182` (`bpy.data.images.load`) .. `line 202` (`foreach_get`)
- What: Blender keeps a 16-bit PNG/TIFF as a FLOAT buffer and, on load, converts it from the file's colour space (sRGB) to scene linear; `Image.pixels` then returns those linear floats. An 8-bit file stays a byte buffer and `pixels` returns the raw encoded bytes / 255. The loader treats both as "luminance in [0,1]".
- Trigger: any 16-bit source - the default height-map export depth of Substance, Photoshop, GIMP and most displacement tools; `.tif` 16-bit likewise.
- Impact: measured headless in Blender 5.1.2 with a uniform mid grey (128/255 in 8-bit, 32896/65535 in 16-bit - the identical value): 8-bit reads 0.5020, 16-bit reads 0.2159. Midtones collapse (the sRGB decode), so a 16-bit height map displaces with the wrong curve - the percentile stretch re-spans the range but cannot undo the curve. Users get a different relief from the "better" file and nothing tells them why.
- Fix: a height map is data, not colour - mark the loaded image `Non-Color` before reading its pixels (`img.colorspace_settings.name = "Non-Color"`, in a try so a build without the name keeps today's read). Verified in the same probe: the 16-bit file then reads 0.5020, identical to the 8-bit one; 8-bit/JPEG/WebP byte sources are unaffected (their raw read never went through colour management), EXR/float-linear sources are unaffected (linear -> linear was already a no-op). Probe `reaudit/probe_ps_heightmap_1.py` (bpy): `HM_16bit_png_matches_8bit` RED on the current bytes, `HM_noncolor_reads_raw_16bit` GREEN (the mechanism of the fix).
- Verification: CONFIRMED (reproduced headless; the fix mechanism reproduced in the same run).

## Missing safeguards (not fixed)
- `_svg_url_fetcher` trusts the data: URI's declared MIME, but cairosvg's `image()` SNIFFS the payload (`b'<svg' in image_bytes`) and renders a nested SVG tree regardless of `image/png` - so the "refuse nested SVG" rule is bypassable by lying about the type. Not a defect in effect: the nested tree is built with the same `url_fetcher` and `unsafe=False`, so its external refs and entities still die at the fetcher; recorded so nobody claims the MIME rule is a barrier.
- The `_MAX_MEGAPIXELS` guard runs after `img.size`, which already decoded the full byte raster (w*h*4 bytes, ~0.5 GB at the 128 MP cap) - it protects the 4x float materialisation, not the decode.
- `<use>`/`<pattern>` amplification in an SVG is CPU-only (cairosvg renders at a fixed 1024 px), local file, user-chosen: not worth a guard.

## Adversarial verification pass
- CSS `url(` hidden with a numeric entity (`&#117;rl(`) in a style attribute: passes the text scan, decoded by the XML parser, reaches cairosvg -> `_svg_url_fetcher` refuses the non-data: URL. Belt holds - refuted as a bypass.
- `<?xml-stylesheet href="data:text/css;base64,...">` with a base64-hidden `@import`: the href scan allows data:, the CSS scan cannot see inside base64, but the fetcher refuses a `text/css` MIME and cairosvg only reads `file:` stylesheets by path anyway - refuted.
- Nested data: SVG with a lying MIME (above): renders, but with the same fetcher and `unsafe=False` - no fetch, no entity; refuted as a security finding, kept as a note.
- `.svgz` sources: neither branch handles gzip; Blender's loader reports "Couldn't read image" - honest failure, not a defect.
- `make_seamless` on a 1-px strip, `tiling_score` on H or W of 1, the LRU copy-out, the mtime_ns cache key: all traced clean.

## Remediation postscript (same session)
The fixes were applied after this review hashed the bytes above; the file is now `6e09372833c3576a048037e56327e548a858bd1f0417e5f129123f8247348cb8`. Rows PS-HM-16BIT-LINEARISED in `docs/remediation_manifest.json`, same commit.

