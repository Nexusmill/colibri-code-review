# Colibri review — bug mode (debug-run record)

- **Source:** `KokoroBookReader/reader/library.py`
- **Reviewer:** GLM-5.3 (in-session, colibri-review v0.4.0 debug modality)
- **sha256:** 455f0a44fd3d40467b31b1d88156ae02df44afbd2e1119599121501e5dad29f3
- **Date:** 2026-09-26 21:14 · **Mode:** bug (Phase D debug record for the round-61 fix)
- **Context pack:** jCodemunch symbol map (Library class, import_book identity guard,
  callers in reader/ui/window.py); round-60 remediation row (import-side duplicate
  guard, same domain); live sqlite forensics (junk/kbr_dup_probe3.py); suite 198.

## Verdict
Shippable. The change adds the missing durable fact ("this Kindle folder's book is in
the library") that round 60 forensics identified as the scan-side hole; the round-60
identity guard is byte-untouched.

## What changed and why (finding KBR-SCAN-DUP-REDISPLAY)
`refresh_library` hid scanned Kindle folders only while a volatile whole-folder
fingerprint matched; Kindle sidecar writes flip it post-import, so already-imported
books re-appeared as "Discovered" (owner report 2026-09-26; live probe: 2 of 9 stored
origins stale). This file gains `kindle_origins(origin, book_id, book_fp)` +
`record_origin()` + `imported_origins()` (JOIN books: a deleted book row turns its
folder back into a real candidate — the JOIN is the invariant).

## Adversarial pass
- `record_origin` failure path: raises into `import_result`'s existing except AFTER
  `import_book` succeeded → status can over-report failure (PRE-EXISTING posture for
  the adjacent QSettings write; next import rebinds and self-heals). Documented, not
  changed — no new silent swallow introduced.
- Legacy DBs: `CREATE TABLE IF NOT EXISTS` in `__init__` upgrades in place (test
  `test_kindle_origin_table_upgrades_a_legacy_library`).
- Rebind semantics: INSERT OR REPLACE covers re-import under a new download folder
  and revised editions (identity guard returns the existing row id; round-60 tests).

## Verification
Suite 195 → 198 (new: origin lifecycle incl. deleted-row un-hide + rebind; legacy
upgrade; window display cases). RED→GREEN traced.
