# colibri review — birdcam/enricher.py (delta + security hunt)

- source: `birdcam/enricher.py`
- reviewer: ZCode in-session (account:zai-individual-coding-plan/GLM-5.3), colibri-review v0.4.0, bug mode, security lens
- sha256: c097cbf0ac904d4baebd3469889803949b47b30f23a9dc6c34d5d8f6fda8061c
- date: 2026-10-05 03:30
- context pack: prior bug review 21fd6e41 (hy4, f04d93d bytes, 2 findings both fixed); git delta
  73225de→c1eb108 (music archive+index, online publish, village songs/catalog/genre slots, ledger,
  static card videos — the file doubled to 1567 lines, most of the network/publish code is
  UNREVIEWED until now); jCodemunch outline (60+ symbols); design docs per memory (e4a94f9, 3eaca4f,
  c1eb108); cross-file contract: site/music_worker.js KEY_RE; compiler.sanitize_component charset.

## Verdict

Shippable. The outbound-network discipline is genuinely strong for a stdlib-only pipeline: every
server-supplied URL (poll URLs, output-file URLs, every redirect hop) passes `_guard_url` —
https-only, per-service host allowlist, resolved-addresses-must-be-public — and the redirect
handler re-validates each hop, closing the silent-redirect downgrade. API keys travel only in
Authorization headers and never appear in error text. One new LOW (a cross-file charset mismatch
that breaks online publishing for non-ASCII titles); two recorded limitations below.

## Fixed since last review

- Disk-write error inside the guarded block (prior MEDIUM): `_download` writes + size-checks inside
  try (755-768) — verified.
- Naive timestamps treated as UTC (prior LOW): 174-176 — verified.

## Bugs & vulnerabilities (new findings only)

**[LOW] Non-ASCII song titles produce archive filenames the music-site Worker rejects, silently losing the online publish** - `line 1127` (`compiler.sanitize_component(song.title)`) vs `site/music_worker.js:6` (KEY_RE)
- What: `sanitize_component` keeps any character for which `str.isalnum()` is true — that includes
  é, ñ, Cyrillic, CJK. The Worker's upload key regex is ASCII-only
  (`^[A-Za-z0-9 _.-]+/[A-Za-z0-9 _.-]+\.mp3$`). An LLM title like "Pierre le rouge" is fine, but
  "Genève Sunrise" archives to `... Genève ....mp3`, the PUT `/f/...` is decoded then rejected with
  400 "bad key", and after the retry `publish_songs` returns None — the video still posts, but its
  description loses the songs-page link (and that song is missing from the public site).
- Trigger: any title containing a non-ASCII alnum character from the LLM.
- Impact: best-effort degradation, printed but easy to miss; no security impact.
- Fix: restrict archived song titles to the Worker's charset at archive time (e.g. transliterate or
  fall back to `f"song {index}"` when the sanitized form differs after ASCII-only sanitization), or
  widen the Worker's KEY_RE to Unicode classes. The pipeline-side clamp is the smaller change and
  keeps the public surface strict.
- CONFIRMED (charset trace across both files; decode-before-validate order verified in the Worker).

## Missing safeguards

- `_guard_url` resolves-then-urlopen-resolves-again — a DNS-rebinding attacker (compromised
  upstream redirect) could pass the public-IP check and then connect to a rebound private address
  (TOCTOU). Stdlib urllib cannot easily pin the validated IP with correct SNI; the per-hop
  allowlist still constrains the HOST, so the practical exposure is small. PLAUSIBLE limitation,
  not fixable cheaply — record, revisit if urllib is ever replaced. [LOW]
- `_songs_site_request` (1301-1324) skips `_guard_url`'s IP-resolution check for the FIRST url
  (only redirects are guarded); acceptable because `songs_base_url` is owner-set config validated
  https at load — noted so the docstring's "same URL-guard discipline" claim is read accurately.
  [INFO]

Adversarial pass: the title-charset finding was traced end to end (`parse_plan` title →
`_archive_song` filename → `publish_songs` PUT path → Worker decodeURIComponent → validKey) with
the reject branch verified at music_worker.js:92. The manifest key shapes (`slug`, `key`) were
checked against `_merge_manifest` for the same charset question — slugs are batch ids (ASCII by
construction). The wallet-clamp zip (1468-1475), single-clip body-deletion guard (1562-1564), and
ledger merge precedence (301-303) were each traced and found correct — not restated as findings.
