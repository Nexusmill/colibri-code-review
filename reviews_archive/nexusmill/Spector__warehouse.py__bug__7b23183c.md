# Colibri Review - bug (FULL re-audit) - Spector/warehouse.py

- **Source path:** `Spector/warehouse.py`
- **Reviewer:** claude-fable-5-1 (in-session), Colibri G37 protocol, campaign item 1 (product cores), rank 53
- **sha256 reviewed:** `7b23183c383300c0c8217f895036de99dcf87d7af2b5c0c9ca771c38b7cf01d4` (sha8 `7b23183c`) - the PRE-fix bytes
- **Date:** 2026-09-10 · **Mode:** bug, FULL review of the current bytes (owner ruling 2026-09-10: this file's prior audits predate the adversarial gate and cannot be trusted - no delta against them)
- **Context pack:** FULL read of the current bytes (owner ruling 2026-09-10: the file's reviews of 2026-07-19..08-15 predate the gate and are untrusted); jCodemunch `get_file_outline` + `find_importers`; the prior review records and the remediation/deferred rows for the file loaded as CLAIMS to re-verify, not as baseline; call sites traced with `get_symbol_source`.

## Verdict
Shippable after the two fixes below (applied this session, RED-first). The 1233 lines were read end to end: the atomic blob path (WH-11), the per-space search (WH-12), the pack validation (`_clean_row` caps, hash-shaped blob names, ref-cycle guard) and the startup GC all hold at the bytes. Both defects are DATA-LOSS class and both sat behind pre-gate reviews that never exercised them.

## Bugs & vulnerabilities

**[HIGH] The whole-library `.spectorpack` export zipped the RAW `library.db` of a WAL-mode connection** - `_export_pack_locked`, the `ids is None` branch
- What: `__init__` sets `PRAGMA journal_mode=WAL`; a commit in WAL mode lands in `library.db-wal` and reaches `library.db` only at a checkpoint (autocheckpoint at 1000 pages, or connection close). The export copied `library.db` alone.
- Trigger: export while the app runs (the only way the UI exports) after any ingest since the last checkpoint.
- Impact: the pack - the product's portable/transfer format - silently omitted the newest parts. Reproduced: one part in the library, zero in the pack.
- Fix (applied): `_snapshot_db()` - `VACUUM INTO` a temp copy (the path `backup()` already used), fallback `PRAGMA wal_checkpoint(FULL)` then copy - is now what both `export_pack(ids=None)` and `backup()` zip/copy. Battery `tests/harness/probes/sweep_wh_r3.py` `WH_export_includes_wal_rows` watched RED (0 of 1) then GREEN.
- Verification: CONFIRMED (SQLite WAL semantics + the reproducer).

**[MEDIUM] Linked-duplicate guards counted LIVE children only** - `_delete_locked`, `purge_trash`, `restore`
- What: a dedup child stores no blob; it resolves through `ref_id`. `_delete_locked` refused to remove a parent only while a child sat in `parts`; a child in the TRASH did not count, so its parent could be permanently deleted (`_drop_blob` then removed the only geometry) or purged. `restore()` re-inserted such a child with a dangling `ref_id`, i.e. a part that can never reproduce.
- Trigger: trash a duplicate, then permanently delete (or trash and purge) its parent, then restore the duplicate; or a pack import that inserts a child whose parent is in the trash.
- Impact: silent permanent loss of the child's geometry; only `verify()` would ever show it.
- Fix (applied): `_n_children()` counts both tables; permanent delete refuses while trashed children exist (soft delete stays allowed - the trash row keeps the blob); `purge_trash` keeps any row a live child, or a trashed child not purged in the same call, still needs (reports `skipped`); `restore()` refuses a child whose parent is not live ("restore its parent first"). Battery sections B-D RED then GREEN; `wh_unpark.py` + `sp_four.py` ALL PASS; Spector's own `tests/test_warehouse.py` now runs to the end.
- Verification: CONFIRMED by trace and reproducer.

## Adversarial verification pass / notes
- `tests/test_warehouse.py` (Spector's own suite) had been dying at its delete assertion since the trash landed (it expected a soft delete to drop the blob), so its backup / pack-import / thumbnail-cap sections never ran - revived to the trash contract (row SP-TEST-WAREHOUSE-DEAD).
- Missing safeguards (not fixed): `_import_pack_locked` extracts the whole zip with only a slip guard (no inflate cap - a hostile pack can fill the disk; local-only, user-chosen file); a child row whose `ref_id` never resolves is imported as-is (verify() flags it as broken_ref); `restore()` on an id that a live part reuses deletes the trash row before raising.

## Remediation postscript (same session)
The fixes were applied after this review hashed the bytes above; the file is now `0ac65534e034c4ea998e3cdea0f75402ec0db1006bd2e7f196746aaef1c6c1eb`. Rows SP-WH-EXPORT-WAL, SP-WH-TRASH-REFS and SP-TEST-WAREHOUSE-DEAD in `docs/remediation_manifest.json`, same commit.
