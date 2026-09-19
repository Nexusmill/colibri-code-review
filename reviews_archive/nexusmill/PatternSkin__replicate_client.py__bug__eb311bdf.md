# Colibri Review - bug (DELTA) - PatternSkin/replicate_client.py

- **Source path:** `PatternSkin/replicate_client.py`
- **Reviewer:** claude-fable-5-1 (in-session), Colibri G37 protocol, campaign item 1 (product cores), rank 10
- **sha256 reviewed:** `eb311bdf798d22bebeca541aad113ef32e6a2ee13269e0e7bd27d2cc3fa35f76` (sha8 `eb311bdf`)
- **Date:** 2026-09-10 · **Mode:** bug, stale-file DELTA against `43c9db79` (2026-07-24 round 2)
- **Delta reviewed:** 8 commits / 299 diff lines: cf6c2635 + 0585cba0 (RC-1 one budget, `ReplicateMaybeBilled`, cancel on budget exhaustion), 1bbfa8bf (flux-dev -> prunaai/flux-fast), 3f6bb667 (klein + `_model_key_for_slug`), 60bbde28 (GLM-POLISH non-object body, poll clamp), 69d0c2e2 (GROK-RC2 download retry + cancel fallback), 83d109f8 (GLM-R2 `HTTPException`), d82f8de0 (UA injection) - every hunk read.
- **Context pack:** the prior review record(s) for the file, `docs/remediation_manifest.json` rows from 2026-07-24 on, `docs/deferred_manifest.json` rows naming the file, `_hunt_plan.json` + `_refuted_ledger.json` loaded; jCodemunch `get_symbol_source` on the call sites each finding depended on.

## Fixed since last review
- Every remediation row dated after the base review was verified present at the bytes (they are the delta).

## Verdict
Clean at the delta. Every post-send failure class (5xx, read timeout, post-send drop, unreadable or non-object 2xx body, `HTTPException`) raises the billed framing and is never re-POSTed; 429 and pre-send network failures retry only inside the one deadline; the poll clamps its socket timeout to the remaining budget and a budget-exhausted run is cancelled through `urls.cancel` then the documented endpoint; the output download retries twice, unlinks partial files and never retries the size-cap refusal.

## Bugs & vulnerabilities
None confirmed at the delta.

---

# FULL re-audit 2026-09-10 (appended - the record above predates the adversarial gate and is kept as history, not as baseline)

# Colibri Review - bug (FULL re-audit) - PatternSkin/replicate_client.py

- **Source path:** `PatternSkin/replicate_client.py`
- **Reviewer:** claude-fable-5-1 (fork of the lead session), Colibri G37 protocol, campaign item 1 (product cores), rank 10
- **sha256 reviewed:** `eb311bdf798d22bebeca541aad113ef32e6a2ee13269e0e7bd27d2cc3fa35f76` (sha8 `eb311bdf`) - the PRE-fix bytes
- **Date:** 2026-09-10 · **Mode:** bug, FULL review of the current bytes (owner ruling 2026-09-10: the prior audits - r1 `f143644d`, r2 `43c9db79` 07-24, the 08-15/08-20/08-26/08-27 GLM/Grok/SAM3 rounds - predate the adversarial gate and are untrusted; no delta)
- **Context pack:** every line read (333); importers `__init__.py` (`_retry_transient` 3603-3628 and its substring classifier, `_gen_texture_to_library` 3631-3669 synchronous on the main thread, the provider-key dialog 3474-3517, the library generator 5265-5359), `filmstrip.py` (dress modal: `_replicate_generate` on a daemon thread 359-364); the stdlib path re-read at the installed interpreter (`http.client.HTTPConnection.putheader` / `_send_request`, `urllib.request.AbstractHTTPHandler.do_open`, `OpenerDirector.open`); remediation/deferred rows RC-1, GROK-RC2, GLM-POLISH, GLM-R2, PS-SAM3-EMPTYZIP loaded as CLAIMS and re-verified at the bytes; the prior records read as claims.

## Verdict
Shippable after one small fix. The money-safety ladder holds at the bytes: one deadline for create + poll, 429 and pre-send (refused/DNS) failures are the only re-POSTs, every post-send class (5xx, read timeout, post-send drop, unreadable/non-object 2xx, `HTTPException`) is the billed framing, the poll clamps to the budget and a budget-exhausted run is cancelled via `urls.cancel` then the documented endpoint, the free output GET retries and never leaves a partial file, the no-redirect opener keeps the bearer on `api.replicate.com`, every request carries the add-on UA. One CONFIRMED misframing: a pre-send failure reported as "created and billed".

## Bugs & vulnerabilities

