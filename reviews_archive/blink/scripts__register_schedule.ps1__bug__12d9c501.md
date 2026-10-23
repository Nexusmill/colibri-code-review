# colibri review — scripts/register_schedule.ps1 (delta + security hunt)

- source: `scripts/register_schedule.ps1`
- reviewer: ZCode in-session (GLM-5.3), colibri-review v0.4.0, bug mode, security lens
- sha256: 12d9c501f12b470cf0ea219ee0501d0e46f5dbd15e2ab8d1ee9b288a1a465b9d
- date: 2026-10-05 04:12
- context pack: prior review b25365fe (2026-09-05 — schtasks PLAUSIBLE settled via object-model
  rewrite, live-probed); delta 800e9c7 (hidden-VBS launch model + 6h ExecutionTimeLimit); live
  task facts per memory (hourly, HIDDEN, IgnoreNew); the PS 5.1 quoting trap memory.

## Verdict

Clean delta. The rewrite-to-object-model remediation holds; the only quoting left is the single
quoted -Argument, which Register-ScheduledTask passes verbatim (live-verified 2026-09-05).

## Bugs & vulnerabilities (new findings only)

None. Verified by trace:

- `New-ScheduledTaskAction -Execute wscript.exe -Argument "`"$vbs`"" -WorkingDirectory $repo`
  (line 31): one quoted path, no nested-quote parsing; the path derives from $PSScriptRoot, not
  user input.
- Remove path is guarded (18-24); -ErrorActionPreference Stop (12); settings match the live task
  (Once + 1h repetition, IgnoreNew, 6h limit — overlapping backlog runs cannot stack).
- No principal is set, so the task runs interactively as the registering user — intentional
  (alert popups from the reminder task need the interactive session) and consistent with the
  yt_login_reminder design.

Adversarial pass: the quoting claim re-checked against the documented 2026-09-05 live probe
(readback of the action object matched verbatim). Prior findings not restated.
