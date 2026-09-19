# Colibri Review - bug (FULL re-audit) - asset-forge/forge/library.py

- **Source path:** `asset-forge/forge/library.py` (twin `asset-forge-user/forge/library.py` byte-identical - fix applies to both)
- **Reviewer:** claude-fable-5-1 fork (in-session), Colibri G37 protocol, campaign item 1 (AF units), rank 28
- **sha256 reviewed:** `640d29b08dc5779632304b3f8b47534cfcf0b4dba521d3689d4e335e8af08de3` (sha8 `640d29b0`) - the PRE-fix bytes
- **Date:** 2026-09-10 · **Mode:** bug, FULL read of the current bytes (owner ruling: pre-gate audits untrusted)
- **Context pack:** importers bundle.py:158-193 (categories + per-item reference_data_uri), userlib.py (data_uri thumbnailer), app.py:485/972/1016 (availability, categories, thumbs); make_user_edition.py DROP_IN_FORGE does NOT drop this file, so it ships in the user edition; imagegen/config.py exports HOME and load_providers; the UNIT 11 remediation row (thumb traversal refuted) loaded as a claim.

## Verdict
Shippable after one LOW fix. The traversal guard, symlink filter, corrupt-image tolerance and seeded pick all hold; the one defect is a developer-machine path shipped verbatim as the default library root.

## Bugs & vulnerabilities

**[LOW] `DEFAULT_ROOT` is the developer's own filesystem path, shipped in the byte-identical user edition** - `line 17`
- What: `DEFAULT_ROOT = r"C:\Users\User\source\repos\3DPrinting\Dragon\images"` is the fallback whenever neither the env var nor the providers store names a library. On a customer's machine it can never exist, and it discloses the developer's user name and repo layout in the compiled product (G18-adjacent hygiene; the docstring even names the Dragon library).
- Trigger: any user-edition install without ASSET_FORGE_LIBRARY set (all of them).
- Impact: no functional break (`available()` is False, the UI hides the browser) - a leaked local path in a shipped binary and a default that is wrong for every customer.
- Fix: `DEFAULT_ROOT = str(HOME / "style_refs")` with HOME imported from imagegen/config.py (the app home the rest of the product uses); docstring re-worded. The creator points ASSET_FORGE_LIBRARY at the Dragon folder once (env or the providers store - the mechanism the docstring already describes). Battery `LIB_no_developer_path_in_source` + `LIB_default_root_under_app_home` RED on the repo, GREEN on the patched copy; `LIB_env_override_still_wins` green on both.
- Verification: CONFIRMED (bytes; make_user_edition.py keeps the file).

## Missing safeguards
- `categories()` is `lru_cache(maxsize=1)` and `_first_image_str` `lru_cache(256)` - a library path changed at runtime (settings) or files added later are invisible until restart.
- `pick_image(category, seed)` indexes the rglob order, which is filesystem-dependent: the same seed picks a different reference after a file is added - harmless for recipes (they carry the data URI), noted.
- `root()` calls `load_providers()` on every call (each thumb / category listing re-reads the providers store).

## Adversarial verification pass (refuted claims)
- "`/api/library/thumb/<category>` traverses" - `_images_in` resolves `root/category` and refuses anything whose parents do not include the root; absolute categories resolve outside and return [].
- "rglob follows a symlink out of the library" - each candidate's resolved path must be relative to the resolved root.
- "A corrupt image 500s the route" - `thumb_uri`/`reference_data_uri` catch and return None (the UNIT 11 row's fix is present).
- "`is_relative_to` is missing on the shipped Python" - the build env is 3.12.

## Remediation postscript (same session)
The fixes were applied after this review hashed the bytes above; the file is now `9cc8f6ef4097d7aa3b5ad2e2d81e95ab952886ef2f4f53e7c41cbf6d277bdb9a`. Rows AF-LIBRARY-DEV-PATH in `docs/remediation_manifest.json`, same commit.

