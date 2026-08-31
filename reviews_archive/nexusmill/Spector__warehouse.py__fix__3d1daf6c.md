# Fix closure — Spector/warehouse.py (WH-11..14 unpark tranche)

- **Source path:** `Spector/warehouse.py`
- **Model:** claude-fable-5 (in-session)
- **sha256 (post-fix):** `3d1daf6c7666d1cc291138a9007be5a187ee379f536941c6177a39db9a7ec584`
- **Prior review sha:** `f9dfde08…` (the 2026-08-12 bug review that produced dockets WH-11..14)
- **Date:** 2026-08-15 · **Mode:** fix-closure (delta against the prior review, per the skill's stale-file DELTA law)
- **Context pack:** prior review + deferred_manifest WH-11..14 + jCodemunch (`Nexusmill/nexusmill`) reference sweep for `_all_dna` (warehouse-internal only; app.py's `_all_dna` is an unrelated module-level twin) and `near_duplicates` (one route call site, return shape unchanged) + `index.py` read for `_sqrt_weights`/`query` clamping.

## Fixed since last review

- **WH-11 CONFIRMED → FIXED** — `_write_blob` now tmp → fsync → `os.replace`; exists-skip only on size match (truncated survivor repaired in place); `gc_blobs` sweeps `.bin.tmp` crash residue.
- **WH-12 CONFIRMED → FIXED** — DNA cache carries per-row `scale_invariant`; `find()` queries each space with a matching DNA and merges (non-rerank path sorts the merge); ingest dedup and `inspect` restricted to same-space rows. `find_similar` inherits via `_find_locked`.
- **WH-13 CONFIRMED → FIXED** — `near_duplicates` applies `_sqrt_weights` per space; exact SearchIndex metric parity (probe checks both the hand-computed reference and a live `SearchIndex.query`).
- **WH-14 CONFIRMED → FIXED** — `_check_faces` on all three array paths; named scene-flatten error; `reproduce()` distinguishes unreadable blob from missing part; import filters `blobs/` to `[0-9a-f]{64}.bin`; `_chamfer` → inf on empty clouds.

## Verification

`tests/harness/probes/wh_unpark.py` 14/14 (real `Warehouse` on temp roots); full feature tier
green (CRITIC 0 FAIL, 0 DRIFT; SP now 13 rows incl. SP-WH-UNPARK). One probe assertion was
corrected during verification (dedup-twin tie at distance 0.0 — either row may rank first);
no product change came from that failure.

Remediation manifest row: `sp-unpark-wh` (same commit).
