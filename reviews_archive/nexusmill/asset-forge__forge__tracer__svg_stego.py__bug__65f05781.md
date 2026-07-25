<!-- source: asset-forge/forge/tracer/svg_stego.py | reviewer: claude-fable-5 (colibri-review G37, verify-first over deepseek-v4-pro batch) | sha256 (reviewed, pre-fix) 65f0578149e7... | 2026-07-22 | mode: bug | context pack: jcodemunch (callers: pipeline.py:84 embed_svg(token=make_token AF1|b64url|b64url, geom_token=make_serial AFS1|...), app.py:493 + verify.py:44 extract_svg; fingerprint.py token_bits/bits_to_token/_b64e alphabet; signer.py key_id=8-hex), user twin = crypto-free stub (WHITELIST divergence by design), remediation ledger -->

## Verdict
DeepSeek: 3 HIGH, 1 MED, 1 LOW. Adjudicated verify-first: 1 HIGH confirmed-with-corrected-impact,
1 HIGH refuted-as-claimed but its trace exposed a REAL sibling defect (illegal-XML `--` in ~1.1%
of sold SVGs), 1 HIGH + 1 MED + 1 LOW refuted outright, plus 1 NEW self-found defect (re-embed
poisoning). All fixes verified by a 9-scenario functional battery (junk/_svg_stego_unit6_repro.py
-> junk/_svg_stego_unit6_out.txt) + metadata round-trip check + PNG attack-grid regression (10/11,
baseline unchanged).

## Adjudication of DeepSeek findings

**[HIGH] token `-->` comment breakout / XSS (line 68) — REFUTED as claimed / CONFIRMED sibling**
- As claimed: refuted. Tokens are exclusively produced by make_token / make_token_asym /
  make_serial: `AF{1,2}|urlsafe_b64|urlsafe_b64[|8-hex]` — alphabet `A-Za-z0-9-_|`, `>` is
  unreachable, so the comment can never be closed early by our pipeline (embed_svg's only callers,
  both editions' pipeline.py:84). Creator-only local tool; operator is the trust boundary.
- BUT b64url contains `-`, and `--` inside an XML comment is ILLEGAL XML: **measured 1.1% of real
  tokens contain `--` (22/2000)**, and a sold SVG carrying one FAILS strict parsers (xml.etree
  rejects; browsers parse standalone SVG with a strict XML parser) — ~1 in 90 sale SVGs shipped
  broken. **CONFIRMED [HIGH, product-breaking], fixed:** comment layer now stores the token with
  the bijective `-` -> `.` mapping (`.` never occurs in any token format; verified across
  make_token, make_token_asym incl. 8-hex key_id, make_serial), decoded on extract; legacy raw
  comments decode unchanged (no-op). Battery: R6 sold-SVG with `--` token now parses; metadata
  round-trip on a geometry-poor SVG returns the exact original token.

**[HIGH] geometry layer broken by metadata digits (line 74) — CONFIRMED (impact corrected), fixed**
- Confirmed: extract ran NUM_RE over the WHOLE doc including our comment, whose b64 digits inflate
  n and desync `_perm(secret, n)` — geometry never decoded while a comment was present. DeepSeek's
  "defeats the whole purpose" was overstated for the benign case (strip-the-comment restores the
  embed-time number set, so the designed threat scenario worked — battery R4), but the REAL bite:
  an adversary REPLACING the comment with digit-bearing junk made extract return the FORGED string
  with geometry silenced (R5 pre-fix: got_forged=True). Fixed: both embed and extract now compute
  the number set on the META-FREE document (`_strip_meta`). Post-fix R3/R5: geometry answers first
  with the authentic serial even under a forged comment.

**[NEW, self-found during trace] re-embed poisoning — CONFIRMED, fixed**
- embed_svg computed nums on the INPUT svg, which may carry a stale AF comment (re-embedding a
  previously traced asset); parity positions then included comment digits that _with_meta
  subsequently removed — geometry layer permanently unrecoverable (R8 pre-fix: "no tracer found"
  after strip). Fixed by the same `_strip_meta` at embed entry. R8 post-fix: serial recovered.

**[HIGH] ZeroDivisionError, empty token (line 45) — REFUTED**
- token_bits prepends a 2-byte length header: `len(bits) >= 16` for ANY input including `""`;
  geom defaults to token, callers pass non-empty serial. L==0 unreachable. Battery R7: empty-token
  embed completes without crash.

**[MEDIUM] unhandled exception in bits_to_token (line 89) — REFUTED**
- bits_to_token guards len<16 -> None, need-vs-len -> None, wraps utf-8 decode in try/except ->
  None. Its input here is "".join of 0/1 ints — int(bits[:16], 2) cannot raise on that alphabet.
  No exception path exists.

**[LOW] missing L >= 16 lower bound (lines 39-40) — REFUTED**
- Impossible via the only bits producer (token_bits' 16-bit header). "A custom fingerprint
  implementation" is not a caller that exists (jcodemunch: zero other producers).

## Missing-safeguards claims
- secret str->TypeError: internal creator-only API; both call sites pass secret_bytes() bytes.
  Noted, not a defect. Float re-serialization fragility + editor-added numbers breaking NUM_RE
  count: real, documented design limit of "survives light editing" (any tool rewriting precision
  breaks any parity scheme); recorded, not fixed here. NEW note: NUM_RE splits exponent notation
  ("1e-3" -> two numbers) — no current emitter produces exponents (generators write fixed-point),
  latent hazard only, recorded.

## Fixes shipped (this unit)
`_strip_meta` used at embed entry + extract + _with_meta; `_meta_encode`/`_meta_decode` (`-`<->`.`)
for XML-comment safety; META_RE hoisted. Creator edition only — user twin is the crypto-free stub
(G14/G23 WHITELIST divergence, untouched). py_compile clean. Battery 9/9 + round-trip + PNG grid
regression green.
