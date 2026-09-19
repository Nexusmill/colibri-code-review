# Colibri Review - bug (FULL re-audit) - asset-forge/forge/seamless.py

- **Source path:** `asset-forge/forge/seamless.py` (twin `asset-forge-user/forge/seamless.py` byte-identical - fix applies to both)
- **Reviewer:** claude-fable-5-1 fork (in-session), Colibri G37 protocol, campaign item 1 (AF units), rank 29
- **sha256 reviewed:** `b8fe26178d13ba15f69fde1aac74b567135900bf7a0e6fe8e1890f44dbe87b48` (sha8 `b8fe2617`) - the PRE-fix bytes
- **Date:** 2026-09-10 · **Mode:** bug, FULL read of the current bytes (owner ruling: pre-gate audits untrusted)
- **Context pack:** jCodemunch importers (library_gen.py imports SEAMLESS_SUFFIX and calls make_seamless at 1094 for non-emblem output only - AF-LIB-SEAM; bundle.py:23/138/219 appends the suffix and blends the raw PNG whenever its `seamless` arg is true; lib_seam_fur + run_assetforge probes); call sites traced to their source: the Studio's startBundle body (index.html:726-738) sends NO `seamless` key, app.py:1127 defaults `seamless=bool(params.get("seamless", True))`, app.py:1194 normalizes `params["output"]` through output_opts.normalize whose DEFAULTS carry `seamless: False` for emblem and `True` for heightmap (output_opts.py:50-55); the user build's tracer `embed_png` is a plain copy; the deferred row LIB-SEAM-FUR and feature rows AF-LIB-SEAM / AF-SEAM-FUR / AF-BUNDLE-ALPHA loaded as claims.

## Verdict
Shippable after ONE fix. The blend itself is sound (strictly reduces the wrap discontinuity, feather bounded, never raises without numpy/PIL) - but it destroys the alpha channel of any transparent PNG it touches, and the Studio's bundle path touches every image.

## Bugs & vulnerabilities

**[HIGH] `make_seamless` flattens a transparent PNG to opaque - every native-transparency Studio bundle was delivered without its transparency** - `line 43` (`Image.open(path).convert("RGB")`) and `line 57` (`Image.fromarray(...)` with no mode)
- What: the image is read as RGB and the blended RGB is written back over the file; a PNG with an alpha channel loses it entirely (mode RGBA -> RGB, every transparent pixel becomes the model's backdrop colour).
- Trigger (traced end to end): the Studio never sends `seamless` -> app.py builds the bundle with `seamless=True` (its default, ignoring the normalized output opts that say emblem -> `seamless: False`) -> bundle.py `_generate_once` calls `make_seamless(raw)` on the provider's raw PNG before the tracer copy. A native-transparency emblem (AF-BUNDLE-ALPHA: the knob injected server-side, the run PAID for) therefore arrives opaque. Reproduced: `SEAM_bundle_item_keeps_alpha` builds a one-item emblem bundle through `build_bundle` with a fake provider that writes an RGBA disc - the delivered file is mode RGB with 0 transparent pixels.
- Impact: the product's one transparency promise, quietly broken on the bundle path since AF-BUNDLE-ALPHA shipped (2026-08-25); the buyer pays for a transparent emblem and gets a backdrop. (The emblem prompts also carry the tiling suffix - "seamless tileable repeating pattern ... designed to tile" - on the same default, so emblem bundles ask for a pattern, not an emblem.)
- Fix (this unit, applied to a scratch copy and proven GREEN): keep the image's own mode - read as RGBA when the source carries alpha (RGBA/LA, or P with transparency), blend all channels, write back in that mode; opaque sources are unchanged (still RGB, still blend - `SEAM_opaque_still_blends`, `lib_seam_fur` 6/6 on the copy). Snippet in `fix_snippets_af7.json`.
- Cross-file (the caller gate, app.py - for the lead): the honest default is the normalized output opts' own `seamless` flag, so emblems are neither suffixed nor blended (AF-LIB-SEAM parity with the library path):
  ```
  OLD  asset-forge/app.py (+ user twin), _run_bundle:
                                   seamless=bool(params.get("seamless", True)),
  NEW
                                   # Full re-audit 2026-09-10: the Studio never sends `seamless`; the normalized
                                   # output opts already carry it (output_opts DEFAULTS: heightmap ON, emblem OFF).
                                   # The old default True tiling-suffixed AND edge-blended every emblem - and the
                                   # blend flattened native transparency (seamless.py, SEAM-ALPHA).
                                   seamless=bool(params.get("seamless",
                                                 (params.get("output") or {}).get("seamless", True))),
  ```
  `params["output"]` is normalized at bundle_start (app.py:1194) before the worker runs, and `normalize()` returns the DEFAULTS merged (output_opts.py:94-103), so the key is always present.
- Verification: CONFIRMED (bytes + the reproducer; RED on the repo, GREEN on the patched copy).

## Missing safeguards
- `make_seamless` writes the blended image over the source in place with a non-atomic `save(path)`; a crash mid-write truncates a paid image (the tracer copy happens after). Temp + `os.replace` would close it.
- `tile_score` and the pre-fix `make_seamless` opened the file without a context manager (fd held until GC); the fix uses `with`.
- No caller passes emblem-class output through `tile_score`; fine, noted.

## Adversarial verification pass (refuted claims)
- "The blend can increase the seam" - it pulls both edges to their shared mean with a monotone ramp; the edge rows become equal, the interior is untouched (probe: score drops >5x).
- "A tiny image breaks the slicing" - `fw = max(2, int(w*feather))`; for w >= 4 the two bands do not cross the centre destructively, and no caller produces images under 256 px.
- "16-bit PNGs are mangled" - `convert("RGB")`/`("RGBA")` quantises to 8-bit; provider output is 8-bit PNG.
- "`feather=0.012` for fur types (AF-SEAM-FUR) still smears" - out of this review's mode; the A/B ruling stands, the fix keeps the parameter path intact (lib_seam_fur SF3/SF4 green on the copy).

## Remediation postscript
Applied by the lead if accepted; rows suggested: AF-SEAM-ALPHA (this unit, HIGH) and AF-BUNDLE-SEAM-DEFAULT (app.py, the caller gate).

## Remediation postscript (same session)
The fixes were applied after this review hashed the bytes above; the file is now `9cc8e0d9904987a2449abdd6a835f3d86b016473a6bf4d94c1223c377d349fb1`. Rows AF-SEAM-ALPHA in `docs/remediation_manifest.json`, same commit.

