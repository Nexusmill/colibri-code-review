# colibri review — scripts/yt_login_reminder.ps1 (bug)

- Source: scripts/yt_login_reminder.ps1
- Reviewer: ZCode in-session (GLM-5.3)
- sha256: 39d665afe1719a6cbee0c6027d31ecbd6583ef9c126378abe59777bd52ae2f27
- Date: 2026-09-18
- Mode: bug
- Context pack: born of the 2026-09-11→18 invalid_grant outage (see
  birdcam__youtube_client.py__debug__1052fa7d.md); sole caller is Task Scheduler task
  "BirdCam YouTube Login Reminder" (daily 10:00, StartWhenAvailable, IgnoreNew, 1h limit,
  interactive user); reads data/hourly_run.log — appended hourly by run_hourly.cmd via
  run_hourly_hidden.vbs (VBS trims log >5MB); success marker "uploaded as" is
  pipeline.py::upload's print; alert pattern matches the owner's GLOBAL_MEMORY alert
  command (beep 880/250 + 1175/400 + WScript Popup).

## Verdict

Shippable. Read-only, one decision function, no secrets, no state mutation; failure modes
degrade to silence rather than false alarms. Biggest (accepted) risk: silent death if the
repo moves or both log markers change wording — both are single-machine constants also
baked into the live hourly task.

## Bugs & vulnerabilities

**[LOW] Hardcoded absolute repo path** - `line 13`
- What: `$root = 'C:\Users\User\source\repos\Blink'` (same convention as the live hourly
  task's absolute script path).
- Trigger / Impact: moving/renaming the repo makes the script exit silently forever
  (`Test-Path` fails) — reminders stop with no error surfaced.
- Fix if it ever matters: derive from $PSScriptRoot\.. — not done now to keep parity with
  the registered-task pattern in this repo.

**[LOW] Log-marker string coupling** - `lines 41-42`
- What: relies on the exact strings `invalid_grant` (Google's stable OAuth error code)
  and `uploaded as` (pipeline.py print text).
- Trigger / Impact: a reworded pipeline success line with the failure marker also gone
  would read as healthy ($lastFailure = -1). `invalid_grant` is Google's documented,
  long-stable error code, so the failure side is solid; only the success side is
  cosmetic-coupled, and it only matters for the rare "recovered after failure within the
  600-line window" ordering check.
- Fix: none needed at this scale; revisit if pipeline print wording changes.

**[LOW] Stop-preference silent exit** - `line 10`
- What: `$ErrorActionPreference = 'Stop'` means a transient read error aborts with no
  popup; the task exits nonzero and retries the next day.
- Impact: worst case one missed daily check. Acceptable for a belt-and-suspenders nudge;
  the Monday trigger gives a second, independent chance each week.

## Missing safeguards

- No "reminder fatigue" guard if the user leaves the sign-in dead for days: the urgent
  popup repeats daily by design (intended — posting is stopped). Considered and kept.
- No written state/flag file; deliberate — statelessness keeps it read-only and safe
  alongside the pipeline's atomic state.json.
