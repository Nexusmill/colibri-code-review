# Debug: library run produced 555 files where the job's content is 500 (LIB-FLAGGED-2)

- **source:** `asset-forge/forge/library_gen.py`
- **model:** claude-fable-5[1m] (in-session)
- **sha256:** cd828195ca9587b389332175988b5116701204d99a821a3d666e6e8671b0ff81 (post-fix bytes; twin byte-identical)
- **date:** 2026-08-12
- **mode:** debug (Phase D)
- **context pack:** file outline + `_lib_out()`/`prepare_job` call sites (app.py), LIB-FLAGGED-1
  comments in both twins + its remediation row, AF-QUALITY-FLOOR registry row + tester,
  live-library census (Damien's real `C:\Users\User\Documents\AssetForge\library`), job
  `20260812_055729_3c8fb80615` autopsy (job.json fields + per-item pair check)

## Reproduce / capture

Damien: "i ran the library 300 files now there is 555, its not supposed to do that anymore."
Census of the live library: job 20260812_055729 = 300 items, all `done`, model
flux-2-klein-4b, `height_map=True`. `heightmap/` = **555 files, all from this job**:
305 raw + 250 height. `flagged/` = 100 (50 retry raws `_rXXXX` + 50 heights).
Per-item check: **all 300 recorded pairs exist** — ~50 items record their final home in
`flagged/`. Reconciliation: 245 clean items (490 files) + 5 retry-accepted (10 files)
= 500 referenced in heightmap/ + **55 files referenced by NOTHING** = 555. The 55 are
quality-floor-rejected first attempts (50 whose retry also failed → pair went to flagged/;
5 whose retry passed → pair stayed in heightmap/ under `_r` names).

## Hypothesis ledger

1. **Rejected first attempts orphaned by the retry path** — CONFIRMED. `_attempt` line
   ~752: retry deliberately writes a DIFFERENT filename and leaves the rejected image "on
   disk for inspection" (2026-07-30, pre-dates flagged/). The LIB-FLAGGED-1 move block
   (coordinator) moves only `png`/`hp`/`vector` of the FINAL attempt, and only when
   `quality_warning` is set. First attempt never moves, on either outcome. Arithmetic
   closes exactly (55 = 50 + 5).
2. Stale/old files from earlier runs mixed in — REFUTED: every heightmap/ file carried
   this job's `_3c8fb8` suffix; `heightmap.old`/`.old2` are separate roots.
3. Wrong build (Damien's suspicion) — REFUTED: the job's prompts contain tranche-1
   TYPE_FORMS phrases ("scalloped edge scales" …) that exist only in the new build.
4. PATTERN-1 changed file behaviour — REFUTED: PATTERN-1 touched prompt text only; the
   orphan mechanism is dated 2026-07-30 and was present in the 08-09 runs' leftovers too.

## Fix (root cause, minimal)

`_attempt` records the rejected file on the item (`qc_rejected`, rel path) when the retry
is taken; the single-writer coordinator moves every recorded reject to `flagged/` via
`_unique_flagged_dest` (hoisted out of the warned-item branch) and persists destinations
as `qc_rejected_files`. Both retry outcomes covered; inspection-evidence intent preserved,
in `flagged/`. Live library repaired the same way: 55 orphans MOVED (not deleted) with a
reversible log (`flagged/_orphan_cleanup_20260812.json`); heightmap/ = 500, 0 unreferenced.

## Verify

Offline reproducer (scripted fake provider), both scenarios, post-fix: retry-fails →
heightmap 0 / flagged 2 / recorded / 0 unreferenced; retry-passes → accepted `_r` pair in
heightmap, reject in flagged, recorded, 0 unreferenced. AF-QUALITY-FLOOR tester extended
with both scenarios + the direct invariant (every png under the job dir referenced by the
job record); assertions authored against pre-fix behaviour = their own falsification.
Registry expectation + anchor updated same commit. Remediation row `lib-flagged-2` (G35).
