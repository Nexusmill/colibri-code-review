# Colibri review — KokoroBookReader/reader/library.py (bug / debug, Phase D, gate-hardened)

- Source: KokoroBookReader/reader/library.py
- Reviewer: GLM-5.3 (in-session, ZCode)
- sha256: f67d30b2210a8e6360df3be78aa2f7324ed33177491028320cec0e0c0ece91fc
- Date: 2026-09-26
- Mode: bug (debug ladder; supersedes b964559f after the adversary-gate BLOCK round 1)
- Context pack: prior review b964559f (same hunt); gate verdict gate_20260926-023019 (mimo-v2.6-pro
  BLOCK, 2 findings); read_epub metadata defaults (title->stem, author->""); repo precedent
  KBR-STALE-VOICE-PATHS (per-entry guards); live-library forensics (unchanged).

## Delta since b964559f (gate findings, both CONFIRMED and FIXED)
1. MEDIUM (wide match space): (title, author) equality alone could merge distinct books -
   read_epub defaults missing OPF title to path.stem and missing creator to "", and Book(None)
   shapes exist behind the round-57 export guards. FIXED: identity match now requires BOTH
   title and author to be non-empty strings AND identical sentence-text sequences; books
   without real metadata never identity-match (fall through to normal import + hash dedup).
2. LOW (unguarded per-row parse): one corrupt payload row would raise out of import_book and
   block all imports. FIXED: per-row try/except (AttributeError, TypeError, ValueError) ->
   skip that row (repo precedent for this loop shape).

## Verification
RED: test_import_revised_edition_same_title_imports_separately and
test_import_without_author_metadata_never_identity_matches failed against the wide guard.
GREEN after hardening; test_import_same_book_reconverted_bytes_returns_existing_id reworked to
the true re-conversion shape (two EPUBs, same extracted text, different zip timestamps ->
asserted different ids) and passes; suite 195/195. Live data state unchanged (9 books, zero
duplicate groups).

## Adjudicated (not changed)
- "Surface the swallow to the caller": returning the existing id matches the pre-existing
  hash-dedup contract (import_result shows "Ready: <title>", and titles are identical by the
  match predicate); with the content check a swallow now only occurs for identical text.
- Revised edition with same title+author now imports as a second row - distinct content is
  not a duplicate; no replace feature exists.
