# Colibri Review - bug (FULL pass, perfection #6) - PatternSkin/keyvault.py

- **Source path:** `PatternSkin/keyvault.py` (vendored byte-identical x3: asset-forge/forge/keyvault.py, asset-forge-user/forge/keyvault.py; blender_dev symlink)
- **Reviewer:** glm-5.3 (ZCode in-session), Colibri G37 + perfection protocol L2 postures A-D
- **sha256 reviewed:** `4bc56fc687a8e672625e0c9b9ffb46a1d43215ad024a7ee2f1223ff9ef88da2a` (sha8 4bc56fc6; 566 lines)
- **Date:** 2026-10-01 · **Mode:** bug, FULL pass (the file's FIRST adversarial-era review - the 2026-09-10 core sweep missed it; prior art = 8 probe batteries + 1 pre-gate MEDIUM remediation row)
- **Context pack:** file read end-to-end; jCodemunch outline (39 symbols); importers = keystore.py (KV-2 bridge, function-local at 148/151/176/179) + __init__.py (4253/4278, function-local - static analysis shows 0 for that reason); **live evidence: keepassxc-cli 2.7.12 probed on a throwaway vault** (empty group rc=0 '[empty]'; missing group rc=1 'Cannot find group'; wrong pw rc=1 'Invalid credentials'; `db-create` exists and is documented 'Create a new database.'); all 8 keyvault probes run (7 green + crypto1_bpy premise row RED = environment drift).

## Verdict
Shippable after the wave. The vault model is well-designed (sticky backend, atomic verified writes, secrets never in argv, KV3-LEAK-1 path-free errors, KDF iteration ceiling, verify-before-shred migration, GLM-R2 keychain-marker keep-rule). The defects are at the seams: the subprocess contract, a legacy-input edge that destroys its own source, and silent-success CLI mapping.

## Bugs & vulnerabilities

**[MEDIUM] KV-TIMEOUT - `_run` lets subprocess.TimeoutExpired escape the VaultError contract** - `line 128`
- What: a hung keepassxc-cli (agent prompt, locked db) raises TimeoutExpired from `_run`; the module's contract (VaultError "for an operational failure", mapped at AF's HTTP boundary) is bypassed - the user sees a raw traceback, not guidance.
- Trigger: any CLI invocation that stalls past the 30s timeout.
- Fix (W1): caught at the single choke point (all 6 call sites inherit); VaultError names the timeout and the likely prompt.
- Verification: CONFIRMED (trace; battery W1a RED pre-fix / GREEN post; mutation m1 caught).

**[MEDIUM] KV-BOM - a BOM'd providers.env migrates keys under invisible mangled names, then shreds the source** - `read_legacy_recoverable` `line 402`
- What: `open(pf, encoding="utf-8")` leaves the BOM in the first key name -> '\ufeffREPLICATE_API_TOKEN'. migrate_and_shred vaults the token under the mangled name, its read-back verify PASSES (the mangled name reads back fine), then the plaintext source is destroyed - post-migration `token_present()` is False and the user was told the migration succeeded.
- Trigger: any providers.env saved with a UTF-8 BOM (an editor fingerprint) on the migration path.
- Fix (W2): utf-8-sig. Sibling checked: secrets.dat is JSON (a BOM fails json.load -> {} - loud, not mangling).
- Verification: CONFIRMED at runtime (battery W2a reproduced the mangled key on pre-fix bytes; GREEN post; mutation m2 caught).

**[LOW] KV-LS-MAPPING - unrecognized CLI errors silently map to a successful empty-vault unlock** - `_list_entries` `line 220-228`
- What: rc!=0 with any wording outside the wrong-passphrase family returned [] - a future keepassxc-cli message change would fake a successful unlock of an empty vault. Current behavior on 2.7.12 is CORRECT for the three probed cases (missing group -> [] is right semantics); this is drift-proofing, not a live bug.
- Fix (W3): explicit three-way mapping (wrong-pw family -> VaultError; 'cannot find group'/'empty' -> []; anything else -> loud VaultError) + the '[empty]' output marker filtered (it currently costs one wasted `show` call per unlock of an empty vault).
- Verification: CONFIRMED as hardening (live-probed; battery W3a-d; mutation m3 caught).

**[LOW] KV-PROBE-PREMISE - crypto1_bpy's premise row reds a healthy machine** - `tests/harness/probes/keyvault_crypto1_bpy.py:42`
- What: the row asserts Blender's python lacks cryptography; after the one-click install ran for real on this machine the premise is gone and the row has been failing ever since - a battery that cries wolf. The row's own founding comment promises it "must not turn this baseline red forever".
- Fix (W4): premise SKIPs (recorded, non-failing) when cryptography is present; verdict loop honors SKIP.
- Verification: CONFIRMED (premise failed pre-fix on this machine; probe exits 0 post-fix with SKIP + 4 PASS).

## Adjudications (L2.5)
- ADJ-KV-1 deferred LOW: concurrent fernet keyring writes are a read-modify-write race (last writer loses a key); the fixed .tmp name self-detects collisions via byte-verify (loud failure, store untouched). Single-user local app. Deferred row with unblock condition.
- ADJ-KV-2: migrate_and_shred's plaintext backup_dir = documented creator-only convenience (G14-adjacent; docstring warning verbatim).
- ADJ-KV-3: keepassxc `db-create` VERIFIED LIVE on 2.7.12 - create path sound (refuted).
- ADJ-KV-4: unlock("") behaves as wrong passphrase - safe (create refuses empty pw).
- ADJ-KV-5: read-side KDF iteration count has no minimum - not exploitable without the passphrase; the 1..10M ceiling blocks grinding.

## Adversarial verification pass (refuted candidates - recorded as calibration)
- "create() uses a nonexistent db-create command" - refuted LIVE (2.7.12 has it; probed).
- "Empty group breaks unlock" - refuted LIVE: rc=0 + '[empty]' marker; unlock's cache ends empty and correct (one wasted show call - hygiene, folded into W3a).
- "KDF downgrade via tampered iters header" - refuted (attacker cannot craft a valid token at any iteration count without the passphrase).
- "Passphrase in argv" - refuted by design (stdin-fed; _run docstring; never logged).
- "Fernet tmp file ACL on Windows" - profile-dir default ACLs; acceptable.

## Remediation postscript (same session)
W1/W2/W3 applied to keyvault.py and mirrored byte-identical to both vendored twins (sha8 53613e63 x3); W4 applied to the probe. Battery tests/test_perfection_keyvault.py 12/12 (RUNTIME - the module is bpy-free; live fernet roundtrip), RED-first proven, 3/3 mutants caught; all 8 keyvault probes exit 0 (crypto1_bpy now SKIP+4PASS); full suite 35/35 ALL PASSED. Rows KV-TIMEOUT / KV-BOM / KV-LS-MAPPING / KV-PROBE-PREMISE in docs/remediation_manifest.json, same commit.
