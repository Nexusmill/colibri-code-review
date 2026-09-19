# Colibri Review - bug (FULL re-audit) - asset-forge/forge/output_opts.py

- **Source path:** `asset-forge/forge/output_opts.py` (twin `asset-forge-user/forge/output_opts.py` byte-identical, G23)
- **Reviewer:** claude-fable-5-1 fork (in-session), Colibri G37 protocol, campaign item 1 (AF units), rank 43
- **sha256 reviewed:** `3a63a0b4873b4ce0b8d78641901fefa1dbc48d0236e81048b47fdfc023c28433` (sha8 `3a63a0b4`)
- **Date:** 2026-09-10 · **Mode:** bug, FULL review of the current bytes (owner ruling 2026-09-10: the 08-04 `3a63a0b4` fix record predates the adversarial gate and is untrusted - no delta against it)
- **Context pack:** jCodemunch outline (constants, defaults_for, normalize, prompt_fragment, wants_dual_render, alpha_from_dual, alpha_by_removal, vector_suitability, vectorize); callers scanned: library_gen.py (normalize/prompt_fragment at 329-330/419-420/571/817, wants_dual_render at 528/1143, the dual-pass block 1143-1224, the removal `elif` at 1227, vectorize at 1256), app.py (normalize at 1309/1383/1580, `_bundle_output_route` native-transparency routing); remediation rows GROK-OO (three findings); feature rows AF-OUTPUT-KNOBS and AF-ALPHA-HONESTY (contracts pressed); batteries grok_oo_output.py 14/14 and af_output_knobs.py 4/4 re-run on the current bytes with the buildenv's Pillow 12.3.0 / numpy 2.5.1.

## Verdict
Clean - 0 confirmed. The dual-pass solve refuses every non-pair class it claims to (backdrop corner prior, w<b physics, per-channel alpha disagreement by mean and by local fraction) before saving anything; `normalize` canonicalizes the mode token first and clamps transparent for anything heightmap-class; `vectorize` traces to a sibling temp, downscales past 2048 px, promotes only an unwarned SVG and always removes its temps; `prompt_fragment(key=...)` swaps exactly one word between the two frames.

## Bugs & vulnerabilities
None confirmed.

## Missing safeguards
- `normalize` canonicalizes the mode but not the `background` / `alpha_method` tokens: an unknown background reads as full-bleed in `prompt_fragment` while the job record keeps the junk value and no `_forced` note; a transparent background with an unknown `alpha_method` falls into library_gen's removal `elif` (a silent downgrade from the requested method). Only the JSON API can send such values - both UIs emit the two known tokens - so this is API hygiene, not a live path.
- `height_map` is tested for truthiness; a string `"false"` from a hand-built request would clamp an emblem to full-bleed. Same reachability as above.
- `vectorize`'s temps (`<out>.svg.tmp`, `<out>.svg.trace.png`) sit beside the deliverable in the library; only a hard kill mid-trace leaves them, and `.trace.png` is an image the flat-library listing would show (the GROK-LG5 #4 class). Needs a hard kill; not a defect of the current bytes.
- `alpha_from_dual`'s corner prior refuses (honestly) a subject that covers the corners; the caller keeps the opaque render with `alpha_error` - the second paid frame is spent for nothing on such compositions. By design (refuse-not-substitute), noted as the cost.

## Adversarial verification pass (refuted claims)
- "`Image.fromarray(..., mode='RGBA')` raises on Pillow ≥ 11.3 (mode parameter deprecated), so every dual-pass solve fails and the customer pays 2x for an opaque image" - refuted on the installed buildenv: Pillow 12.3.0 accepts the call with no warning even under `warnings.simplefilter('error')`; grok_oo_output.py 14/14 on the current bytes.
- "A transparent background with a junk `alpha_method` ships opaque silently" - refuted as a defect: library_gen's `elif background == BG_TRANSPARENT` routes every non-dual method to `alpha_by_removal`, so the deliverable is RGBA; the downgrade-of-method is recorded above as a missing safeguard (API-only input).
- "`vector_suitability` leaks the source file handle on Windows" - refuted: `convert()` forces the load and Pillow closes the exclusively-opened fp; `vectorize` itself uses a context manager.
- "`os.path.getsize(src_png)` measures the original while the trace ran on the downscaled copy, skewing the ratio warn" - refuted as a defect: the ratio's purpose is SVG size versus the PNG the customer keeps; the original is the deliverable.
- "`normalize` lets `opts['mode']` override the mode argument" - refuted: `o['mode'] = mode` is assigned after the update; the plan's mode wins and the heightmap clamp keys on the argument.
- "`alpha_by_removal` produces a hard 0/1 alpha" - refuted: `clip((dist - tol) / tol, 0, 1)` ramps over one tolerance width (soft edge of ~2·tol in colour distance).
