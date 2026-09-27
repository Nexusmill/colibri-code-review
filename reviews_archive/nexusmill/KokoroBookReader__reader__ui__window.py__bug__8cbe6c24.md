# Colibri review — bug mode (debug-run record)

- **Source:** `KokoroBookReader/reader/ui/window.py`
- **Reviewer:** GLM-5.3 (in-session, colibri-review v0.4.0 debug modality)
- **sha256:** 8cbe6c24e2b93bb3600ee9b68d37e6877b3bc91b0efc74d79c2b17d6b2e58be1
- **Date:** 2026-09-26 21:14 · **Mode:** bug (Phase D debug record for the round-61 fix)
- **Context pack:** jCodemunch call sites of refresh_library/import_result/ImportJob.run;
  conftest settings isolation; round-60/57 pytest-qt lessons (close order, currentItemChanged).

## Verdict
Shippable. Single new predicate `pending_kindle()` is now the ONLY source for both the
Discovered list and the "N new or changed" status (the sibling count was the
round-61 ledger's second site — closed in the same edit).

## What changed
`pending_kindle()`: a folder is pending iff its fingerprint differs AND its origin is
not mapped (live row) at the same book-files fingerprint. `refresh_library` iterates
it; the scan count is `len(pending_kindle())`; `import_result` captures
`import_book`'s returned id and records `(origin, book_id, book_fingerprint)` before
the QSettings write.

## Adversarial pass
- The ImportJob result tuple grew to 6 elements — `import_result` is the only
  consumer (searched); unpack updated in the same diff.
- Self-caught during review (contract v2): the first draft hid any recorded origin
  unconditionally, which would make an Amazon book update permanently undiscoverable;
  the book-files fingerprint comparison restores discoverability for genuine book
  changes (test UPDATED_EBOK).
- `imported_origins()` on a closed DB would raise — same exposure class as the
  pre-existing `library.books()` call in refresh_library; no new path added.

## Verification
Suite 198; window test covers hidden-stale, shown-update, legacy-fingerprint-hide,
shown-new, and the count predicate sharing.
