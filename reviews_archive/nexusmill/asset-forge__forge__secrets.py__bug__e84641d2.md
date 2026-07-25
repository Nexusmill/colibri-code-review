# colibri-review — asset-forge/forge/secrets.py  (bug)  [+ byte-identical asset-forge-user twin]
- model: claude-fable-5 (in-session, max) · sha256: e84641d27827ac3752e9c4787e816d44aae15ddd9a954173209a9d9e0d0d760b · date: 2026-07-22 · mode: bug
- context pack: DeepSeek V4 Pro batch review (18 findings) as INPUT hints; remediation_manifest
  (5a03f9c keychain-injection/DPAPI-UAF/silent-loss FIXED; glm20-7 export-KEY parsing FIXED;
  accepted-by-design fixed-temp-name + RMW race WON'T-FIX per G1); sync_builds (secrets.py is a
  SHARED byte-identical twin, NOT whitelisted); docstring contract (DPAPI/_enc/_dec format MUST
  match PatternSkin byte-for-byte). Current on-disk source re-read at dispatch (G36).

## Verdict
Shippable after this pass. The real, previously-unclosed risk was silent data loss on a corrupt
store. Most of DeepSeek's "CRITICALs" were already fixed or already adjudicated — recorded, not re-fixed.

## Bugs & vulnerabilities (CONFIRMED-new, fixed this pass)
**[HIGH] _load returns {} on CORRUPTION -> next _save destroys all secrets** - `_load`
- What/Trigger/Impact: a corrupt secrets.dat (bad JSON) made _load return {}; the next secret_set
  did d=_load(); d[k]=..; _save(d) -> os.replace wrote a near-empty dict, destroying every other
  stored key. Fix: split FileNotFoundError (->{}) from corruption; on corruption move the bytes
  aside once to secrets.corrupt (recoverable) then start clean. VERIFIED (corrupt load -> {} +
  .corrupt backup; post-corruption save keeps the corrupt bytes).
**[MEDIUM] _save world-readable window** - `_save`
- temp written at umask (~0644), os.replace made it live, chmod 0600 only AFTER -> brief window the
  plain:-base64 store was world-readable. Fix: chmod tmp 0600 BEFORE replace (+ HOME 0700). VERIFIED 0o600.
**[MEDIUM] empty ASSET_FORGE_HOME -> cwd** - module L14
- ASSET_FORGE_HOME="" made Path("") == cwd -> secrets written to an unintended dir. Fix: `or`. VERIFIED.
**[MEDIUM] migrate_legacy: scrub unwrapped + skipped when already-stored** - `migrate_legacy`
- scrub_legacy raised -> whole migration aborted mid-list; and a key already in the store left its
  redundant plaintext line in providers.env. Fix: wrap scrub in try/except; scrub even if already
  stored. VERIFIED (plaintext scrubbed).

## Verified-stale / already-adjudicated (DeepSeek re-flags — NOT re-fixed, per G35/G1/G11)
- fixed-temp-name (.tmp) race -> ACCEPTED-BY-DESIGN won't-fix (0o700 dir + single-user local tool).
- keychain arg-injection (shlex.quote+stdin -i), DPAPI use-after-free (_keep ref), silent-secret-loss
  on failed keychain set (raise OSError) -> all FIXED in 5a03f9c; current code confirmed to contain them.
- export-KEY parsing (strip 'export ') -> FIXED glm20-7; current code confirmed.
- _dpapi string_at(NULL,0) crash -> REFUTED (size-0 read does not dereference).
- PLAUSIBLE/low, not fixed: tab-separated `export\tKEY` + quoted export values (rare), _mac get/clear
  missing try/except (macOS security-missing, rare), _mac get rstrip vs strip, _dec silent '' on unknown
  prefix, secret_set input-type validation. Noted for a possible follow-up; none is a confirmed live defect.

## Note
PatternSkin/keystore.py is a SEPARATE implementation of the same store (not a byte-identical twin);
the _load data-loss guard + _save perm window should be mirrored there as its own review unit (follow-up).
