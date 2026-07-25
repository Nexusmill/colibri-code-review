# colibri-review — asset-forge/forge/secrets.py — bug (hunt round 1, effort=high) [+ twin]

- **Source:** asset-forge/forge/secrets.py (byte-identical twin asset-forge-user/…, G23) · **Scanner:**
  general-purpose subagent @ claude-opus (deep security) · **Verification + fix:** claude-opus-4-8[1m]
  (in-session, Phase 3) · cost $0.00
- **sha256 reviewed:** 5007dc2334a4def7e21c52750bf1e8931b09800244324d3003891b155b06467e ·
  **post-fix:** a93d9f9c
- **Date:** 2026-07-23 · **Mode:** bug · round 1. Prior review `e84641d2` (5 findings, all closed).
- **Context pack:** remediation rows (corrupt-store `_load→{}` HIGH fixed 07-22; export-KEY parse
  fixed; temp-name/RMW won't-fix); call sites — `imagegen/config.py` (`load_providers` wraps secret
  access in try/except; **`save_provider` calls `secret_set` UNWRAPPED**). Current bytes re-hashed (G36).

## Verdict
One real defect the prior pass missed — the same class as the keystore fix (unit 9), in Asset Forge's
separate secret-store impl. The 07-22 corruption guard only defends against JSON that *fails to
parse*; a store that is valid JSON but not an object slips through and crashes every caller. Fixed.

## Bugs & vulnerabilities (CONFIRMED, fixed)

**[MEDIUM] Non-dict (valid-JSON) store crashes all callers and defeats the corruption guard** - `_load:70` (impact at `secret_get:142`, `is_plaintext:162`, `secret_set:136/138`)
- What: `_load` returned `json.loads(...)` unchecked. `null`/`[]`/`"str"`/`123`/`true` parse without
  exception, so the corrupt-store branch never runs (no `.corrupt` backup) and the non-dict reaches
  callers: `secret_get`/`is_plaintext` → `AttributeError`, `secret_set` → `TypeError`.
- Trigger: any `secrets.dat` whose top-level JSON is not a dict (external edit, a truncation/sync
  artifact that happens to be valid JSON, a stray `null`).
- Impact: `load_providers` swallows its calls, but `config.save_provider` calls `secret_set`
  **unwrapped** → the exception propagates to the Flask handler (500) and the user's new key is
  **never stored**. Exactly the failure class the 07-22 "corrupt store must not crash / must not
  destroy secrets" fix was meant to cover — the guard had a shape hole.
- Fix: `isinstance(dict)` gate in `_load` that raises into the existing corrupt-preserve path.
- **Verified by execution:** pre-fix all five non-dict types crashed `secret_get`/`is_plaintext`/
  `secret_set`; post-fix all return safely, the bad store is preserved to `.corrupt` (not destroyed),
  and a proper dict store still round-trips. `module._DAT` repointed to a temp dir — real store
  untouched.

## Verify
`junk/_afsecrets_test.py` — post-fix **16/16 PASS**, pre-fix **6/21** (verified by restoring HEAD
bytes). Mirrored to the twin; `tools/sync_builds.py` green; py_compile clean. Forge stack + DPAPI run
headlessly on this Windows host, so this is real coverage.

## Refuted during verification (recorded in `_refuted_ledger.json`)
- `_dpapi` input-BLOB use-after-free — the inline `_BLOB` (holding `._keep = buf`) stays alive
  through the synchronous `CryptProtect` call via `byref`; no dangling pointer.
- `_log.warning` leaking secret bytes — it logs `%r` of the parse *exception* (position-only),
  never the file contents or the key.
- `_dec`/`_mac`/`secret_set` value-type items — recorded PLAUSIBLE-low in prior review `e84641d2`,
  current bytes unchanged; not relitigated.
