# Colibri security hunt — synthesis (2026-10-05)

- scope: ALL 36 code files in the repo (owner-ordered full hunt; prior reviews loaded as context,
  new-findings-only mandate per the 2026-09-21 amendment)
- reviewer: ZCode in-session (account:zai-individual-coding-plan/GLM-5.3), colibri-review v0.4.0
- evidence: 36 per-file artifacts + manifest pass lineage this date; `python -m unittest discover`
  = 191 tests, FAILED (errors=1, skipped=1) — the one error is finding S-2 below
- attack context: owner under active Blink-account 2FA attack; leak sweep this session: NO remote,
  sensitive paths never committed, gitignore coverage verified, no credential literals tracked

## Ranked findings (new this hunt, all adversarially verified)

**S-1 [MEDIUM, CONFIRMED] Plaintext Blink password persists in data/blink.token**
blinkpy's `Blink.save()` writes `login_attributes`, which re-adds `data["password"]` — verified
against installed blinkpy 0.25.9 source AND the live file's key set (names only, never values).
Two write sites: blink_client.py:130 and scripts/check_password.py:118. Fix (traced safe): scrub
the password key after save; re-inject credentials from .env in open_session BEFORE `_make_auth`
(blinkpy's validate_login demands username+password even for refresh grants). Directly relevant to
the active account attack: minimize at-rest copies of the master credential.

**S-2 [MEDIUM, CONFIRMED] Pillow used but undeclared → test suite red, 471 lines of regression coverage inert**
cards.py:42 imports PIL at module level; requirements.txt has no pillow; the venv lacks it.
`unittest discover` ends FAILED (loader error on tests/test_cards). Live hourly pipeline
unaffected (nothing imports cards). Fix: one requirements.txt line (or lazy import + loud message).

**S-3 [LOW, CONFIRMED] state.py save() rename without fsync**
Power loss in the rename window can materialize a zero-length state.json over the old file —
the safety evidence (which clips were deleted from Blink) is then unrecoverable; the rotation
path cannot rescue it. Fix: fsync the temp file before replace.

**S-4 [LOW, CONFIRMED] delete_video maps ANY 403 to "token lacks permission"** (youtube_client.py:200)
— a quota 403 misroutes to re-login advice. Fix: require the insufficientPermissions reason.

**S-5 [LOW, CONFIRMED] Legacy config validations crash with TypeError** (config.py:158-171)
— the deferred crash-instead-of-ConfigError pattern, now formally recorded.

**S-6 [LOW, CONFIRMED] Typo'd top-level config section silently ignored** (config.py:147) →
misleading "cameras is empty" error pointing the user at the wrong place.

**S-7 [LOW, CONFIRMED] Non-ASCII song titles break online publishing** (enricher.py:1127 vs
music_worker.js KEY_RE) — sanitize_component keeps unicode alnums the Worker's ASCII-only key
regex rejects; the songs-page link is silently lost for that video.

**S-8 [LOW, CONFIRMED] open_session raw traceback on corrupt blink.token** (blink_client.py:145).

**S-9 [LOW, PLAUSIBLE] delete_clip trusts status<300 without reading the body**
(blink_client.py:362) — a 200-with-success:false would mark a clip deleted while it lingers in
the cloud; failure-body behavior unverified.

## Selected safeguards (non-defects, recorded)

- `_guard_url` resolve-then-connect TOCTOU (DNS rebinding) — stdlib urllib cannot pin the
  validated IP with SNI; per-hop allowlist still constrains hosts. Revisit if the HTTP layer is
  ever replaced.
- youtube.token / blink.token writes non-atomic (crash-mid-write → documented re-login).
- StateStore.from_json does not type-check values (hand-editing is a documented workflow).
- Space Grotesk font download unpinned (contrast: person-detection model IS sha-pinned).
- check_password: no pacing between login attempts; run_hourly.cmd: no data/ mkdir self-heal.

## What held up (verified this hunt)

The delete-safety machine end to end (confirm→hash→delete, orphan adoption, vanished re-post
guard, takedown resurrection guard); the person gate fail-closed at every layer with a pinned
model; the SSRF guard architecture in enricher (allowlist + public-IP + per-hop revalidation);
the Worker's escaping/auth discipline; the state-machine transition guards; and the remediation
wave's fixes all present in current bytes. One retraction: the config.example "default-armed
enrichment" claim was wrong (default IS false) — corrected in its artifact after the test
contradiction surfaced.

## Recommended remediation order (next tranche, not tonight)

S-1 (secret hygiene, pairs with the live account attack) → S-2 (suite green, one line) → S-3
(one fsync) → S-4..S-8 (small guided fixes) → S-9 (verify live first, then fix or close).
