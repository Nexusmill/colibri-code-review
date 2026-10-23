# colibri review — birdcam/cards.py (first review, security hunt)

- source: `birdcam/cards.py`
- reviewer: ZCode in-session (account:zai-individual-coding-plan/GLM-5.3), colibri-review v0.4.0, bug mode, security lens
- sha256: c7cbe56f0af7d158a41c36c18dbbdd672c79897a570066e79ea048d63eaabbc5f
- date: 2026-10-05 04:00
- context pack: never stored as a review before (born c2ae400 2026-09-27, klein-4b calendar card
  generator — the run itself was stopped and superseded by the static-card archive, but the tool
  remains the fallback generator); reuses enricher.run_replicate/_download/_sha256 (already
  reviewed this session); gate findings cited in-line (092925/093333/094046/094339/091454);
  design tokens G28 (Space Grotesk, gold/dark); tests/test_cards.py covers the calendar math.

## Verdict

Shippable; unusually careful for a paid-asset generator — OS-level run lock with kernel-release
semantics, atomic manifest merges that re-read disk before every write, atomic card archival with
a size floor that cannot destroy an existing card under --force, honest billed-attempt accounting,
and a cost estimate printed before any spend (G19 compliant). No new findings; one pinning
safeguard.

## Bugs & vulnerabilities (new findings only)

None CONFIRMED. Verified by trace:

- Network: all Replicate traffic goes through enricher's guarded stack (allowlist + public-IP +
  per-hop redirect validation — reviewed in the enricher artifact this session); the one other
  outbound call is the fixed-https GitHub font fetch (309-313).
- `ensure_font` (293-328): size floor, PIL-must-load-before-promote, tmp→replace atomicity — an
  interrupted setup cannot poison later overlays.
- `_acquire_lock` (436-464): msvcrt/fcntl non-blocking lock, content write is best-effort by
  design, handle kept alive for the run, released by the kernel on crash — no stale-lock or
  takeover path.
- `_save_manifest` (402-415): merges under the run lock, so overlapping runs cannot erase rows;
  `_load_manifest` heals corrupt shapes before any paid generation depends on them.
- `generate_one` (467-506): raw temp removed on both paths; retries sleep; billed counts completed
  predictions even when the post-processing failed — cost reporting never understates.
- `build_index` escaping covers the interpolation set used (fixed holiday/kind vocabularies,
  posix-digit-relative image paths).

## Missing safeguards

- The font download is not content-pinned: FONT_URL is a fixed https GitHub link, but no sha256 is
  recorded for Space Grotesk — inconsistent with the person-detection model's pinned-hash
  doctrine (config validates a 64-hex sha). A compromised CDN/path change would deliver a
  different font (or a PIL-crashing blob) silently. Pin the hash next time the asset is touched.
  [LOW]

Adversarial pass: lock semantics verified against the msvcrt byte-range model (seek-then-lock of
byte 0); manifest merge verified read-merge-write under lock; the skipped header region (1-286) is
prompt/calendar constant data whose behavior is covered by tests/test_cards.py (reviewed as its
own unit this session).
