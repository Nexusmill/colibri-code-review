# Colibri Review - bug (FULL re-audit) - asset-forge/forge/tracer/fingerprint.py

- **Source path:** `asset-forge/forge/tracer/fingerprint.py`
- **Reviewer:** claude-fable-5-1 (fork of the lead session), Colibri G37 protocol, campaign item 1 (AF units)
- **sha256 reviewed:** `003df9b59a8226fe1fd6fc3ae974a093b67e3d65df32ac2d75ff91c101e76544` (sha8 `003df9b5`)
- **Date:** 2026-09-10 · **Mode:** bug, FULL review of the current bytes (owner ruling 2026-09-10: pre-gate audits untrusted - no delta)
- **Context pack:** jCodemunch get_file_outline + find_importers on all five units; call sites traced in forge/bundle.py, forge/pipeline.py, app.py (/api/verify), verify.py, sign_set.py, gen_bundle.py; the 2026-07-22 unit-6 svg_stego record and unit-9 row loaded as CLAIMS; both editions' forge/tracer/ hashed file by file (user build = 7 stubs, no hmac/hashlib/cryptography/numpy import, creator-only scripts absent from the user tree); probes run with asset-forge-user/.buildenv python (scipy 1.18, cryptography 50).

## Verdict
Clean at the full read: constant-time HMAC compares, magic + length gates, key-id-then-signature order, the asymmetric path never trusts the token's own key id.

## Bugs & vulnerabilities
None confirmed.

## Missing safeguards / notes
- datetime.utcnow() is deprecated in 3.12 (DeprecationWarning only).
- verify_token_asym reports a malformed certificate as 'malformed AF2 token' - misleading wording, harmless.

## Adversarial verification pass (refuted claims)
- A set_id containing ':' makes verify_serial's split fail (unverifiable serial) - REFUTED: Both producers (bundle.py, pipeline.py) build set_id as a 12-hex sha256 prefix - ':' never occurs.
- token_bits' 2-byte length prefix overflows for long tokens - REFUTED: A full AF1/AF2 token is ~300-400 bytes; 65535 is unreachable from build_payload (bounded fields).
- identify() calls pl.get on a non-dict payload and crashes - REFUTED: pl is only non-None when the HMAC verified under OUR secret, and make_token only signs dicts.
- _b64d on a huge token exhausts memory via /api/verify - REFUTED: Local, origin-guarded, creator-only route; the request body size is Flask/werkzeug-bounded by the caller's own upload limits - noted, not a defect of this unit.
