Source: Spector/build.py
Reviewer: claude-sonnet-5 (in-session)
sha256: 92378d811572c37131bc1aec5235975971f5b03ea540ed84a4658faec8e07e77
Date: 2026-08-07
Mode: bug (FIRST review - never in .colibri_reviews/_manifest.json)
Context pack: full 38-line file read; compared against the twin build scripts for the other two
products (asset-forge/build.py, asset-forge-user/build.py, PatternSkin has no equivalent) which
were already colibri-reviewed, to check whether this file shares any of their known patterns/
findings; checked .github/workflows/build-spector.yml (referenced by CLAUDE.md as this file's
CI caller) exists.

## Verdict
Shippable. A short, single-purpose PyInstaller wrapper run by CI/developers only - never
reachable from any customer-facing code path, no untrusted input.

## Bugs & vulnerabilities
None. `run()` uses `subprocess.check_call(list(a), cwd=HERE)` with a fixed, hardcoded argument
list built entirely from constants and `sys.executable`/`HERE` - no shell=True, no string
interpolation of external input, nothing attacker- or even user-influenced reaches the
subprocess call.

## Missing safeguards
- None worth flagging: this is a developer/CI-only build script, not shipped code, with a
  trivial and fully-static command surface.
