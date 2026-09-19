# Colibri Review - bug (FULL re-audit) - asset-forge/forge/tracer/keys.py

- **Source path:** `asset-forge/forge/tracer/keys.py`
- **Reviewer:** claude-fable-5-1 (fork of the lead session), Colibri G37 protocol, campaign item 1 (AF units)
- **sha256 reviewed:** `c203388aeca13096ebaf796b41258d2e1b17ed0a36a3ea8193ae41199d3fd3d1` (sha8 `c203388a`)
- **Date:** 2026-09-10 · **Mode:** bug, FULL review of the current bytes (owner ruling 2026-09-10: pre-gate audits untrusted - no delta)
- **Context pack:** jCodemunch get_file_outline + find_importers on all five units; call sites traced in forge/bundle.py, forge/pipeline.py, app.py (/api/verify), verify.py, sign_set.py, gen_bundle.py; the 2026-07-22 unit-6 svg_stego record and unit-9 row loaded as CLAIMS; both editions' forge/tracer/ hashed file by file (user build = 7 stubs, no hmac/hashlib/cryptography/numpy import, creator-only scripts absent from the user tree); probes run with asset-forge-user/.buildenv python (scipy 1.18, cryptography 50).

## Verdict
Shippable after two small fixes (both verified GREEN on a scratch copy): an empty ASSET_FORGE_HOME put the master secret in the cwd, and the root-of-trust file was rewritten in place. The plaintext-at-rest storage is a G18 doctrine gap docketed for the vault (creator-only machine, not blind-fixed).

## Bugs & vulnerabilities

**[MEDIUM] An EMPTY ASSET_FORGE_HOME resolves KEY_DIR to the current working directory: the 256-bit master secret is written as ./creator_key.json wherever the app was launched from, and _ensure_dir chmods that folder 0700 on POSIX (config.py guards this exact class with `or`; the 07-22 unit-9 row called it RECURRING and missed this file)** - `line 22`
- Fix: KEY_DIR = Path(os.environ.get("ASSET_FORGE_HOME") or (Path.home() / ".asset-forge"))   # an EMPTY env var ...
- Verification: CONFIRMED (probe RED on the repo bytes)

**[MEDIUM] _save rewrites the root of trust IN PLACE (open 'w' + json.dump): an interruption between the truncate and the last byte leaves creator_key.json empty/half-written - every sold tracer unverifiable; the display-name update path (line 44-47) re-saves on every creator_id mismatch, so the window is hit routinely** - `line 63`
- Fix: def _save(data: dict): ...
- Verification: CONFIRMED (probe RED on the repo bytes)

**[MEDIUM (doctrine G18)] The master secret sits in a plaintext JSON file; the 0600 chmod is a no-op on Windows (chmod toggles read-only only), so any process of the creator's Windows user reads it - G18 says keys encrypted at rest; the provider keys moved to the KeePassXC vault on 08-24, this one did not** - `line 52`
- Fix: AF-TRACER-KEY-AT-REST: keep the secret in the Nexusmill vault (forge/secrets.py API) with the JSON file reduced to creator_id + created; migrate an existing plaintext file on first run and shred it. Design change, creator-only machine - docket, not blind-fixed.
- Verification: CONFIRMED at the bytes (doctrine); docketed

## Missing safeguards
- Windows: os.chmod(0o600/0o700) does not restrict access; the plaintext file is readable by every process of the user (the G18 docket).
- The key file is also read on EVERY app start (app.py load_or_create_key) - fine, but each mismatch of creator_id rewrites it, which is why the atomic write matters.

## Adversarial verification pass (refuted claims)
- public_fingerprint (sha256 of 'pub:'+secret_hex) leaks the secret - REFUTED: A 256-bit random secret has no feasible preimage; the fingerprint is 64 bits of a one-way hash.
- A truncated creator_key.json silently regenerates a NEW key (old tracers orphaned) - REFUTED: json.load raises on a truncated file and load_or_create_key does not catch it - it fails loud, which is the right side of the error.

## Remediation postscript (same session)
The fixes were applied after this review hashed the bytes above; the file is now `425a859963b3f2c277a93fc73bb14fabf9ffa5f7a8b1860bc204a16deadb22d4`. Rows AF-TRACER-KEY-EMPTY-HOME, AF-TRACER-KEY-ATOMIC in `docs/remediation_manifest.json`, same commit.

