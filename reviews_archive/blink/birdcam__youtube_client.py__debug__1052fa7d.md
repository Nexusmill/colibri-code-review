# colibri review — birdcam/youtube_client.py (debug)

- Source: birdcam/youtube_client.py
- Reviewer: ZCode in-session (GLM-5.3)
- sha256: 1052fa7dccfb58c77898777757d5c39a6a4621cdb985b53f28259a59e4227f97
- Date: 2026-09-18
- Mode: debug (failure investigation — channel stopped receiving videos after 2026-09-10 footage)
- Context pack: data/hourly_run.log (full run timeline), data/youtube.token structure (keys
  only, no values), config.yaml (max_uploads_per_run=6), pipeline.py::upload +
  state.py::StateStore.batches (oldest-first, 6-slot budget → backlog-drain semantics),
  git log (last code change 2026-09-11 20:47 vs failure onset 2026-09-12 00:27), Google
  OAuth 2.0 official docs (Testing-status consent screens issue 7-day refresh tokens).

## Symptom

No new YouTube videos since the 2026-09-10 compilations posted (early 2026-09-11).
Every hourly run since 2026-09-12 00:27 fails every upload with:
`invalid_grant: Token has been expired or revoked.`

## Evidence timeline

- Refresh token issued at setup: 2026-09-04/05.
- Last successful refresh + uploads: 2026-09-11 00:31 local (token file mtime;
  access-token expiry field 2026-09-11T07:31Z) — these were the 09-10 videos, the last posted.
- 2026-09-11 01:27→23:27 runs: zero upload attempts (the only closed-but-unuploaded day,
  09-11, was still open/held), so the dead token surfaced no error that day.
- First failure: 2026-09-12 00:27 run — first attempt to use the >7-day-old refresh token.
  Identical failure on every attempt since: 6 per run, oldest-first (09-11/12/13 × both
  cams); 09-14→17 never reach the 6-slot `max_uploads_per_run` budget while retries fail.

## Root cause — CONFIRMED (external; no code defect)

Google expires refresh tokens 7 days after issuance while the OAuth consent screen's
publishing status is "Testing" (official: developers.google.com/identity/protocols/oauth2).
Our token died exactly 7 days after issuance. youtube_client.py is correct:
`_get_service()` refreshes and persists the token; `login_interactive()`
(prompt="consent") replaces it cleanly on re-login. Staging, compiling, and state
handling were healthy throughout the outage (clips kept staging; batches kept forming).

## Fix

1. Immediate (owner action): double-click `2-youtube-login.bat`, sign in, approve —
   new refresh token; pipeline self-recovers on the next hourly run.
2. Durable (owner action, Google Cloud Console): OAuth consent screen → "Publish app"
   (production status stops the 7-day expiry; unverified-app warning during consent is
   expected and safe to click through for personal use). This is separate from the
   YouTube API compliance audit that unlocks public visibility of uploads.

## Post-fix expectations

Backlog (2026-09-11 → renewal day, both cams) drains oldest-first at ≤6 uploads/run,
~6/day (API quota resets midnight Pacific) — full catch-up ≈ 3 days. Blink-side
deletions resume only for batches that reach `confirmed`, as designed; nothing was
deleted during the outage and no footage was lost (staged clips + compilations retained).
