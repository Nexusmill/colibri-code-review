# Colibri Review - bug (FULL re-audit) - asset-forge/forge/tracer/png_stego.py

- **Source path:** `asset-forge/forge/tracer/png_stego.py`
- **Reviewer:** claude-fable-5-1 (fork of the lead session), Colibri G37 protocol, campaign item 1 (AF units)
- **sha256 reviewed:** `fa0e3134a97484413c99cf27e46d65dc75bad9fa68e90ce49ea7caaf66d4a688` (sha8 `fa0e3134`)
- **Date:** 2026-09-10 · **Mode:** bug, FULL review of the current bytes (owner ruling 2026-09-10: pre-gate audits untrusted - no delta)
- **Context pack:** jCodemunch get_file_outline + find_importers on all five units; call sites traced in forge/bundle.py, forge/pipeline.py, app.py (/api/verify), verify.py, sign_set.py, gen_bundle.py; the 2026-07-22 unit-6 svg_stego record and unit-9 row loaded as CLAIMS; both editions' forge/tracer/ hashed file by file (user build = 7 stubs, no hmac/hashlib/cryptography/numpy import, creator-only scripts absent from the user tree); probes run with asset-forge-user/.buildenv python (scipy 1.18, cryptography 50).

## Verdict
Correct for opaque textures (lossless round-trip verified) and NOT robust for the product's default transparent output: a transparent-pixel-flattening re-save removes both hidden layers (measured). Two design-level dockets (alpha-aware carrier; a version-stable permutation); no blind code change here.

## Bugs & vulnerabilities

**[HIGH (robustness claim; docket - design change)] Both hidden layers write their bits into the RGB of fully TRANSPARENT pixels; for an emblem (Asset Forge's default transparent output, ~70 % alpha-0 here) a re-save that discards the colour of transparent pixels - a lossless re-save of the visible image, the default of common editors/optimisers - destroys BOTH the deep-LSB token and the DCT serial: extract_png returns 'no tracer found'. The docstring's 'survives re-saves' does not hold for the product's default output class.** - `line 40-55 / 93-120`
- Docket: AF-TRACER-ALPHA-CARRIER: carry LSB bits only in pixels with alpha > 0 (the extractor sees the same alpha, so the slot set stays deterministic) and run the DCT-QIM on the alpha-composited (opaque) luma; version the layer (a metadata field) so files marked under the old scheme still decode. The simulated loss is CONFIRMED; that editors zero transparent RGB by default is PLAUSIBLE (not verified against a real GIMP export in-session).
- Verification: CONFIRMED by simulation (probe RED); trigger PLAUSIBLE

**[PLAUSIBLE-HIGH (docket)] The slot permutation comes from numpy.random.default_rng(seed).permutation - NumPy's Generator carries NO cross-version stream guarantee (NEP 19: 'the bit stream may change' in a release), so a NumPy upgrade on the creator machine could silently move every hidden bit position and make every previously sold asset unrecoverable; unverified because no such change has shipped for permutation yet** - `line 35-37 / 84-86`
- Docket: AF-TRACER-PERM-STABILITY: derive the permutation from a hash-based Fisher-Yates (HMAC-DRBG over the secret) or the legacy RandomState stream (guaranteed stable), versioned; pin the extractor's numpy in the meantime. Same code in svg_stego._perm.
- Verification: PLAUSIBLE (official NumPy policy, no shipped change observed)

## Missing safeguards
- embed_png's return value claims layers ['dct', 'lsb', 'metadata'] without checking that either embedder actually placed bits (both return the array unchanged when capacity is short).
- The PNG text chunk carries the full token in clear (by design, 'catches the lazy').

## Adversarial verification pass (refuted claims)
- embed_png silently skips the LSB layer on small images yet reports it - REFUTED: True in code (L > n returns arr) but needs an image under ~900 pixels; every Asset Forge output is >= 512x512 - unreachable from the product, noted only.
- extract_png on an attacker-supplied PNG (a found copy) can OOM the creator machine - REFUTED: PIL's decompression-bomb guard (MAX_IMAGE_PIXELS) raises before the RGBA array is built; the route is local, origin-guarded, creator-only.
- _lsb_extract's copies can be 0 and crash the reshape - REFUTED: copies < 1 returns None before the reshape; the length gate (< n // 8) keeps L within n + 8.
