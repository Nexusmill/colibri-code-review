# Colibri Review - bug (FULL re-audit) - asset-forge/forge/tracer/signer.py

- **Source path:** `asset-forge/forge/tracer/signer.py`
- **Reviewer:** claude-fable-5-1 (fork of the lead session), Colibri G37 protocol, campaign item 1 (AF units)
- **sha256 reviewed:** `10354644cb6a3f4917860d78f39edf7140c9d3b4c4daac1ccd8947fcbb6ec824` (sha8 `10354644`)
- **Date:** 2026-09-10 · **Mode:** bug, FULL review of the current bytes (owner ruling 2026-09-10: pre-gate audits untrusted - no delta)
- **Context pack:** jCodemunch get_file_outline + find_importers on all five units; call sites traced in forge/bundle.py, forge/pipeline.py, app.py (/api/verify), verify.py, sign_set.py, gen_bundle.py; the 2026-07-22 unit-6 svg_stego record and unit-9 row loaded as CLAIMS; both editions' forge/tracer/ hashed file by file (user build = 7 stubs, no hmac/hashlib/cryptography/numpy import, creator-only scripts absent from the user tree); probes run with asset-forge-user/.buildenv python (scipy 1.18, cryptography 50).

## Verdict
Clean at the full read; the user-build stub verification passed byte for byte (G14/G15).

## Bugs & vulnerabilities
None confirmed.

## Missing safeguards / notes
- PivSigner.key_id / _rs_to_der use x509 / asym_utils without the _HAVE_CRYPTO guard: without cryptography they raise NameError instead of the clean RuntimeError EcdsaFileSigner gives (creator machine has cryptography - cosmetic).
- PivSigner.sign: a failing sess.login(pin) raises before the try, leaving the PKCS#11 session open until GC; getSlotList()[slot_index] raises IndexError with no token present - creator-side ergonomics, not correctness.
- verify_signature checks the signature only - no validity window, chain or revocation - by design: the verifier supplies the certificate it trusts.
- G14 CHECK (byte level): asset-forge-user/forge/tracer/ = 7 stubs (sha8 05b5bb1a __init__, 3c8b176f config, 47f28363 fingerprint, e03df531 keys, e21dbf22 png_stego, ee91533c signer, 464dd796 svg_stego), no hmac/hashlib/cryptography/numpy/PIL import; verify.py, sign_set.py, gen_bundle.py, sign/, creator_cert.pem ABSENT from the user tree; forge/watermark.py in the user tree is a copy-through stub (G15). No real tracer code is reachable in the user build.

## Adversarial verification pass (refuted claims)
- verify_signature passes (sig, body) in the wrong order - REFUTED: cryptography's EllipticCurvePublicKey.verify(signature, data, algorithm) - the call matches; the RSA branch (PKCS1v15 + SHA256) likewise.
- The 8-hex key id lets a forged token pass with a colliding id - REFUTED: The id is a routing hint; verify_token_asym still verifies the signature against the certificate's key - a collision buys nothing.
- PivSigner keeps the PIN in memory - a leak - REFUTED: Documented ('captured once per object, RAM only'); the PIN is needed per context-specific login and is never written or logged.
