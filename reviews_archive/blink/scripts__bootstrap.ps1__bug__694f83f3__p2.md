# colibri review — scripts/bootstrap.ps1 (pass 2, security hunt)

- source: `scripts/bootstrap.ps1`
- reviewer: ZCode in-session (GLM-5.3), colibri-review v0.4.0, bug mode, security lens
- sha256: 694f83f352ecb2fa… (unchanged since pass 1, 2026-09-05)
- date: 2026-10-05 04:20
- context pack: prior review 694f83f3 (clean; live-proven at repo birth); requirements.txt /
  .env.example consumers; guarded-copy semantics.

## Verdict

new: 0. Re-verified this pass: both local config copies are Test-Path-guarded (never clobber
edited secrets), no secret values anywhere, Push-Location/Pop-Location balanced in try/finally,
$ErrorActionPreference Stop. The venv is created from the system launcher (py -3) — no network
fetch beyond pip itself.
