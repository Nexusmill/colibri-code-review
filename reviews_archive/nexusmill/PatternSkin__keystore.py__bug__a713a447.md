# BUG review: PatternSkin\keystore.py

- source: `C:\Users\User\source\repos\Nexusmill\PatternSkin\keystore.py`
- model: moonshotai/kimi-k3
- reviewed: 2026-07-20 01:07
- tokens: in 3026 / out 2358
- est cost: $0.0444

---

## Verdict
Not safe to ship as-is. The biggest risk is the macOS Keychain path: secrets and names are interpolated unvalidated into an interactive `security` command stream (newline injection), and `secret_set` reports success even when the `security` CLI fails — silently losing the token while recording `"keychain"` in `secrets.dat`.

## Bugs & vulnerabilities

**[HIGH] Command injection into `security -i` via unvalidated name/value** - `lines 92-93`
- What: `name` and `value` are interpolated directly into an interactive `security` command fed on stdin. The comment claims tokens match `[A-Za-z0-9_-]` and therefore "need no quoting," but nothing enforces that charset — it's an assumption, not a validation.
- Trigger: any `secret_set(name, value)` where `value` (or `name`) contains a newline, e.g. `secret_set("k", "tok\ndelete-generic-password -s other-service")`, or a name containing spaces/quotes.
- Impact: arbitrary `security` CLI commands execute with the user's Keychain privileges (read/delete/overwrite arbitrary keychain items); at minimum, malformed input silently corrupts the intended entry.
- Fix: validate with `re.fullmatch(r"[A-Za-z0-9_.-]+", name)` and a token-charset check (reject or escape values containing `\n`); check `r.returncode` and raise on failure.

**[HIGH] `secret_set` on macOS silently loses the secret when `security` fails** - `lines 92-94, 129-131`
- What: `_mac_keychain("set", ...)` ignores `returncode`/stderr and unconditionally returns `True`; `secret_set` then writes `d[name] = "keychain"` to `secrets.dat` regardless of whether the Keychain write succeeded.
- Trigger: `security` CLI missing, Keychain locked, permission denied, or an interactive prompt (UI-forbidden contexts) — common in headless/SSH sessions.
- Impact: `secrets.dat` says the secret lives in the Keychain, but it was never stored. `secret_get` returns `""` forever after; the user's token is silently lost.
- Fix: capture the result, `raise OSError(...)` on non-zero returncode, and only record `"keychain"` in `secrets.dat` after a confirmed successful write.

**[MEDIUM] Prefix match scrubs unrelated variables in legacy migration** - `line 174`
- What: `s.startswith("REPLICATE_API_TOKEN")` also matches `REPLICATE_API_TOKEN_BACKUP=...`, `REPLICATE_API_TOKEN_OLD=...`, etc. Those lines get replaced with the "moved" comment and their values may overwrite the real token in the store.
- Trigger: a `providers.env` containing any variable whose name merely begins with `REPLICATE_API_TOKEN`.
- Impact: wrong token migrated (e.g. an old/backup token wins, since `secret_get` is re-checked per line but the first match claims the slot), and unrelated config lines are destroyed.
- Fix: match `s.startswith("REPLICATE_API_TOKEN=")` (or split on `=` first and compare the key exactly).

**[MEDIUM] Permission race: `secrets.dat` briefly world-readable before chmod** - `lines 75-80`
- What: the tmp file is created with default umask permissions, atomically renamed into place, and only *then* chmod'd to 0600. Between `os.replace` and `os.chmod` the file holding (obfuscated/DPAPI) secrets is readable per umask; on POSIX a umask of 022 makes it 0644.
- Trigger: any `secret_set` on a multi-user POSIX system (the `plain:` fallback path explicitly exists for such systems).
- Impact: other local users can read stored secrets during the window; also `os.makedirs` leaves `~/.asset-forge` itself at default perms.
- Fix: `os.chmod(tmp, 0o600)` before `os.replace`, and create the dir with `os.makedirs(_SECRETS_DIR, mode=0o700, exist_ok=True)` plus chmod it.

**[MEDIUM] Corrupt `secrets.dat` is silently treated as empty and then overwritten** - `lines 64-68, 132`
- What: `_secrets_load` swallows every exception (including JSONDecodeError from a truncated/corrupt file) and returns `{}`. The next `_secrets_save` then replaces the file, permanently destroying all stored secrets.
- Trigger: a crash mid-write, disk-full, or any I/O error leaving malformed JSON.
- Impact: total silent loss of all stored API tokens for every provider.
- Fix: distinguish "file missing" (return `{}`) from "parse failure" (raise or back up the corrupt file before overwriting).

**[LOW] Unlocked read-modify-write race on `secrets.dat`** - `lines 130, 132, 151-153`
- What: concurrent `secret_set`/`secret_clear` calls (e.g. two Blender operators/threads) each load, mutate, and save with no lock; last writer wins.
- Trigger: two secrets written concurrently.
- Impact: one secret silently dropped.
- Fix: hold a lockfile or in-process `threading.Lock` around load→save.

**[LOW] Unclosed file handle in legacy migration** - `line 167`
- What: `open(_LEGACY_ENV, ...).read()` never closes the file object (relies on refcounting); on non-CPython or with the file locked (Windows), the subsequent rewrite at line 187 can fail.
- Fix: use `with open(...) as f: lines = f.read().splitlines()`.

**[LOW] `token_present` can return stale `True` for up to `ttl` seconds** - `lines 113-123`
- What: the cache is only invalidated by this module's own set/clear; if the token is removed externally (another process editing `secrets.dat`, keychain cleared), the UI keeps reporting a token for up to 5s. Probably acceptable for a draw() cache, but the TTL default of 5s combined with env-var fallback (line 204: env changes are invisible until TTL expiry and never invalidate) should be documented.

## Missing safeguards
- Charset/format validation for `name` and `value` in `secret_set` before any Keychain/DPAPI interaction (the injection assumption at line 91 is enforced nowhere).
- Return-code checking on every `subprocess.run` to `security` (set/get/clear), with exceptions on failure instead of `return True`.
- A test that `secret_set` on a simulated failing `security` binary does **not** record `"keychain"` in `secrets.dat`.
- Tests for the legacy migration: exact-key matching, `secret_set` failure path (line 179-180 keeps the line — good, but untested), and idempotent re-run.
- A test asserting `secrets.dat` permissions are 0600 *immediately* after `os.replace`, not eventually.
- `secret_get` on macOS returns `""` indistinguishably for "no secret" vs "Keychain read failed" — callers can't tell a locked keychain from a missing token; consider raising or logging.