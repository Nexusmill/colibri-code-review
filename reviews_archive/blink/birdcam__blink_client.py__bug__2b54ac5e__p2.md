# colibri review — birdcam/blink_client.py (pass 2, security hunt)

- source: `birdcam/blink_client.py`
- reviewer: ZCode in-session (account:zai-individual-coding-plan/GLM-5.3), colibri-review v0.4.0, bug mode, security lens
- sha256: 2b54ac5eb284f56ebfb11310c529c6ce6d16c6ce3c626c0f1a1f81deba8ab511 (unchanged since pass 1)
- date: 2026-10-05 03:05
- context pack: pass-1 hy4 review (2b54ac5e, delta-clean) + its pass-0 predecessor (f48357c5: non-200
  media + auth edges, remediated 572703b); jCodemunch symbol map (23 symbols); git history (last
  change f04d93d 2026-09-19); blinkpy 0.25.9 INSTALLED SOURCE inspected (Blink.save →
  util.json_save(auth.login_attributes); login_attributes sets data["password"]; Auth.login →
  validate_login requires username+password before ANY grant; refresh_tokens → login(refresh=));
  live data/blink.token KEY NAMES ONLY read (no values): password IS a persisted key.

## Verdict

Shippable, and the prior passes' guards are intact. The security hunt found one real secret-hygiene
defect (plaintext password persisted in the token file — confirmed against both the library source
and the live file's key set) plus two minor edges. Biggest risk: data/blink.token is a second
plaintext copy of the master Blink credential on disk, in a file whose name suggests it is only a
token.

## Bugs & vulnerabilities (new findings only)

**[MEDIUM] blink.save() persists the plaintext Blink password into data/blink.token** - `line 130`
(`await blink.save(str(destination))`)
- What: blinkpy 0.25.9's `Blink.save()` writes `auth.login_attributes`, and that property explicitly
  re-adds `self.data["password"]` (and `username`) next to the tokens. Verified live: the current
  data/blink.token key set is `[account_id, client_id, device_id, expiration_date, expires_in,
  hardware_id, host, password, refresh_token, region_id, token, uid, user_id, username]`.
- Trigger: every `1-blink-login.bat` run (interactive login) — i.e. weekly under the 7-day token cycle.
- Impact: a second at-rest copy of the account's master password beyond `.env`, in a file named like
  a mere token — the kind of file an operator copies when moving machines or "saving the session",
  and the kind a backup tool sweeps up with `data/`. Under the current active account-attack, every
  unneeded plaintext copy is attack surface. (Not HIGH: single-user machine, gitignored, no remote;
  local-file access already implies .env access.)
- Fix (traced safe): after `blink.save()`, re-load the JSON, drop the `password` key, rewrite
  atomically; in `open_session`, re-inject credentials via `config`'s env-backed
  `blink_credentials()` into the loaded dict BEFORE `_make_auth` — required because blinkpy's
  `validate_login()` demands username+password even for the refresh_token grant, so a scrub without
  re-injection would break every hourly reopen. Net effect: password lives only in `.env`.

**[LOW] open_session crashes with a raw traceback on a corrupt token file** - `line 145`
(`json.loads(path.read_text(encoding="utf-8"))`)
- What: a truncated/hand-edited blink.token raises JSONDecodeError; the `except Exception` at 165
  closes the session and re-raises; cli surfaces a library traceback instead of the actionable
  "run 1-blink-login.bat" message the codebase standardizes on.
- Trigger: interrupted write, manual edit, disk-full during save.
- Impact: confusing failure for the least technical user (same UX class as the two LOWs fixed in
  572703b). CONFIRMED (path traced; trigger rare).
- Fix: wrap the load, raise `BlinkError("saved Blink session is unreadable - run 1-blink-login.bat")`.

**[LOW] delete_clip treats any <300 status as deletion confirmed, without reading the body** - `line 362`
- What: the v4 media/delete endpoint replies 200 with a JSON body; only `response.status < 300` is
  checked. A 200 body carrying `{"success": false}` (or sync:false) would mark the clip deleted
  while it survives in the cloud, and the pipeline's retry-on-False semantics never re-attempt it.
- Trigger: Blink returning an affirmative status with a non-success body (observed shape per the
  module docstring is `{"sync":true,"success":true}`; the failure shape is UNVERIFIED).
- Impact: a cloud copy of a clip lingers indefinitely (state dedupe prevents re-upload, so it is
  invisible locally). PLAUSIBLE — unverified because the server's failure-body behavior cannot be
  traced from source; keep the note, verify live before fixing.
- Fix (if confirmed): parse the JSON body when present and require `success` truthy for True.

## Missing safeguards

- None new beyond the above (prior passes' items stand as recorded).

Adversarial pass: the password-at-rest finding was traced end-to-end through installed blinkpy
bytes (save → login_attributes → data["password"]) AND the live file's key set (names only);
CONFIRMED. The corrupt-JSON crash path was traced through the except chain; CONFIRMED. The
delete-body semantics stayed PLAUSIBLE with the reason stated. Prior findings not restated.
