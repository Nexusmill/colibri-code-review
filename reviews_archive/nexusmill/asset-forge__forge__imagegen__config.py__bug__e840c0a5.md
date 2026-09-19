# Colibri Review - bug (FULL re-audit) - asset-forge/forge/imagegen/config.py

- **Source path:** `asset-forge/forge/imagegen/config.py` (twin `asset-forge-user/forge/imagegen/config.py` byte-identical, G23)
- **Reviewer:** claude-fable-5-1 fork (in-session), Colibri G37 protocol, campaign item 1 (AF units), rank 27
- **sha256 reviewed:** `e840c0a55bca36d362e72d0800f24fbe7e60121519fd4c45f331c51314114d1a` (sha8 `e840c0a5`)
- **Date:** 2026-09-10 · **Mode:** bug, FULL review of the current bytes (owner ruling 2026-09-10: the UNIT-9 record that touched this file predates the gate; its claim - an empty ASSET_FORGE_HOME must not resolve to cwd - re-verified, not taken as baseline)
- **Context pack:** jCodemunch outline + importers (imagegen/__init__, prompts, replicate_flux, schema, forge/library - load_providers; app.py settings/save_settings/library_dir through the imagegen package); forge/secrets.py contract (migrate_legacy / secret_get / secret_set / scrub_legacy, SECRET_KEYS); remediation row UNIT 9; doctrine G18 (no plaintext keys, providers.env import-only KV-5). Every one of the 78 lines read.

## Verdict
Clean - 0 confirmed. The KV-5 contract holds at the bytes: providers.env is read only through `migrate_legacy` (lift-then-scrub), the served values come from the encrypted store with real environment variables layered on top, `save_provider` refuses to resurrect the plaintext file for any non-secret key, and an empty ASSET_FORGE_HOME cannot resolve to the working directory.

## Bugs & vulnerabilities
None confirmed.

## Missing safeguards (not fixed)
- `save_settings` writes settings.json in place (`write_text`) and `settings()` swallows a corrupt file as `{}`: a crash mid-write (a millisecond window on a tiny file) would read as a first run - library_dir back to the default - and the NEXT `save_settings(patch)` would rewrite the file from `{}` + patch, dropping the other keys (custom_styles, bundled_dir). PLAUSIBLE, LOW: tmp -> os.replace plus a logged warning on a corrupt file would close both halves.
- `library_dir()` trusts the settings value's type (`Path(d)` on a non-string would raise); the only writer is the app's own settings route.
- `load_providers` re-runs `migrate_legacy` on every call (a stat of providers.env per call) - cost, not correctness.

## Adversarial verification pass (refuted claims)
- "An empty ASSET_FORGE_HOME resolves HOME to the current directory" - refuted: `os.environ.get(...) or Path.home()/...` (the UNIT-9 fix is present).
- "providers.env lines are served as live secrets" - refuted: only `migrate_legacy` reads the file; values come from `secret_get` over SECRET_KEYS, then env vars.
- "save_provider writes the key in plaintext" - refuted: `secret_set` + `scrub_legacy`; anything not in SECRET_KEYS raises.
- "An exception inside the store lookup hides the environment override" - refuted: the env loop runs after the try/except, unconditionally.
