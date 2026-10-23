# colibri bug review — tests/test_heightmap.py

- source: tests/test_heightmap.py · model: GLM-5.3-Flash (in-session)
- sha256: f4a5bda5dd (full sha in manifest row) · reviewed_at: 2026-10-13 · mode: bug
- context pack: live execution (exit 0); the bpy-blocking idiom traced (sys.modules["bpy"]=None → heightmap's guarded import → bpy=None, asserted l.21 — the fixed tautology row now a scar comment l.13).

## Verdict
Clean — no defects. Compact and exact (exact-score thresholds, idempotence row, constant-tile zero).

## Bugs & vulnerabilities
None CONFIRMED.

## Missing safeguards
- `line 44`: `sys.exit(1 if n_fail else 0)` at MODULE scope — a pytest collection of this file would hit SystemExit (the runner drives it as a subprocess, so latent only; the math file shows the function-wrapped alternative).
