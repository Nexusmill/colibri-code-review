# Colibri Review - bug (FULL re-audit) - Spector/spectordna.py

- **Source path:** `Spector/spectordna.py`
- **Reviewer:** claude-fable-5-1 (in-session), Colibri G37 protocol, campaign item 1 (product cores), rank 52
- **sha256 reviewed:** `42304e8a43cb5a26145704103a7e9aa97d282c694ae4b38b6f79d91e0fa527c9` (sha8 `42304e8a`)
- **Date:** 2026-09-10 · **Mode:** bug, FULL review of the current bytes (owner ruling 2026-09-10: this file's prior audits predate the adversarial gate and cannot be trusted - no delta against them)
- **Context pack:** FULL read of the current bytes (owner ruling 2026-09-10: the file's reviews of 2026-07-19..08-15 predate the gate and are untrusted); jCodemunch `get_file_outline` + `find_importers`; the prior review records and the remediation/deferred rows for the file loaded as CLAIMS to re-verify, not as baseline; call sites traced with `get_symbol_source`.

## Verdict
Clean. Input validation, the exact component-count kernel drop (SDNA-1), the ARPACK wrap and the scale-invariant divide all hold; `eigsh(sigma=-1e-5, which='LM')` is the documented shift-invert for the smallest modes.

## Bugs & vulnerabilities
None confirmed.

## Adversarial verification pass / notes
- Known and still open, unchanged: sliver triangles get an unclamped cotangent weight in `cotan_laplacian` (the robust engine is the default so real exposure is low); `dna_distance`/`nearest` truncate to the shorter vector while `index.py` pads - both have zero production callers.
