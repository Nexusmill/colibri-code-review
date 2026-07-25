# colibri-review — PatternSkin/heightmap.py — bug (hunt round 1, effort=high/security)

- **Source:** PatternSkin/heightmap.py · **Scanner:** general-purpose subagent @ claude-opus (deep,
  untrusted-image lens) · **Verification + fix:** claude-opus-4-8[1m] (in-session, Phase 3) · cost $0.00
- **sha256 reviewed:** 01dab69cafa748563a249b237c8385b4e2dc8eba1bced72b8ca61ba2556ee24f
- **Date:** 2026-07-23 · **Mode:** bug · round 1 of the top-20 hunt (deep security pass)
- **Context pack:** no prior review / refuted ledger / remediation rows for this file; callers in
  `__init__.py` (apply/batch/lithophane/region via `load_heightmap`); prior in-code fixes PSK-11
  (temp-leak) and PSK-13 tranche 2 (extraction). `search_text` confirmed **no dimension cap exists
  anywhere in PatternSkin/*.py**. Current bytes re-hashed at dispatch (G36).

## Verdict
The SVG path is well hardened (external-ref/XXE filter, 1024² raster cap), but the untrusted-image
threat model had two real memory-exhaustion vectors — an uncapped raster path and a size guard that
ran *after* slurping the whole file — plus a temp-leak and a scan/render TOCTOU. All four fixed.

## Bugs & vulnerabilities (all CONFIRMED, all fixed)

**[MEDIUM] No decompression-bomb / dimension cap on raster images** - `heightmap.py:109-115`
- What: `_load_heightmap_uncached` loaded any PNG/JPG via `bpy.data.images.load` and did
  `np.array(img.pixels[:]).reshape(h,w,4)` guarded only by `w==0 or h==0`. `img.pixels[:]`
  materializes the full float buffer (`h*w*4*4` bytes ≈ 6.4 GB for 400 MP) on top of Blender's copy.
- Trigger: a 20000×20000 (or crafted) image from any apply/batch/region job → Blender OOM/crash.
  The SVG branch caps to 1024² (proving the intent); the raster branch had none.
- Fix: `_MAX_MEGAPIXELS = 128` cap checked **before** `img.pixels[:]`, plus a `len == w*h*4`
  pixel-buffer guard (closes the ungraceful-`reshape` LOW at the same site).

**[MEDIUM] SVG 64 MB size guard ran *after* reading the whole file** - `_rasterize_svg:34-39`
- What: `_raw = _sf.read()` slurped the entire file unconditionally; the `len(_raw) > 64_000_000`
  check ran afterward — a no-op for the multi-GB `.svg` it exists to stop (OOM before the guard).
- Fix: bounded read `_sf.read(64_000_001)` — caps memory, the guard still fires, and the full-content
  regex safety scan still runs on everything actually accepted (≤ 64 MB).
- **Verified (mechanism, headless):** a 65 MB file → bounded read pulls 64,000,001 bytes (not the
  full 68 MB) and the guard fires; the old `read()` would have materialized all 68 MB.

**[LOW] Rasterized-SVG temp PNG leaked when `images.load` failed** - `_load_heightmap_uncached:109`
- What: `bpy.data.images.load(...)` sat *outside* the `try/finally` that removes `_tmp_png`, so a
  load failure skipped cleanup — the exact PSK-11 temp-accumulation class, missed on this path.
- Fix: `img = None` before the try, load moved inside, `finally` guards `if img is not None`.

**[LOW] TOCTOU between the safety scan and cairosvg's re-read** - `_rasterize_svg:59`
- What: the filter scanned bytes read at `open()`, but `cairosvg.svg2png(url=path, …)` re-read the
  file from disk — a file swapped in between bypasses the external-ref/XXE filter (mitigated by
  cairosvg's `unsafe=False` default, so defense-in-depth erosion, not a primary hole).
- Fix: `cairosvg.svg2png(bytestring=_raw, …)` renders the exact scanned bytes.

## Verify
`junk/_heightmap_probe.py` 9/9 PASS: module still imports (bpy=None), pure members unbroken, the
`_MAX_MEGAPIXELS` constant + guard arithmetic correct, and the F2 bounded-read mechanism proven
against a real 65 MB file (reads 64 MB, not 68). F1/F3/F4 touch the `bpy`-dependent load path and are
verified by inspection + `py_compile` only — **not exercised in a live Blender session** (no headless
image-load path). All fixes via `_safe_edit` (G8).

## Refuted during verification (deep scan self-refuted; recorded in `_refuted_ledger.json`)
- SVG XXE via `<!DOCTYPE>/<!ENTITY>` — line 51 rejects both on the NUL-screened lowercased full text;
  cairosvg defaults `unsafe=False`. Sound.
- SVG external `href`/`url()` fetch (SSRF / local-file disclosure) — lines 43-50 blacklist every ref
  not `#`/`data:` on lowercased full content; scheme-less local paths correctly rejected.
- Div-by-zero in normalization — `np.ptp(a)+1e-9` and the `white>black` guard prevent it.
- `make_seamless` index error on tiny tiles — `mx/my = max(1,…)` keeps loops valid; callers pass
  non-empty maps.
- `_save_gray_png` image orphan on save failure — `try/finally` removes it (present).
- Path traversal on `path` — user-selected local file in a desktop add-on; no attacker-controlled
  remote path.
