# colibri review — scripts/check_password.py (delta + security hunt)

- source: `scripts/check_password.py`
- reviewer: ZCode in-session (account:zai-individual-coding-plan/GLM-5.3), colibri-review v0.4.0, bug mode, security lens
- sha256: 3a6c979997b5d3ca08e16d35d986e8e29be52128811a3f7f7df4f3b1cff2df7ee
- date: 2026-10-05 03:35
- context pack: prior bug review 7ae74dfd (2026-09-05, 127 lines); launcher
  0b-check-passwords.bat; secrets covenant; blinkpy 0.25.9 login semantics (401/412/200/406,
  live-probed 2026-09-05); cross-ref tonight's blink_client.py finding on blink.save()
  persistence.

## Verdict

Clean delta. The prior LOW is fixed exactly as prescribed; the hidden-input/no-persistence posture
holds. One cross-file note tying this file into tonight's blink.token finding.

## Fixed since last review

- 2FA-rejection crash (prior LOW): the success branch now wraps `prompt_2fa()`/`start()` at
  101-117, prints the "rejected or expired code - run 0b again" guidance, closes the session, and
  returns 1 — verified in current bytes.

## Bugs & vulnerabilities (new findings only)

None unique to this file. Cross-file note: `await blink.save(str(destination))` at line 118 is a
SECOND write site for the blink.token password-persistence MEDIUM recorded in
birdcam__blink_client.py__bug__2b54ac5e__p2.md (blinkpy's login_attributes re-adds the plaintext
password). The remediation must cover both sites (or land in blink_client.login_interactive and
have this script reuse it) — tracked there, not double-counted here.

## Missing safeguards

- Still no pause between consecutive wrong-password attempts (prior safeguard, unchanged) — five
  rapid tries against the login endpoint could contribute to Blink-side lockout; a 2-3 s sleep
  between attempts would be polite hygiene.

Adversarial pass: fix verification re-read lines 97-123; the 406/401 loop paths re-traced for
session hygiene (close at 92, 116, 120, 123 on every branch — no leak path found).
