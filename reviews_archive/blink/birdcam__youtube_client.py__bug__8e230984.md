# colibri review — birdcam/youtube_client.py

- source: `birdcam/youtube_client.py`
- reviewer: in-session (zai-coding-plan/GLM-5.3-Flash), colibri-review v0.2.0 bug mode
- sha256: 8e230984… (128 lines, bytes on disk at review time)
- date: 2026-09-05
- context pack: callers pipeline.upload (wrapped in per-batch except) and cli yt-login/check-setup; README quota + audit-lock invariants; googleapiclient resumable-upload semantics; token refresh flow from google-auth.

## Verdict

Correct against its contract (resumable upload + processing poll + persisted refresh token); the
risks are operational — transient API failures convert to "batch failed" states that cost quota
on retry — and are owned jointly with pipeline (see its F-1 orphaned-duplicate finding).

## Bugs & vulnerabilities

**[LOW] No retry/backoff around chunk uploads and processing polls** - `lines 96-104, 113-128`
- What: a single transient 5xx/network blip mid-resumable-upload raises HttpError out of
  `next_chunk`, and one failed `videos().list` poll raises out of `wait_processing` — the gate's
  per-batch handler then marks the batch failed even though the upload may have landed.
- Trigger: momentary network loss during a 1-2 GB compilation upload; a 500 during a poll.
- Impact: failed runs that need a whole extra day-cycle to recover (and, combined with
  pipeline's re-upload path, duplicate videos).
- Fix: wrap `next_chunk` and the poll request in a small retry (3 attempts, exponential backoff,
  retry only on 5xx/transport — googleapiclient's `Request` has `num_retries` support via
  `request.next_chunk(num_retries=3)` for the upload half).

## Missing safeguards

- `wait_processing` polls only `processingDetails`; a video that finishes processing as failed
  with a specific rejection reason (terms-of-use, length) surfaces only as "failed" — pulling
  `status.privacyStatus`/`uploadStatus` into the failure message would make channel-side
  diagnosis possible from `status` output alone.
- Token file writes after refresh are non-atomic (`write_text` directly) — a crash mid-write
  corrupts `data/youtube.token` (recovery: re-run yt-login; acceptable for a single-user token,
  inconsistent with state.py's atomic standard).
- No explicit scope check after `Credentials.from_authorized_user_file` — a token created with
  older scopes would 403 at upload with a Google-shaped error rather than a local hint.

Adversarial pass: the num_retries mechanism's availability on the resumable path was checked
against the installed googleapiclient (MediaFileUpload/HttpMedia next_chunk accepts num_retries
on the request construction); CONFIRMED as available. The privacy-poll and atomic-token items are
safeguards, not defects (current behavior is loud, not wrong).
