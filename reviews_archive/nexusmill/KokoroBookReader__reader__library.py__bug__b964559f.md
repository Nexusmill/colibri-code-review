# Colibri review — KokoroBookReader/reader/library.py (bug / debug, Phase D)

- Source: KokoroBookReader/reader/library.py
- Reviewer: GLM-5.3 (in-session, ZCode)
- sha256: b964559fddcfb147d755b7a7d122628f99d77cc56481e3411d527a3fd2797794
- Date: 2026-09-26
- Mode: bug (debug ladder — specific failure: duplicate Kindle imports)
- Context pack: jCodemunch symbol map (import_book, books, scan_kindle, manifest, ImportJob.run,
  import_result, refresh_library); live-library forensics (snapshot read of library.sqlite3 WAL);
  remediation manifest prior KBR rows (KBR-KINDLE-LOCKED-SCAN et al.); memory kokorobookreader-app.

## Failure signal (reproduced on live data)
Library held 11 rows with two duplicate (title, author) groups: "Part 2 Volume 1"
(aa81033a rowid 1 vs 44951402 rowid 6; 8256 sentences / 55 chapters both; epub sizes differ by
4 bytes) and "Part 3 Volume 5" (704ceff8 rowid 5 vs e3748f13 rowid 8; 7094 / 55 both; 1 byte
apart). All four rows: default reading position, zero narration/cast keys, no scan_cache/refined.

## Root cause (traced end to end)
Library.import_book's ONLY identity is the source-file sha256 (book.id). Kindle re-imports of the
same title re-convert via Calibre and the output is not byte-stable (observed 4-byte/1-byte
deltas), so every re-import hashes differently and inserts a second row. The re-import trigger:
refresh_library hides a candidate only while QSettings kindle/<id> equals the directory
fingerprint, and manifest() fingerprints EVERY file in the download dir — Kindle-side sidecar
changes (position sync / re-download) flip it, re-showing an imported book as "Discovered".
scan_kindle itself is pure inventory (unique glob dirs) — duplication never originates there.

## Fix (minimal, root cause)
import_book now returns the existing book's id when any stored row has the same (title, author),
placed after the existing hash short-circuit and BEFORE any file copy (no temp file, no teardown
scope). First-imported wins; a genuinely revised edition with identical title+author returns the
existing row (no replace feature exists; no-duplicate-rows is the ordered behavior).

## Sibling ledger (G41)
- Library.import_book — APPLY.
- ReaderWindow.import_result — ADJUDICATED: idempotent via import_book; fingerprint updated so
  the candidate stops re-appearing; "Ready: <title>" truthful on both paths.
- ReaderWindow.refresh_library — ADJUDICATED: fingerprint-mismatch discovery signal unchanged;
  re-imports can no longer create rows.
- scan_kindle / manifest — ADJUDICATED: inventory only.
- EPUB/TXT import path — covered transitively (same import_book).

## Verification
RED: test_import_same_book_reconverted_bytes_returns_existing_id failed exactly at the invariant
(second row created, returned id != first id). GREEN after fix; boundary test
test_import_different_title_same_author_still_imports pins the guard's input space; pre-existing
test_library_deduplicates_restores_and_copies_source unchanged and green. Full suite 194 passed
(192 + 2). Live data remediation: 2 duplicate rows + 2 orphaned epubs deleted after backup
(junk/kbr_dedup_backup_20260926/); post-state 9 books, zero duplicate groups, 9 epubs.

## Findings verdicts
- CONFIRMED: sha256-only identity admits re-converted duplicates (live rows + RED test).
- CONFIRMED: volatile directory fingerprint re-surfaces imported books (mechanism; by design
  unchanged — with the guard the re-import is a no-op that refreshes the fingerprint).
