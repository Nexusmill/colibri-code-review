# Colibri Review - bug (FULL re-audit) - asset-forge/make_user_edition.py

- **Source path:** `asset-forge/make_user_edition.py`
- **Reviewer:** claude-fable-5-1 (fork of the lead session), Colibri G37 protocol, campaign item 1 (Asset Forge tooling)
- **sha256 reviewed:** `d9ed85e471d0dbadd43eeceb9cfe6336360d0447a070e74262d3812b5442dac6` (sha8 `d9ed85e4`) - the PRE-fix bytes
- **Date:** 2026-09-10 · **Mode:** bug, FULL review of the current bytes (owner ruling: pre-gate audits untrusted - no delta)
- **Context pack:** FULL read of the current bytes at e7be3d43 (owner ruling 2026-09-10: the file's pre-gate reviews are untrusted); jCodemunch get_file_outline + find_importers (none of the six is imported by product code - entry points/tools); tools/sync_builds.py WHITELIST (which of the six are shared twins); the remediation/deferred rows and the prior .colibri_reviews records for launcher/secrets/make_user_edition loaded as CLAIMS re-verified at the bytes; stdlib urllib proxy logic read from the buildenv's own source; the windowed-process stream state proven with pythonw.exe started without a console.

## Verdict
NOT working as shipped: the generator has been unable to regenerate the user edition since 2026-08-24 and would quarantine the user tree's tracked source on every attempt. One further latent G18 hole in the copy filter. Everything the earlier CRITICAL fixed (whole-tracer nuke, recursive nono scan, key/cert extensions, edition-owned preservation, line-level marker scan) is present.

## Bugs & vulnerabilities

**[HIGH] Every regeneration aborts on forge/keyvault.py ('hazmat' marker) and quarantines the regenerated source - the user-edition generator has been broken since the vault landed (2026-08-24)** - `line 222`
- What: forge/keyvault.py (the CUSTOMER vault, vendored byte-identical from PatternSkin, GPL) derives its Fernet key with `from cryptography.hazmat.primitives ... PBKDF2HMAC` (lines 245-246). The contamination scan treats 'hazmat' on any non-`excludes` line as creator signing material, so the run ends with ABORTED and deletes every regenerated child of asset-forge-user (app.py, forge/, templates/, static/, launcher.py, requirements.txt, BUILD.md - all git-tracked).
- Trigger: Any run of make_user_edition.py on the current creator tree (reproduced on a sandboxed copy: 'ABORTED - creator-only material detected: forge\\keyvault.py').
- Impact: The stripped user edition cannot be regenerated from the creator tree; the twins have been kept aligned only by sync_builds --fix since 08-24. On the real tree a run wipes the tracked user source (restorable with git restore, but a destructive surprise).
- Fix: An explicit per-file marker allowance: _MARKER_ALLOW = {'forge/keyvault.py': ('hazmat',)} consulted by the scan. Battery MUE_clean_tree_still_generates RED -> GREEN on the fixed copy (the stub tracer lands, verify.py stays out).
- Verification: CONFIRMED by running the real script against a sandboxed copy of the creator tree.

**[LOW] Secret-store files (providers.env, secrets.dat, *.vault, *.kdbx) left inside the copied dirs ship into the customer edition - the filters know keys and certificates only (G18, latent)** - `line 160`
- What: copytree's ignore list and _SECRET_EXT cover .pem/.key/.crt/.cer/.der/.p12/.pfx/.pkcs12/.jks; a providers.env, secrets.dat, Nexusmill.vault or .kdbx inside forge/, static/ or templates/ is copied and passes the scan (.env/.dat are not in _SCAN_EXT either).
- Trigger: A creator saves a secret-store file inside the tree (the product stores them under ~/.asset-forge, so none exists today - latent).
- Impact: A token or vault file in the shipped edition with a 'Verified: no certificate...' line.
- Fix: Add *.env/*.dat/*.vault/*.kdbx to the copytree ignore and .env/.dat/.vault/.kdbx to _SECRET_EXT. Battery MUE_secret_store_files_never_ship: RED on a copy carrying only the marker fix (planted providers.env/secrets.dat/Nexusmill.vault all shipped), GREEN with both.
- Verification: CONFIRMED by running the script on a sandboxed copy with planted files (values built at runtime).

## Missing safeguards / notes
- rmtree on a symlinked child of DST raises (rmtree refuses symlinks) and leaves a half-cleared tree - creator-only dev script, edge.
- The quarantine deletes the user tree's tracked regenerated files by design (they are what the run produced); a git restore brings them back.

## Adversarial verification pass (refuted claims)
- a regeneration deletes git-tracked user-tree files outside KEEP/EDITION_OWNED -> refuted: every tracked top-level entry of asset-forge-user is in KEEP, EDITION_OWNED or written by STUBS (checked against git ls-files)
- the stub tracer lacks a symbol the shared code imports -> refuted: app.py / pipeline.py / bundle.py import names all exist in the stubs (load_or_create_key, secret_bytes, public_fingerprint, build_payload, make_token, embed_png/svg, extract_png/svg, identify_any, make_serial, make_token_asym, load_cert_pem); no attribute-style uses
- sign/ is deleted on regeneration (the 2026-08 'signing capability deleted' class) -> refuted: neither tree carries a sign/ dir today (the toolkit lives in Tools\sign); the WHITELIST entry is stale but harmless
- compiled .pyd/.so modules could smuggle crypto past the text scan -> refuted: no binary extension modules exist under forge/; __pycache__ is excluded at copy

## Remediation postscript (same session)
The fixes were applied after this review hashed the bytes above; the file is now `e9a64b6be1b8a887ff493d0bbff9c4b5ddcdbe5d211b48b5382f6136a7623cdd`. Rows AF-MUE-HAZMAT-ALLOW, AF-MUE-SECRET-STORES in `docs/remediation_manifest.json`, same commit.

