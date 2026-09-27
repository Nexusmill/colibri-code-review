# Colibri review — bug mode (debug-run record)

- **Source:** `KokoroBookReader/reader/importers/kindle.py`
- **Reviewer:** GLM-5.3 (in-session, colibri-review v0.4.0 debug modality)
- **sha256:** 5917ed921b8dd5be6a198f7749ba3c558a421ea5e3154525863e7a382d737f31
- **Date:** 2026-09-26 21:14 · **Mode:** bug (Phase D debug record for the round-61 fix)
- **Context pack:** full-file read (118→131 lines); tests/test_kindle.py contract
  (snapshot integrity, locked-download skip, cancellation); live probe re-run with the
  new scan (book_fingerprints observed on 11 folders).

## Verdict
Shippable. The manifest's import-safety semantics are unchanged; the new books-only
digest is additive.

## What changed
`manifest()` now digests book files (`BOOK_SUFFIXES`) into a second digest at zero
extra IO (bytes already streamed) and returns a 3-tuple; `scan_kindle` stores it as
`KindleCandidate.book_fingerprint` (defaulted field — existing constructions valid);
`snapshot()` unpacks the 3-tuple and still compares only the full fingerprint + file
list, exactly as before.

## Adversarial pass
- Cancellation/size-limit raises inside the loop propagate before any digest use —
  unchanged flow (the round-53 KBR-KINDLE-LOCKED-SCAN guards untouched).
- `is_book` is computed from the suffix before IO; the path-traversal and symlink
  guards precede it.
- test_kindle.py asserts on files/candidate identity — unaffected (suite green).

## Verification
Suite 198; live probe4: 11 candidates with distinct book fingerprints, hidden/shown
classification matches the designed predicate.
