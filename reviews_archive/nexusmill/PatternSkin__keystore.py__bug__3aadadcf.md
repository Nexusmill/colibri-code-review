# Colibri Review - bug (DELTA) - PatternSkin/keystore.py

- **Source path:** `PatternSkin/keystore.py`
- **Reviewer:** claude-fable-5-1 (in-session), Colibri G37 protocol, campaign item 1 (product cores), rank 9
- **sha256 reviewed:** `3aadadcfcc0d5521ddf5e4b41ed9dabfc55375cd8fb8a513d85bf6b433e094d3` (sha8 `3aadadcf`)
- **Date:** 2026-09-10 · **Mode:** bug, stale-file DELTA against `8a27009e` (2026-07-24 round 2 verification)
- **Delta reviewed:** 6 commits / 197 diff lines: 548b320f (non-dict store preserved as .corrupt), 94d62567 (KS-1 keychain delete honesty), 60bbde28 (GLM-POLISH), 7b56acd9 (GROK-KS3 atomic scrub + loud failure), fd53f382/0e9adaff (KV-2/KV-3 vault-first accessors + draw-safe `vault_ui_state`) - every hunk read.
- **Context pack:** the prior review record(s) for the file, `docs/remediation_manifest.json` rows from 2026-07-24 on, `docs/deferred_manifest.json` rows naming the file, `_hunt_plan.json` + `_refuted_ledger.json` loaded; jCodemunch `get_symbol_source` on the call sites each finding depended on.

## Fixed since last review
- Every remediation row dated after the base review was verified present at the bytes (they are the delta).

## Verdict
Clean at the delta. Vault-first reads fall back to the legacy store when the vault is locked or lacks the key; `secret_clear` keeps the marker whenever any store refuses the delete; the legacy scrub only rewrites the line when the stored token equals the plaintext one and writes atomically; `vault_ui_state` caches the disk probes under a TTL and reads the memory-only `unlocked` live.

## Bugs & vulnerabilities
None confirmed at the delta.

---

# FULL re-audit 2026-09-10 (appended - the record above predates the adversarial gate and is kept as history, not as baseline)

# Colibri Review - bug (FULL re-audit) - PatternSkin/keystore.py

