# Colibri Review - bug (FULL re-audit) - asset-forge/forge/pipeline.py

- **Source path:** `asset-forge/forge/pipeline.py` (twin `asset-forge-user/forge/pipeline.py` byte-identical)
- **Reviewer:** claude-fable-5-1 fork (in-session), Colibri G37 protocol, campaign item 1 (AF stale units)
- **sha256 reviewed:** `f3c5a3cec49815481bd8208db92c6a50b121f268380209a189c7391438399572` (sha8 `f3c5a3ce`)
- **Date:** 2026-09-10 · **Mode:** bug, FULL review (pre-gate ruling)
- **Context pack:** FULL read of the current bytes (owner ruling 2026-09-10: the unit's 07-22..08-15 reviews predate the gate and are untrusted); jCodemunch get_file_outline + find_importers; every remediation/deferred row naming the file loaded as CLAIMS and re-checked at the bytes; call sites traced (app.py bundle job + prog callback, library_gen, gen_bundle.py, concurrency.map_bounded/imap_bounded/Stop). Twin asset-forge-user/<same path> byte-identical (sha256 equal) - one review covers both.

## Verdict
Clean. Every remediation row present at the bytes: category/family refuse separators, '..', absolute and drive paths; count/base_seed/buyer/formats validated BEFORE mkdir; the generation loop and the manifest/signing/write are each under their own INCOMPLETE net; SALE vs PREVIEW manifests differ only where they should (token/serial/signature). Live in both editions (app.py /api/generate).

## Bugs & vulnerabilities
None confirmed.

## Missing safeguards (not fixed)
- `formats` accepts an unknown entry alongside a valid one (`("png", "bogus")`): the bogus one is ignored silently, the manifest is honest about what was written.
- `count` has no upper bound here (the app caps it; the CLI is the owner's).
- Writing INCOMPLETE.txt inside the `except` can itself raise (disk full) and mask the original error - the same shape bundle.py uses.

## Adversarial verification pass (refuted claims)
- "the module is dead code" - refuted: both app.py editions import it for /api/generate.
- "`canvas.to_svg()` embeds the sale token on preview sets" - refuted: gated on `is_sale`.
- "a string `formats` ("png") writes nothing" - refuted: the `any(f in ...)` guard rejects it upfront (a str iterates characters).
- "`base_seed` as a float seeds differently" - refuted: `int()` upfront, ValueError on non-integers.
