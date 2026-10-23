# colibri review — scripts/run_hourly_hidden.vbs (first review, security hunt)

- source: `scripts/run_hourly_hidden.vbs`
- reviewer: ZCode in-session (GLM-5.3), colibri-review v0.4.0, bug mode, security lens
- sha256: 79ba46935b2b44efec5980cba3143346416621f28db27b46b1db97768b8db9bd
- date: 2026-10-05 04:12
- context pack: never reviewed (born 800e9c7); invoked by the scheduled task as
  `wscript.exe "<this file>"` (register_schedule.ps1:31); launches run_hourly.cmd hidden and waits
  (keeping the task instance alive for -MultipleInstances IgnoreNew); log-trim contract documented
  in memory and the yt_login_reminder review.

## Verdict

Clean. new: 0.

## Bugs & vulnerabilities (new findings only)

None. Verified by trace:

- Path derivation is self-anchored (ScriptFullName parent-of-parent → repo root); wrapper
  existence checked with a loud MsgBox + Quit 1 before anything runs (20-23).
- `shell.Run "cmd /c """ & wrapper & """", 0, True` — exactly one quoted path after cmd /c, no
  nested-quote parsing traps (the comment's own claim, re-verified); window style 0 + wait=True
  give the hidden-and-serialized semantics the task settings rely on.
- `On Error Resume Next` is scoped to the log-trim block only (28-32) and reset immediately — a
  trim failure cannot mask a downstream error; the >5 MB delete keeps the log bounded as
  documented.
- Nothing in the file expands remote or user-supplied data; all strings are repo-relative
  constants.
