# colibri bug review — tests/test_perfection_keyvault.py

- source: tests/test_perfection_keyvault.py · model: GLM-5.3-Flash (in-session)
- sha256: 617d78e1e0 (full sha in manifest row) · reviewed_at: 2026-10-13 · mode: bug
- context pack: live execution (PASS, exit 0); env-isolation design verified (throwaway NEXUSMILL_VAULT_HOME before module import); the _cli set/restore sites enumerated (l.80/81/113/139/159); the W3 mapping matrix traced.

## Verdict
Shippable — the strongest isolation design in the suite (temp vault home, real cryptography lifecycle, vendored-drift guard). One restore-error and two dead-code scraps.

## Bugs & vulnerabilities

**[LOW] t2_pins' finally destroys `_cli` instead of restoring it** - `lines 139, 158-159`
- Verbatim: `kv._cli = lambda: None   # simulate the no-KeePassXC customer` ... `finally: kv._cli = None`
- What: W3 saves/restores `real_cli` correctly (l.80/113); t2_pins patches `_cli` at 139 but its finally writes `None` — not the original resolver.
- Trigger: any row appended after t2_pins that resolves the real CLI path.
- Broken behavior: none today (nothing consumes `_cli` afterward); latent confusion for future rows.
- Fix: save `real_cli` in t2_pins and restore it.
- Status: **CONFIRMED** (sites enumerated).

## Missing safeguards
- `line 120`: W4's `.replace("importable", "importable")` is an identity no-op (editing remnant) and the double-space collapse is cosmetic — simplify to the plain `in` checks.
- W1 patches `kv.subprocess.run` — the shared stdlib module attribute (global for the process), restored in finally: acceptable in a standalone battery, noted.
