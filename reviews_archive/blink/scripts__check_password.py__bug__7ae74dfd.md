# colibri review — scripts/check_password.py

- source: `scripts/check_password.py`
- reviewer: in-session (zai-coding-plan/GLM-5.3-Flash), colibri-review v0.2.0 bug mode
- sha256: 7ae74dfd… (127 lines, bytes on disk at review time)
- date: 2026-09-05
- context pack: blinkpy 0.25.9 login semantics verified live this session (401 wrong / 412 correct+2FA / 406 client rejection); launcher 0b-check-passwords.bat; secrets covenant (no password logging/storage — verified: getpass, nothing written).

## Verdict

Does its one job with the right security posture (hidden input, no persistence, verdicts from
Blink's own server). One rough edge: a rejected 2FA code crashes with a traceback and leaves the
HTTP session open.

## Bugs & vulnerabilities

**[LOW] Wrong/expired 2FA code crashes with traceback and leaks an open session** - the success branch (`status in (200, 412)`)
- What: after a correct password, `blink.prompt_2fa()` calls `input()` then
  `auth.complete_2fa_login(code)`; a rejected/expired code raises out of the nested call with no
  handling — the `finally`-less success path skips `session.close()`, and the user sees a
  blinkpy traceback instead of "try the next code".
- Trigger: typo in the 2FA code, or entering it after it expired (Blink codes are short-lived).
- Impact: ugly crash after the moment of maximum user investment; one wasted aiohttp session
  (process exits anyway, so the leak is bounded — the UX is the real cost).
- Fix: wrap the prompt call: on failure print "code rejected - run 0b again and re-enter the
  password", close the session, return non-zero.

## Missing safeguards

- No cap on identical consecutive wrong-password attempts against Blink's login endpoint — five
  tries is polite, but a user hammering it could trip Blink-side lockout; a short sleep between
  attempts would be polite hygiene.
- The 406 verdict text is the correct and verified message (VPN/proxy/API-change); it correctly
  does NOT blame the password — matches the live probe evidence from this session.

Adversarial pass: the unhandled-code path traced `prompt_2fa → send_2fa_code →
complete_2fa_login raise` with no try/except between; CONFIRMED. Password-storage covenant
re-verified by inspection: getpass only, no file writes anywhere in the module; CONFIRMED clean.
