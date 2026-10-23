# colibri bug review — tests/test_part_export.py

- source: tests/test_part_export.py · model: GLM-5.3-Flash (in-session)
- sha256: c602c8d18a (full sha in manifest row) · reviewed_at: 2026-10-13 · mode: bug
- context pack: live execution (PASS, exit 0); the fmt-repurposing scar note (2026-07-25) read — the test that silently asserted against the wrong writer now drives the explicit 3MF_FACECOLOR/3MF_OBJECTS flavors.

## Verdict
Clean — no defects. Exact-byte assertions (STL size = 80+4+50×2), round-trip XML parsing, per-triangle p1 colour checks, TemporaryDirectory with atexit cleanup (the fixed leak).

## Bugs & vulnerabilities
None CONFIRMED.

## Missing safeguards
- Module-level execution (no function wrappers): a pytest collection would run the whole battery at import — same latent class as heightmap; subprocess-driven today.
