# Colibri Review - bug (DELTA) - PatternSkin/heightmap.py

- **Source path:** `PatternSkin/heightmap.py`
- **Reviewer:** claude-fable-5-1 (in-session), Colibri G37 protocol, campaign item 1 (product cores), rank 11
- **sha256 reviewed:** `e97d0e663e80504fd30dac96bab9815d03e2fb906409ac7815a09f1a47fa9d2b` (sha8 `e97d0e66`) - the PRE-fix bytes
- **Date:** 2026-09-10 · **Mode:** bug, stale-file DELTA against `01dab69c` (2026-08-15 grok-hm-residuals)
- **Delta reviewed:** 5 commits / 237 diff lines: a43e39a4 (bomb/OOM guards), 4250c106 (HM-PS-NORM percentile stretch), 8df29eca (GROK-HM 1/2/3 render-boundary `_svg_url_fetcher`, encoding-declaration reject, @import + CSS-escape rejects, `PNGSurface.convert(unsafe=False)`), e4571ba4 (alpha-on-white luma, mtime_ns key, seamless clamp, image datablock leak), 83d109f8 (GLM-R2 NEP-50 float pin) - every hunk read.
- **Context pack:** the prior review record(s) for the file, `docs/remediation_manifest.json` rows from 2026-07-24 on, `docs/deferred_manifest.json` rows naming the file, `_hunt_plan.json` + `_refuted_ledger.json` loaded; jCodemunch `get_symbol_source` on the call sites each finding depended on.

## Fixed since last review
- Every remediation row dated after the base review was verified present at the bytes (they are the delta).

## Verdict
Shippable after the one fix below (applied this session, RED-first). The security belt is sound - the render-boundary fetcher refuses everything but inline raster data URIs, and the text scan sits in front of it - but one of the belt's text rules over-reached into ordinary files.

## Bugs & vulnerabilities

**[MEDIUM] The CSS-escape guard refused every Inkscape SVG saved on Windows** - `_rasterize_svg`, the `\\[0-9a-f]` scan (GROK-HM #1, 2026-08-14)
- What: the guard searched the WHOLE lowercased file for a backslash followed by a hex digit. Inkscape writes the last export path into the root element (`inkscape:export-filename="C:\\Users\\...\\Desktop\\x.png"`); `\\Desktop` lowercases to `\\d`, a hex digit, so the file was refused with "SVG contains CSS escape sequences - export it to PNG instead."
- Trigger: any SVG whose text carries a Windows path with a backslash before one of 0-9/a-f outside CSS - Inkscape export metadata is the common case; `sodipodi:absref` is another.
- Impact: a legitimate texture SVG cannot be loaded as a pattern; the message sends the user to a PNG export instead of naming the real cause.
- Fix (applied): the escape scan runs only over CSS - the joined text of `<style>` blocks and `style="..."` attribute values - which is the only place a CSS ident-escape can hide `url(`; the render-boundary fetcher stays the hard stop. Battery `tests/harness/probes/sweep_heightmap_r3_bpy.py`: an Inkscape-style SVG with a Windows export path must render (watched RED: refused), while a `style="fill:\\75rl(#p)"` attribute and a `<style>` block carrying the same escape must still be refused; GREEN after. Regressions: `grok_hm_svg_filter.py` (Blender's python) and `grok_hm_residuals_bpy.py` unchanged.
- Verification: CONFIRMED (reproduced headless in Blender 5.1.2 with cairosvg present).

## Remediation postscript (same session)
The fix was applied after this review hashed the bytes above; the file is now `9b08c502e3d1d0773755789d9346783a2e902446878641924d15e4f9d1809497`. Row PS-SVG-ESCAPE-SCOPE in `docs/remediation_manifest.json`, same commit.
