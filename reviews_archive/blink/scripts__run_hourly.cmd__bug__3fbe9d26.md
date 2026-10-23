# colibri review — scripts/run_hourly.cmd (first review, security hunt)

- source: `scripts/run_hourly.cmd`
- reviewer: ZCode in-session (GLM-5.3), colibri-review v0.4.0, bug mode, security lens
- sha256: 3fbe9d268d2386699db54af96733f37f4746cefbdbdb72f1a1d017589a5f6a13
- date: 2026-10-05 04:12
- context pack: never reviewed (born 800e9c7 2026-09-09); parent chain: Task Scheduler → wscript
  run_hourly_hidden.vbs → this file; sole consumer of the venv python; log read by
  5-status.bat + yt_login_reminder.ps1 (both reviewed); %~dp0 anchoring convention shared with the
  launcher .bats.

## Verdict

Six lines, correct by construction. new: 0 with one INFO note.

## Bugs & vulnerabilities (new findings only)

None. Verified: `cd /d "%~dp0.."` anchors to the repo root from the script's own location (not
CWD); the venv python is a repo-relative quoted path; stdout+stderr redirect into the quoted log
path. No environment expansion of remote data, no shell metacharacter surface beyond the fixed
command line.

## Missing safeguards

- If data/ were ever deleted while the scheduled task fires, the `>>` append fails ("path not
  found") and that hour's output is lost — though the python run itself still executes (its own
  state writes re-create data/). A `if not exist data mkdir data` line would make the log
  self-healing. [INFO]