**[LOW] A token that cannot be sent in a header is reported as "the prediction was created and billed" (nothing was sent), and the validate path echoes such a key** - `_replicate_generate` `line 243-245`; `_validate_provider_key` `line 78-79`
- What: `http.client.putheader` encodes every header value as latin-1 and rejects CR/LF, raising `ValueError` (`UnicodeEncodeError` is a `ValueError`) BEFORE `endheaders`/`connect` - nothing leaves the machine, and `do_open` re-wraps only `OSError`. The create loop's `except ValueError` was written for a malformed 2xx body but wraps the whole attempt, so the pre-send failure surfaces as `ReplicateMaybeBilled("... unreadable response (the prediction was created and billed)")`. In `_validate_provider_key` the same failure lands in `except Exception` as `"network error (Invalid header value b'Bearer <key>')"` - http.client quotes the value, i.e. the key, into the operator report and the console.
- Trigger: a stored token with a non-latin-1 character (a curly quote or zero-width space pasted into `providers.env` - the migration path never validates - or the `REPLICATE_API_TOKEN` env var); the echo needs a CR/LF inside the key, reachable only through the env var (the dialog `strip()`s and the env file is line-split), so that half is a hygiene closure rather than a live leak.
- Impact: every Generate click tells the user money was spent and to "check replicate.com before retrying" for a key that can never work; `_retry_transient` (correctly) refuses to retry the billed framing, so the user never learns the key is malformed.
- Fix: `_token_sendable()` (latin-1 encodable, no CR/LF) checked at the top of `_replicate_generate` (before the loop: `RuntimeError` "... nothing was sent, nothing was billed") and in `_validate_provider_key` (`(False, "key contains characters that cannot be sent ...")` - never echoing the value). Checked against every call site: `_retry_transient` sees "billed" and does not re-call (correct - retrying cannot help); the filmstrip thread stores `str(e)` for its skipped list; the classic path wraps it as "Generation failed: ..." (the last 160 chars keep the "nothing was billed" tail).
- Verification: CONFIRMED by the stdlib source (putheader precedes endheaders; do_open wraps OSError only) and by reproducer `probe_ps_replicate_client_1.py` (socket.create_connection replaced by a raiser, so any connect fails the probe): RED on the current bytes (both checks: billed framing; key echoed as `b'Bearer r8_probe\r000'`), GREEN on a scratch copy with the fix.

## Missing safeguards (not fixed, no defect traced)
- A connect-phase socket timeout is indistinguishable from a read timeout and is (deliberately) treated as maybe-billed; conservative, but a user behind a dead network gets the billed wording. Recorded design since RC r2.
- Killing Blender mid-generation abandons a running, billing prediction; `_replicate_cancel` exists (RC-1) but no caller wires it to an abort path (the RC-1 residual, a feature).
- The classic Generate path (`_gen_texture_to_library`) runs this client synchronously on Blender's main thread with a 180 s budget and `_retry_transient` x3 - up to ~9 min of frozen UI on repeated nothing-billed timeouts (caller-side; the filmstrip path threads it).
- `_validate_provider_key` accepts 200/201 only; a 204 would read "unexpected response" (Replicate returns 200).
- A "failed" prediction whose `error` text contains "timed out"/"connection" is re-called by `_retry_transient` (a new prediction; failed runs on the official models carry no output charge, so no double-bill of a success).

## Adversarial verification pass (refuted claims - one line each)
- "`_rc_urlopen` on a bare URL string skips the UA and hits the Cloudflare 1010 block" - refuted: every call site passes a `Request`, including the output download (`Request(out_url)`).
- "the no-redirect handler does not replace the default one" - refuted: `build_opener` swaps in a subclass of a default handler; `redirect_request -> None` makes 30x raise `HTTPError`.
- "a poll `HTTPError` (404/401) spins for the whole budget" - true but not a defect: the GET is idempotent, the budget bounds it and the exhaustion path cancels and reports.
- "the size-cap `RuntimeError` is retried by the download loop" - refuted: `isinstance(_dl_err, RuntimeError)` re-raises before the retry.
- "the output `open(out_path, 'wb')` races the unlink on Windows" - refuted: the `with` exits (file closed) before `unlink` runs in the handler.
- "`except OSError` shadows `URLError`" - refuted: `HTTPError`/`URLError` clauses precede it; `RemoteDisconnected` lands in `OSError` by design (GLM-R2 note at 254-255).
- "`_replicate_cancel` sends the bearer off-host through `urls.cancel`" - refuted: `_rc_check_host(url, (_API_HOST,))` guards each candidate.

## Remediation postscript (same session)
The fixes were applied after this review hashed the bytes above; the file is now `596eccc23761285da850584a6d3a36e48bf117e22212c416c3a99b4a76dd4e1d`. Rows PS-RC-TOKEN-SENDABLE in `docs/remediation_manifest.json`, same commit.