- **Source path:** `PatternSkin/keystore.py`
- **Reviewer:** claude-fable-5-1 (fork of the lead session), Colibri G37 protocol, campaign item 1 (product cores), rank 9
- **sha256 reviewed:** `3aadadcfcc0d5521ddf5e4b41ed9dabfc55375cd8fb8a513d85bf6b433e094d3` (sha8 `3aadadcf`) - the PRE-fix bytes
- **Date:** 2026-09-10 · **Mode:** bug, FULL review of the current bytes (owner ruling 2026-09-10: this file's prior audits - K3 07-20, the 07-23 hunt round, the 08-15/08-20 GLM/Grok rounds, the 08-24 KV-2 wiring - predate the adversarial gate and are untrusted; no delta against them)
- **Context pack:** every line read (333); importers `__init__.py` (the provider-key dialog draw/execute 3474-3517, `_gen_texture_to_library`, the library generator, the four `_read_replicate_token` operator sites, `token_present`/`vault_ui_state` in panel draw), `filmstrip.py` (dress dialog + modal), `keyvault.py` (the vault accessors 313-390, create/unlock 143-217, `migrate_and_shred` 511-548); the sibling reader of the SAME shared file `asset-forge/forge/secrets.py` (`migrate_legacy`/`scrub_legacy` 201-240); remediation/deferred rows KS-1, GROK-KS3, GLM-POLISH, KV-2/KV-3 and features PS-KV-2/PS-KV-3/PS-GROK-R5 loaded as CLAIMS and re-verified at the bytes; the prior records `__bug__a713a447` (K3), `__bug__8a27009e`, `__bug__3aadadcf` (today's delta) read as claims.

## Verdict
Shippable after one small fix. Every prior remediation claim is PRESENT at the bytes (DPAPI buffer kept alive, non-dict store preserved to `.corrupt`, 0600 temp file on POSIX, `security -i` fed over stdin with newline rejection and shlex quoting, keychain clear honesty, vault-first accessors, atomic scrub with a logged failure). One CONFIRMED cross-file contract break with the Asset Forge reader of the same `providers.env`, one PLAUSIBLE macOS-only draw() hazard.

## Bugs & vulnerabilities

**[LOW] The shared `providers.env` migration does not recognise the `export KEY=value` form its Asset Forge twin already handles** - `_migrate_legacy_token`, `line 289-291`
- What: `s.split("=", 1)[0].strip() == "REPLICATE_API_TOKEN"` is the only match. Asset Forge's reader of the SAME file (`forge/secrets.py` `migrate_legacy` 228-229 and `scrub_legacy` 209-210) strips a leading `export ` first, with the comment "shell-sourced 'export KEY=v' must migrate too - else the token stays in plaintext after 'migration'". Pattern Skin never got that clause.
- Trigger: a `~/.asset-forge/providers.env` whose token line reads `export REPLICATE_API_TOKEN=...` (the shell-sourced convention for a file named `.env`), with Pattern Skin installed without Asset Forge having migrated first (the products are sold separately).
- Impact: the panel reports "No API key" although the key is in the file, and the plaintext key is never lifted into the encrypted store nor scrubbed (G18) - and because `_read_replicate_token` re-runs the migration on every read, it stays that way forever.
- Fix: strip a leading `export ` before the key compare (the twin's exact clause). Checked against every call site: the function's only caller is `_read_replicate_token`; comment/marker lines have no `=` and are untouched; a prefix-named variable (`REPLICATE_API_TOKEN_BACKUP`) still does not match.
- Verification: CONFIRMED by trace and by reproducer `probe_ps_keystore_1.py` (temp store, real DPAPI): RED on the current bytes (`got None`, plaintext left in place), GREEN on a scratch copy with the fix; the bare form and unrelated lines unchanged.

**[LOW · PLAUSIBLE] (macOS) a "keychain" marker with a LOCKED login keychain makes panel draw() block on a `security` prompt every 5 s** - `secret_get` 227-228 via `token_present` 201
- What: on a `_PRESENCE` cache miss, `token_present()` (called from panel draw at `__init__.py` 5473/5661/5788/7115) runs `_read_replicate_token` -> `secret_get` -> `_mac_keychain("get")` -> `subprocess.run(["security", "find-generic-password", ..., "-w"])`. If the login keychain is locked, `security -w` requests an unlock through the SecurityAgent dialog and the subprocess (and Blender's draw) waits for the answer; a cancel returns "", the cache stores False for 5 s, and the next redraw after that repeats it.
- Unverified because: macOS-only; no host here to observe whether `security find-generic-password -w` prompts on a locked keychain or fails immediately (error 36 / "User interaction is not allowed" is what a non-GUI session gets). The normal login keychain is auto-unlocked at login, so exposure is a user who locked it deliberately.
- Suggested safeguard (not a fix to apply blind): pass the keychain read through a short timeout or cache a keychain failure for longer than the 5 s TTL.

## Missing safeguards (not fixed, no defect traced)
- `_secrets_load` treats ANY read exception as corruption and renames the file to `.corrupt.<ts>`; a transient `PermissionError` (an AV scanner holding the file) would rename a healthy store. The rename itself would also fail under the same lock, which is what keeps it from being a traced defect.
- A `providers.env` value written with quotes (`REPLICATE_API_TOKEN="r8_..."`) is stored verbatim, quotes included - the same as the Asset Forge twin (both `strip()` only), so consistent, but the key can never authenticate and the validate step never sees it (migration bypasses `_validate_provider_key`).
- No lock around the load-modify-save of `secrets.dat` (accepted-by-design row from 07-23; the file now carries one key).
- `secret_get` on macOS returns "" for both "no key" and "keychain read failed" (K3's note from 07-20 still stands).

## Adversarial verification pass (refuted claims - one line each)
- "`_dpapi` passes a temporary `_BLOB` to `byref` that can be freed mid-call" - refuted: `byref()` holds a reference to its object for the call, and `_in()` pins the buffer on the struct (`_keep`).
- "`_dec('dpapi:')` (empty payload) crashes" - refuted: `create_string_buffer(b'', 0)` is legal, `CryptUnprotectData` fails, `OSError` is caught by `secret_get` -> "".
- "`secret_set` under an unlocked vault leaves a stale legacy DPAPI copy that `secret_get` serves after `lock()`" - refuted as a defect of this file: PS-KV-2 mandates vault-only writes, `secret_clear` removes both stores, and `keyvault.migrate_and_shred` deletes the legacy store on migration; a user who never migrated keeps the pre-vault token in the legacy store, which is the documented fallback.
- "`_migrate_legacy_token` scrubs a DIFFERENT token's line" - refuted: the scrub only fires when `stored == tok` (the 07-23 fix is present at 299-304).
- "the scrub's temp file (`providers.env.tmp`) is world-readable on POSIX" - refuted as new exposure: by the time it is written the token line is already the marker comment; remaining lines are whatever the user put there.
- "`token_present` serves a stale True after a secret is cleared through the vault dialog" - refuted: bounded by the documented 5 s TTL, and `secret_clear`/`secret_set` in this module invalidate immediately.
- "token leaks into logs" - refuted: the only log line formats the exception of a failed file write; no path formats the value.

## Remediation postscript (same session)
The fixes were applied after this review hashed the bytes above; the file is now `cae97d2d53300ea81165e0fa888868f850ccba586207a568ca62584780957e90`. Rows PS-KS-EXPORT-FORM in `docs/remediation_manifest.json`, same commit.

