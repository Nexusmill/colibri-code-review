# colibri-review — PatternSkin/keystore.py — bug (hunt round 1, effort=high/security)

- **Source:** PatternSkin/keystore.py · **Scanner:** general-purpose subagent @ claude-opus (deep,
  security lens) · **Verification + fix:** claude-opus-4-8[1m] (in-session, Phase 3) · cost $0.00
- **sha256 reviewed:** 8a27009e63c324c9eb476ab456e13a62c4a59bbf40da9da9e4cbae44445aaeb8
- **Date:** 2026-07-23 · **Mode:** bug · round 1 of the top-20 hunt (deep security pass)
- **Context pack:** prior review `PatternSkin__keystore.py__bug__a713a447.md` (K3) + remediation rows
  (a13567a: command-injection, silent-loss-on-set, DPAPI UAF, corrupt-store, prefix-match, unclosed
  handle — all verified fixed) + the accepted-by-design tmp-path/RMW-race row. Callers: `secret_*`
  via `__init__.py`; `secret_is_plaintext` + `token_present`→`_read_replicate_token` run in panel
  `draw()`.

## Verdict
Materially safer than the prior-reviewed version — every prior HIGH is genuinely closed. Two real
new gaps the prior pass missed: a malformed shared store crashes the panel `draw()`, and (macOS) a
`clear` that ignores keychain-delete failure. Two fixed + tested; the macOS one deferred (untestable
here). One LOW credential-loss in the migration also fixed.

## Bugs & vulnerabilities

**[MEDIUM] Malformed `secrets.dat` crashes the panel `draw()` — the store is trusted to be dict-of-str** - `_secrets_load:64`, `secret_is_plaintext:186`, `secret_get:164`, `secret_set:158`
- What: `_secrets_load` returned `json.load()` with no `isinstance(...,dict)` check. `secrets.dat`
  is a **shared on-disk format with Asset Forge** (docstring line 5), so a foreign/older/partial
  writer can leave valid JSON that isn't a dict, or a dict with non-string values.
- Trigger: a non-dict store → `secret_get`/`secret_set` do `list.get` / `list[k]=…` (AttributeError/
  TypeError); a dict with a `null`/number value → `secret_is_plaintext` does `None.startswith` /
  `int.startswith`. `secret_is_plaintext` and `token_present` run in the panel `draw()`
  (`__init__.py:2661`), so the exception **crashes the panel** — a no-crash-in-draw violation
  (G20/G29).
- Fix: `_secrets_load` rejects a non-dict (preserved to `.corrupt.<ts>` like a parse failure,
  never destroyed); `secret_is_plaintext` uses `str(v).startswith("plain:")` to tolerate a non-str
  value inside a dict.
- **Verified by execution:** pre-fix, a `[1,2,3]` store raised `AttributeError 'list'` in
  `secret_get`/`is_plaintext`/`token_present`, and `null`/`123` values raised in `is_plaintext`;
  post-fix all return safely (`""`/`False`) and the non-dict is preserved to `.corrupt`.

**[LOW] Legacy migration destroys a *different* plaintext token** - `_migrate_legacy_token:203-211`
- What: for a `REPLICATE_API_TOKEN=` line, `if tok and not secret_get(...)` skipped the store when a
  token already existed — but the plaintext line was scrubbed to the "moved" comment regardless. If
  the stored token differs from the plaintext (a newer key in `providers.env`), the plaintext is
  destroyed while the stale stored token wins — one-way credential loss.
- Fix: only scrub when the stored value actually equals this line's token; otherwise keep the line.
- **Verified:** pre-fix a `r8_DIFFERENT` plaintext was scrubbed while `r8_STORED` won; post-fix the
  plaintext survives.

**[MEDIUM] (macOS) `secret_clear` ignores keychain-delete failure — token persists while UI says removed** - `_mac_keychain:126-129`, `secret_clear:175-181` — **CONFIRMED by trace, DEFERRED (KS-1)**
- What: `_mac_keychain("clear")` runs `security delete-generic-password` but never checks
  `returncode`, falling through to `return True`; `secret_clear` then unconditionally removes the
  `secrets.dat` marker. Asymmetric with the remediated `set` path, which checks `returncode` and
  raises. On a locked keychain the marker is removed (UI: "no key") while the Replicate credential
  remains in the login Keychain — a residual secret-at-rest the user believes deleted.
- **Why deferred, not fixed:** macOS-only; I cannot execute it on this Windows host. Shipping an
  unexecuted behavioural change to the `clear` flow risks wedging it (e.g. wrong handling of the
  "item not found" return code 44). The exact patch (mirror the `set` path: return
  `returncode in (0,44)`, raise in `secret_clear` on failure) is logged in `deferred_manifest.json`
  (KS-1), gated on a macOS test. Recording the gap rather than a blind fix (G2/G3).

## Verify
`junk/_keystore_test.py` — post-fix **11/11 PASS**, pre-fix **4/11** (verified by restoring HEAD
bytes: the F1 crash cases and the F3-B credential-destroy fail pre-fix). Store paths are repointed
to a temp dir, so the user's real `~/.asset-forge` is never touched. keystore imports headlessly;
the DPAPI store round-trips on this Windows host. The macOS keychain paths are NOT exercised.

## Refuted during verification (deep scan self-refuted; recorded in `_refuted_ledger.json`)
- `_read_replicate_token` returning `None` — every call site consumes it via `if not tok`/`bool(...)`.
- `_dec` on an unknown/`"keychain"` prefix on non-mac — returns `""`, wrapped by `secret_get`; no leak.
- token in argv / plaintext-in-logs — `set` feeds the value on stdin (`input=cmd`), not argv;
  `get`/`clear` pass only `name` as argv; captured stderr is never logged. No leakage path.
