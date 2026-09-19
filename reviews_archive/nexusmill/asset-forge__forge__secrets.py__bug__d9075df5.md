# Colibri Review - bug (FULL re-audit) - asset-forge/forge/secrets.py

- **Source path:** `asset-forge/forge/secrets.py` (twin: asset-forge-user/forge/secrets.py (byte-identical))
- **Reviewer:** claude-fable-5-1 (fork of the lead session), Colibri G37 protocol, campaign item 1 (Asset Forge tooling)
- **sha256 reviewed:** `d9075df531c223fce9ea915176045eba37fab56c03d4da333282b9711f3d5acd` (sha8 `d9075df5`)
- **Date:** 2026-09-10 · **Mode:** bug, FULL review of the current bytes (owner ruling: pre-gate audits untrusted - no delta)
- **Context pack:** FULL read of the current bytes at e7be3d43 (owner ruling 2026-09-10: the file's pre-gate reviews are untrusted); jCodemunch get_file_outline + find_importers (none of the six is imported by product code - entry points/tools); tools/sync_builds.py WHITELIST (which of the six are shared twins); the remediation/deferred rows and the prior .colibri_reviews records for launcher/secrets/make_user_edition loaded as CLAIMS re-verified at the bytes; stdlib urllib proxy logic read from the buildenv's own source; the windowed-process stream state proven with pythonw.exe started without a console.

## Verdict
Clean at the full read - 0 confirmed. Every prior remediation claim is present at the bytes: corrupt-store preservation (secrets.corrupt), 0600-before-replace, empty ASSET_FORGE_HOME guard, the export-form migration + scrub-even-if-stored, the newline guard before `security -i`, the DPAPI buffer pin, keychain-write failure raising. Vault-first delegation (KV-2) reads as designed.

## Bugs & vulnerabilities

None confirmed.

## Missing safeguards / notes
- migrate_legacy takes the providers.env value verbatim: a dotenv-style quoted value (KEY="r8_...") is stored WITH its quotes and the plaintext line is then scrubbed - the stored token is unusable. Low: the current reader never consumed providers.env lines either (KV-5 import-only), so nothing that worked is lost; strip matching surrounding quotes if it is ever revisited (the PatternSkin keystore twin has the same shape).
- _save's os.replace can raise PermissionError on Windows while the add-on's keystore holds secrets.dat open (no FILE_SHARE_DELETE) - a user-click path, retryable, not the paid-loop class fixed in library_gen.
- _mac('set') relies on `security -i` honouring shlex's '"'"' idiom for a value containing a single quote - unverifiable here (no macOS); already docketed under GROK-SEC5.

## Adversarial verification pass (refuted claims)
- _dpapi's _in(blob) temporary is freed during the CryptProtectData call (UAF) -> refuted: byref keeps the _BLOB alive for the call and blob._keep pins the buffer; the entropy blob is a named local
- a second corruption after secrets.corrupt exists loses the store -> refuted: 'preserve once' is the documented contract; the first preserved copy is the recoverable one and the log line names it
- concurrent secret_set from two Flask threads drops a key (read-modify-write) -> refuted: one SECRET_KEY exists; adjudicated won't-fix 07-22 (single-user local tool)
- _dec returns '' for an unknown prefix and hides corruption -> refuted: an unknown prefix is treated as 'no key' by every caller, which is the safe direction; is_plaintext/token_present report the state
- secret_get on macOS ignores the keychain when the vault is unlocked -> refuted: vault-first is the KV-2 delegation by design; the keychain marker is still served when the vault has no value
