# colibri review — birdcam/blink_client.py

- source: `birdcam/blink_client.py`
- reviewer: in-session (zai-coding-plan/GLM-5.3-Flash), colibri-review v0.2.0 bug mode
- sha256: f48357c5… (bytes on disk at review time, 320 lines)
- date: 2026-09-05
- context pack: full repo (all call sites: pipeline.stage/clean, cli login/run, compiler reuses sanitize_component; blinkpy 0.25.9 source in .venv consulted for query/do_http_get/validate_response behavior; README + gate doctrine invariants; live dry-run evidence 810 clips / 49 person-skips)

## Verdict

Shippable for its role, with one real robustness hole in the download path and two rough
auth-failure edges. Biggest risk: a non-200 media response is silently written to disk as a
".mp4" and enters the compilation pipeline as garbage bytes.

## Bugs & vulnerabilities

**[MEDIUM] Non-200 media response is written to disk as a video** - `line 280` (`if response is None`)
- What: `download_clip` only guards `response is None`. blinkpy's `api.http_get` → `Auth.query`
  returns the raw ClientResponse without raising on HTTP status (verified against the installed
  blinkpy source: `validate_response` returns the response object for non-JSON calls). A 403/404/5xx
  or throttled-HTML body is then hashed and written as a valid-looking `.mp4`.
- Trigger: Blink throttles a media fetch, a clip URL expires between listing and download, or the
  endpoint serves an error page.
- Impact: corrupt "clips" enter the archive and poison a day's compilation — `build_compilation`
  then fails (CompileError → that day is SKIPped every run) or, worse, a garbage segment rides
  into the uploaded video. The sha256 protects integrity-after-download, not correctness-of-download.
- Fix: `if response.status != 200: raise BlinkError(f"download failed for clip {clip.clip_id} (HTTP {response.status})")` before reading the body.

**[LOW] Expired-token 2FA resurfacing as a raw traceback** - `line 147` (`started = await blink.start()`)
- What: `open_session` converts "start returned False" into a friendly BlinkError, but if Blink
  demands fresh 2FA for the saved token, blinkpy re-raises `BlinkTwoFARequiredError` out of
  `start()`; nothing catches it here, and `cli.main` re-raises unknown exceptions.
- Trigger: Blink invalidates the stored session server-side.
- Impact: the scheduled run crashes with a library traceback instead of the actionable
  "run 1-blink-login" message the codebase already has.
- Fix: catch the 2FA error type by name around `start()` and raise `BlinkError("Blink session expired and needs re-verification - run 1-blink-login.bat")`.

**[LOW] login_interactive trusts prompt_2fa without a saved-session sanity check** - `line 109`
- What: after the interactive 2FA path there is no `started`-style verification before
  `blink.save()`; a `prompt_2fa()` failure (wrong code raises from blinkpy) propagates as a raw
  traceback and the session file is left untouched (correct) but the operator gets no guidance.
- Trigger: typo'd 2FA code, or the code expiring before entry.
- Impact: confusing failure on the least technical user's most likely stumble.
- Fix: wrap the prompt path, translate failures into `BlinkError("code rejected or expired - run login again")`.

## Missing safeguards

- No retry/backoff around a single failed clip download (one throttled clip aborts the whole
  stage run; remaining clips wait for the next run — safe but slow at 900-clip backlog scale).
- `_parse_created_at` returns None on unparseable timestamps and silently drops the clip; a
  format change by Blink would masquerade as "no new clips" rather than error. Consider a
  warn-and-count.
- `sanitize_component` collisions (two distinct clip ids differing only in non-alphanumerics)
  would collide in filenames; ids are numeric today, so accepted.

Adversarial pass: the non-200 finding was re-traced through `blinkpy.api.http_get` →
`Auth.query` → `validate_response` against the installed 0.25.9 bytes (no raise_for_status on
this path); CONFIRMED. The 2FA-propagation paths were traced through `cli.main`'s except chain;
CONFIRMED.
