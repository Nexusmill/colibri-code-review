# Colibri Review - bug (FULL re-audit) - asset-forge/forge/tracer/svg_stego.py

- **Source path:** `asset-forge/forge/tracer/svg_stego.py`
- **Reviewer:** claude-fable-5-1 (fork of the lead session), Colibri G37 protocol, campaign item 1 (AF units)
- **sha256 reviewed:** `b3cb591ff5c934f11b697b3cc34594fde38f500ae15cc12d3d1006ca868fd732` (sha8 `b3cb591f`)
- **Date:** 2026-09-10 · **Mode:** bug, FULL review of the current bytes (owner ruling 2026-09-10: pre-gate audits untrusted - no delta)
- **Context pack:** jCodemunch get_file_outline + find_importers on all five units; call sites traced in forge/bundle.py, forge/pipeline.py, app.py (/api/verify), verify.py, sign_set.py, gen_bundle.py; the 2026-07-22 unit-6 svg_stego record and unit-9 row loaded as CLAIMS; both editions' forge/tracer/ hashed file by file (user build = 7 stubs, no hmac/hashlib/cryptography/numpy import, creator-only scripts absent from the user tree); probes run with asset-forge-user/.buildenv python (scipy 1.18, cryptography 50).

## Verdict
NOT shippable as the vector-output path until the fix lands: the parity layer rewrote the namespace URI, the XML encoding name, the version and every hex colour of a sold SVG (reproduced on the real dots(7) generator output: the document no longer parses - 'unknown encoding: UTF-8.000'). One fix (numbers inside geometry attribute values only), verified GREEN on a scratch copy with the serial still round-tripping through geometry. The 07-22 fixes (comment-safe token, meta stripped before decode) are present at the bytes.

## Bugs & vulnerabilities

**[HIGH] every number in the document is a parity slot** - `line 19/52/75`
- What: NUM_RE matches any digit run anywhere; _coords feeds all of them to the key-derived permutation and copies*L of them (nearly all) get a +/-0.001 nudge.
- Trigger: any SVG whose number count reaches the serial's 344 bits - the real generator output does.
- Impact: `xmlns="http://www.w3.001.org/2000/svg"`, `encoding="UTF-8.000"`, `version="1.100"`, `fill="#823.000cfd"` - the sold file fails to parse / renders nothing / loses its colours.
- Fix: GEOM_ATTRS = d, points, cx, cy, r, rx, ry, x, y, x1, y1, x2, y2; _coords returns numbers inside those attribute values only (both embed and extract share it). Snippets in summary_af_tracer_svg_stego.json; GREEN on the scratch copy.
- Verification: CONFIRMED (probe RED on the repo bytes: 4/4 checks fail, including the real generator SVG).

## Missing safeguards
- Consequence of the fix: an SVG embedded under the old all-numbers rule cannot be geometry-decoded under the geometry-only rule (its slot set differs) - its metadata comment still reads, and its geometry layer was corrupt output anyway. If any SVG was ever sold from this path it should be reissued.
- With the geometry-only rule a sparse pattern (fewer than 344 geometry numbers) gets the metadata layer only - embed_svg already handles n < L that way; the return value does not say which layers landed (same as png_stego's claim shape).
- The 2026-07-22 review's 9-scenario battery lived in junk/ (gitignored); nothing in tests/harness exercised a real generator SVG through embed_svg - which is how a header-corrupting layer stayed green for seven weeks.

## Adversarial verification pass (refuted claims)
- A token can close the metadata comment early with '-->' or inject '>' - REFUTED: _meta_encode maps '-' to '.' (07-22 fix, present at the bytes) and the token alphabet is A-Za-z0-9-_| - '>' is unreachable from make_token/make_token_asym/make_serial, the only producers.
- Re-embedding an already-marked SVG poisons the number set - REFUTED: _strip_meta runs before _coords in both embed_svg and extract_svg (07-22 fix, present).
- Scientific-notation numbers (1e-5) get split and corrupted - REFUTED: The generators emit fixed-point decimals (%.3f / ints) - NUM_RE never meets an exponent on product output; the fix's geometry-only rule limits the blast radius anyway.
- extract_svg's n >= 24 gate hides small tracers - REFUTED: The serial needs 344 bits; any document with fewer than 24 numbers cannot carry a geometry layer at all, so the gate only skips work.

## Remediation postscript (same session)
The fixes were applied after this review hashed the bytes above; the file is now `0ad829d88db3da9319ca190424421ae285f8c7a0457c930170d2e4e5c02b540a`. Rows AF-TRACER-SVG-GEOMETRY in `docs/remediation_manifest.json`, same commit.

