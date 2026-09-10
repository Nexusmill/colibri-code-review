# colibri review — scripts/register_schedule.ps1

- source: `scripts/register_schedule.ps1`
- reviewer: in-session (zai-coding-plan/GLM-5.3-Flash), colibri-review v0.2.0 bug mode
- sha256: 06d1a585… (17 lines, bytes on disk at review time)
- date: 2026-09-05
- context pack: schtasks argument-passing semantics from PowerShell 5.1 (the Windows-default shell for .ps1 double-click/RIA context); the pipeline's `cd /d` inside the task action; repo path contains no spaces today (`C:\Users\User\source\repos\Blink`) but usernames/drives routinely do.

## Verdict

Logic is right, but the one line that does the real work — the `schtasks /TR` argument — relies
on PowerShell 5.1 native-command quoting that is known-lossy with embedded quotes, and this
script is the only shipped automation that was never executed live. Treat as unverified until
run once.

## Bugs & vulnerabilities

**[MEDIUM] `/TR` action string may be mangled by PS 5.1 quoting, producing a task that never runs the pipeline** - `line 12` (`$action = "cmd.exe /c cd /d \`"$repo\`" && \`"$python\`" -m birdcam run"`) and `line 13` (`schtasks /Create ... /TR $action`)
- What: `$action` embeds literal `"` characters and spaces; Windows PowerShell 5.1 rebuilds the
  native command line for `schtasks` with its own (historically lossy) quoting rules, so the
  registered task's action can end up split at the first embedded space or missing the inner
  quotes — the task is CREATED (schtasks exits 0) but does nothing when it fires.
- Trigger: running the script on Windows PowerShell 5.1 (the default); paths with spaces make it
  worse.
- Impact: the hourly schedule silently exists but never stages/uploads — the exact silent-no-op
  class the gate's exec-bit lesson (EV-003) warns about, and the reason "verify the task fired"
  belongs in the checklist.
- Fix: prefer the native cmdlet — `Register-ScheduledTask -TaskName $task -Action
  (New-ScheduledTaskAction -Execute $python -Argument "-m birdcam run"
  -WorkingDirectory $repo) -Trigger (New-ScheduledTaskTrigger -Once (Get-Date) -RepetitionInterval
  (New-TimeSpan -Hours 1))` — no quoting games, sets WorkingDirectory properly (dropping the
  `cd /d` trick); or keep schtasks but verify with `schtasks /Query /TN $task /V` and a manual
  firing before trusting it.
- Note: PLAUSIBLE, not CONFIRMED — creating the task on the owner's machine to reproduce it is a
  system-state change not made during this review; the quoting behavior it rests on is a
  documented 5.1 pitfall.

## Missing safeguards

- No `-Verb RunAs`/least-privilege statement; the task inherits "run only when logged on" —
  acceptable for this use, worth stating in the README.
- No existence check before `/Create ... /F` (the `/F` overwrite is deliberate; a README note
  that re-running resets the schedule would prevent surprise).

Adversarial pass: the quoting-loss claim is a platform behavior, not traceable in repo bytes —
PLAUSIBLE with the unverified-because note above; everything else in the script traced clean.
