# colibri review — birdcam/youtube_client.py (delta + security hunt)

- source: `birdcam/youtube_client.py`
- reviewer: ZCode in-session (account:zai-individual-coding-plan/GLM-5.3), colibri-review v0.4.0, bug mode, security lens
- sha256: 8c0558e550178e0a56ff77c0ebaf9742b81e787079961ff74aeb00c0da9962fc
- date: 2026-10-05 03:10
- context pack: prior bug review 8e230984 (2026-09-05, 128 lines) + debug review 1052fa7d
  (invalid_grant outage 2026-09-18) + remediation_manifest 2026-09-23 scope-safety entry; jCodemunch
  outline (16 symbols); git history 88eb139→40691ea (stuck-upload adoption, retry command, takedown
  path, _token_scopes); google-auth/oauth semantics per installed libs.

## Verdict

Shippable. The delta since 8e230984 is a net hardening: retries adopted, scope-safety implemented
exactly as the remediation entry prescribes, and the takedown path maps errors to actionable
messages. One new LOW in the takedown error mapping; two prior safeguards remain open.

## Fixed since last review

- Retry/backoff (prior LOW): `next_chunk(num_retries=3)` at line 123 and `_poll_once` 3-attempt
  backoff (166-180) — fixed in 88eb139, verified in current bytes.
- Scope check after token load (prior safeguard): `_token_scopes()` (37-46) + `LEGACY_TOKEN_SCOPES`
  load only what the grant recorded — fixed per remediation 2026-09-23, verified.

## Bugs & vulnerabilities (new findings only)

**[LOW] delete_video maps ANY 403 to "token lacks delete permission", including quota errors** - `line 200`
(`if "insufficientPermissions" in text or " 403" in text`)
- What: googleapiclient HttpError strings contain the numeric status, so a 403 quotaExceeded (or any
  future non-permission 403) on videos.delete is reported as "the saved YouTube token lacks the
  delete permission. Run 2-youtube-login once...".
- Trigger: Data API delete-quota exhaustion or another 403 class on the takedown path.
- Impact: misdiagnosis — the operator re-logs-in (harmless but pointless) and may not connect the
  failure to quota; the fallback advice (remove in Studio) still works, so the takedown itself is
  not blocked.
- Fix: require the reason token too (`"insufficientPermissions" in text` or parse
  `err.resp.status == 403 and "insufficientPermissions" in err.content`), and let other 403 reasons
  fall through to the generic `deleting ... failed` message with the raw error.
- CONFIRMED (branch trace; frequency low).

## Missing safeguards (still open from prior review, unchanged)

- Token file writes remain non-atomic (`write_text` at 69, 85) — crash mid-write corrupts
  data/youtube.token; recovery is a documented re-login. Same class as the blink.token LOW recorded
  this session; an atomic tmp→replace write (state.py's standard) would close both.
- `wait_processing` reads only `processingDetails.processingStatus`; on failure states it does not
  surface `status.uploadStatus`/rejectionReason, so channel-side diagnosis still needs Studio.

Adversarial pass: the 403-misroute was traced through HttpError's string format ("<HttpError 403
when requesting …") against the except-tree at 195-207; quota-403 demonstrably lands in the
re-login branch. Refresh-token-at-rest in data/youtube.token was examined and NOT flagged: it is
the single designed copy of that credential (unlike blink.token's duplicated password). Prior
findings not restated.
