# Colibri review — bug mode (test-surface audit)

- **Source:** `KokoroBookReader/tests/test_imports.py`
- **Reviewer:** GLM-5.3 (in-session, colibri-review v0.4.0 debug modality)
- **sha256:** 8246238d864a17f004d270ef7ff3e1019a2540723b8cc134ff1372442c11192c
- **Date:** 2026-09-26 21:14 · **Mode:** bug (test-surface audit, round-61 tests)
- **Context pack:** contract sources = Library.record_origin/imported_origins + the
  round-60 identity tests above them in this file.

## Verdict
Sound. Both new tests were proven RED (AttributeError on the missing methods) before
implementation.

## Audit
- `test_kindle_origin_hides_folders_only_while_book_lives`: asserts the empty mapping,
  record, rebind (row + book fingerprint), deleted-row un-hide, rebind-to-live. The
  manual row deletion via `with lib.db` simulates the only real deletion path (no
  remove API; round 60 deleted rows via SQL).
- `test_kindle_origin_table_upgrades_a_legacy_library`: constructs a pre-table DB with
  raw sqlite3, opens it with new code — the live owner DB's exact upgrade path.
- No tautologies, no environment leaks, deterministic, no machine paths.
