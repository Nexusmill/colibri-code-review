# colibri review — scripts/bootstrap.ps1

- source: `scripts/bootstrap.ps1`
- reviewer: in-session (zai-coding-plan/GLM-5.3-Flash), colibri-review v0.2.0 bug mode
- sha256: 694f83f3… (25 lines, bytes on disk at review time)
- date: 2026-09-05
- context pack: executed live on this machine at repo birth (venv created, deps installed, config copies made); README references it as step 1.

## Verdict

Already proven on this machine — it is the script that created `.venv` and the local config
copies. No defects.

## Bugs & vulnerabilities

None. Candidates examined and refuted:

- *Re-run clobbers user edits to config.yaml/.env* — refuted: both copies are guarded by
  `Test-Path` + `Copy-Item` only when absent.
- *`py -3` launcher assumption* — refuted for this machine (py 3.13/3.11 both installed); noted
  as a portability nit for other machines (`python -m venv` fallback would be friendlier).

## Missing safeguards

- No pip failure trap: if `pip install` fails (offline), the script continues to the "Done"
  banner (ErrorActionPreference does not catch native exit codes). A `if ($LASTEXITCODE -ne 0)
  { exit $LASTEXITCODE }` after the install would keep the happy banner honest.

Adversarial pass: refutations traced against the live bytes and the machine's installed
launchers; the native-exit-code gap is CONFIRMED as a safeguard-class gap (no wrong behavior on
the happy path this machine exercised).
