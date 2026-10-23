# Colibri review — src/jcodemunch_mcp/service_installer.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\service_installer.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summary, artifacts reaudit/jcm/)
- sha256: `8a09ffb687fd9a3647ca60eab5acccfeb4cf75bad7e8537b706862ec470d0e91` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: the file end to end (259 lines: systemd unit template 56-72 with `{env_lines}` interpolated raw, `_systemd_env_lines` 75-81, `_install_systemd` 84-103 writing with default permissions, launchd template 132-149, `_launchd_env_xml` 152-157 through `_xml_escape` 287, Task Scheduler path 200-233 which forwards no environment); `credentials.py` `CREDENTIAL_ENV_VARS` 63-74 (the canonical credential list, includes `JCODEMUNCH_HTTP_TOKEN`) and `resolve_credentials_in_env` (replaces `keyring:` references in `os.environ` with the keyring's PLAINTEXT before the server runs - so the installer sees resolved secrets); `org/license.py` 91 (`JCODEMUNCH_LICENSE_KEY`, not in the credentials list); no `tests/test_service_installer*.py` existed; both RED probes re-run on these bytes (probe 1: 4/4 FAIL, probe 2: 2/2 FAIL).

## Verdict
The installer copied the process environment into a plaintext login-service file, secrets and all, with no escaping. Both findings confirmed and fixed; the file is now written 0600 as well.

## Bugs & vulnerabilities
**[HIGH] credentials forwarded verbatim into the systemd unit / launchd plist — CONFIRMED — FIXED** - `line 75-81, 152-157`
- What: every `JCODEMUNCH_*` variable was forwarded, and by the time the installer runs `resolve_credentials_in_env` has already turned a `keyring:` reference into the plaintext token - so `JCODEMUNCH_HTTP_TOKEN` (and `JCODEMUNCH_LICENSE_KEY`) landed in `~/.config/systemd/user/*.service` / `~/Library/LaunchAgents/*.plist` at default permissions, defeating the keyring design. Probe 1 reproduced both values in both files.
- Fix: one `_forwarded_env()` feeds both writers and skips `_is_secret_env(key)`: anything in `credentials.CREDENTIAL_ENV_VARS` (the source of truth - not a second hand-kept list), `JCODEMUNCH_LICENSE_KEY` (a secret the credentials module does not list), and defence in depth any `JCODEMUNCH_*` name ending `_TOKEN/_KEY/_SECRET/_PASSWORD/_PASS` so a credential surface added without updating the list is still kept out. The watcher does not serve HTTP and reads the license through config/keyring at runtime, so it loses nothing.

**[HIGH] an unescaped value with a newline injected directives into the systemd unit — CONFIRMED — FIXED** - `line 80`
- What: `Environment={key}={val}` with the raw value - a value containing `\n[Service]\nExecStart=/bin/evil` wrote those lines into the unit verbatim (probe 2). Whitespace values were also unquoted (broken units).
- Fix: every assignment is `Environment="KEY=value"` with backslashes and quotes escaped inside the quotes and `%` doubled (systemd expands `%` specifiers); a value with a line break cannot be represented on one line and is dropped with a warning, never mangled. launchd was already XML-escaped (a newline inside `<string>` is data); it now shares the same forwarding filter.

## Missing safeguards (fixed alongside)
- Neither writer restricted the generated file: `_restrict()` chmods the unit and the plist to 0600, best-effort. Task Scheduler (Windows) forwards no environment at all - untouched.

## Adversarial verification (Phase 3)
- The battery runs the REAL `_install_systemd` / `_install_launchd` against a scratch home with `Path.home`, `shutil.which` and `subprocess.run` stubbed, and inspects the files they wrote: token and license absent (built at runtime, never literals); every name in `CREDENTIAL_ENV_VARS` plus a made-up `JCODEMUNCH_FUTURE_SECRET` absent; the newline payload yields no `ExecStart` and exactly one `[Service]`; spaces, quotes, `%` and backslashes come out as systemd expects; the 0600 check is POSIX-only (skipped on this Windows box - probe 1's own mode check is likewise gated).
- The five service/installer/credential/cli test files: 46 passed, 1 skipped on the new bytes.

## Remediation postscript (same commit)
The fixes were applied after this review hashed the bytes above; the file is now `e9acc338268167ae44f77e96187b4e2b1def45d78cc1b80aae4591ce727e684d`. TDD: `tests/test_service_installer_reaudit.py` (5 tests) - 4 RED on the old bytes (the POSIX-mode test skipped here), GREEN after; both probes ALL PASS.
