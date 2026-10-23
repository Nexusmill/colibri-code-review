# colibri review — site/music_worker.js (first review, security hunt)

- source: `site/music_worker.js`
- reviewer: ZCode in-session (account:zai-individual-coding-plan/GLM-5.3), colibri-review v0.4.0, bug mode, security lens
- sha256: b8ad0e6a51c49058a978a6776d1e15ac2e3269c804e35e5f9a0f7cf830d77a9c4
- date: 2026-10-05 03:15
- context pack: never reviewed before (deployed as Cloudflare Worker "birdcam-music",
  birdcam-music.birdcam.workers.dev, commit acf8d3d 2026-09-21); uploader = the local pipeline
  (Bearer UPLOAD_TOKEN); KV namespace MUSIC; memory: Cloudflare edge 403s default python UA
  (irrelevant to the Worker itself); jCodemunch outline (10 symbols).

## Verdict

Shippable and notably well-hardened for an outward-facing surface: no CONFIRMED vulnerabilities.
Every dynamic HTML interpolation is escaped or URL-encoded (traced one-by-one below), the upload
token is compared constant-time and fails closed when unset, and path keys are decoded BEFORE
validation with an anchored charset regex plus an explicit '..' ban. Remaining items are
operational safeguards, not defects.

## Bugs & vulnerabilities

None CONFIRMED. Verification notes for the classes hunted:

- XSS: every interpolation audited — title/genre/topic/heading/date/camera through `esc()`
  (7-11, 33-35, 70-71, 84-88); hrefs and audio srcs through `encodeURIComponent` (32, 71) with a
  further `esc()` inside the attribute (35). Manifest is uploader-controlled (Bearer-gated PUT),
  so even a hypothetical slip would be self-inflicted only.
- Path traversal: `%2e%2e` decodes at line 63 BEFORE `validKey` (21-23); KEY_RE is anchored
  `^[A-Za-z0-9 _.-]+/[A-Za-z0-9 _.-]+\.mp3$` ('%' outside the charset, so double-encoding is
  rejected too), plus the explicit `indexOf('..')` ban. KV keys are a flat namespace regardless.
- Auth: `authorized()` (12-20) accumulates XOR over the full header with a length pre-check —
  the standard constant-time pattern; returns false when `env.UPLOAD_TOKEN` is unset (fail
  closed). Upload size guard (104-105) is backed by KV's own 25 MiB per-value cap.
- Content sniffing: audio responses force `content-type: audio/mpeg` after writeHttpMetadata
  (97-98).

## Missing safeguards

- The catch-all at 123-124 returns a bare 500 with NO logging (`console.log`/`throw` absent) —
  Worker failures are invisible in the Cloudflare dashboard tail; one `console.error(err)` line
  would fix observability. [LOW]
- A corrupt `manifest.json` renders as an empty site ("No songs yet") instead of an error
  (27-28) — data corruption masquerades as absence; distinguish `!obj` from parse failure. [LOW]
- HTML responses carry no `Content-Security-Policy` (defense-in-depth behind the complete
  escaping; inline styles are used, so a nonce-based CSP would need a small refactor). [LOW]

Adversarial pass: each "clean" verdict above was reached by re-opening the cited lines and
tracing the actual value flow (e.g. decode-order for traversal, per-interpolation escaping for
XSS); no finding survived to CONFIRM. The three safeguards are real but non-defects (current
behavior degrades quietly, not wrongly).
