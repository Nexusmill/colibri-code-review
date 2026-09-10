# colibri review — scripts/register_schedule.ps1 (delta: PLAUSIBLE settled + rewritten)

- source: `scripts/register_schedule.ps1`
- reviewer: in-session (zai-coding-plan/GLM-5.3-Flash), colibri-review v0.2.0 bug mode
- sha256: b25365fe… (bytes on disk at review time)
- date: 2026-09-05
- mode: bug (delta against scripts__register_schedule.ps1__bug__06d1a585.md — prior sha 06d1a585)

## Fixed since last review

- **PLAUSIBLE (schtasks /TR quoting) — SETTLED: ACCEPTED by live probe, then MITIGATED.**
  Two probes registered tasks using the script's exact /TR construction (PowerShell 5.1):
  `schtasks /Create` rejected the mangled fragments outright ("Invalid argument/option"),
  so the script as written could never register the task. Mitigation: rewritten to the
  `Register-ScheduledTask` object model (`New-ScheduledTaskAction -Execute/-Argument/
  -WorkingDirectory`) — no string quoting involved. Live-verified on the real task name:
  registered, action object read back exact (Execute = venv python, Arguments = "-m birdcam
  run", WorkingDirectory = repo), then unregistered (arming the schedule stays the owner's
  explicit step).
- The former LOW (no existence check before /F overwrite) is superseded by the rewrite
  (-Force on the cmdlet, documented Remove line in the output).

## Remaining findings

None in this file. Probe scripts and their outputs live outside the repo (session temp).
