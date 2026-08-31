# Bug review: asset-forge/forge/library_gen.py (LIB-FLAGGED-1 additions)

- Model: claude-sonnet-5 (in-session)
- sha256 (final, post-fix): 4e7bd2f6...
- Date: 2026-08-10
- Mode: bug
- Context pack: full symbol map of `_run_job_locked`/`_attempt`/`_write_manifest` already
  held from writing this code this session; `.colibri_reviews/_manifest.json` checked -
  no prior review of this file existed (first review). Scope: the new flagged-folder
  relocation block in the job consumption loop, and `_write_manifest`/
  `_write_quality_report`. Cross-referenced against `_migrate_folders`'s established
  collision-handling convention elsewhere in the same file.

## Verdict

Shippable after one fix applied during this review. Biggest risk before the fix: a
quality-floor-failed item could silently stay in `heightmap/`/`emblem/` on a filename
collision in `flagged/`, contradicting the feature's own stated guarantee ("visibly
separated") without any error or log line - low probability (filenames carry job_id+seed)
but a real, silent correctness gap for the exact invariant this feature exists to hold.

## Bugs & vulnerabilities

**[LOW] Silent skip-on-collision leaves a flagged item unmoved** - `library_gen.py`
(consumption loop, flagged-relocation block)
- What: the first cut wrote `if not _fdst.exists(): png.rename(_fdst); png = _fdst` -
  on a name collision in `flagged/`, the `if` is false, so neither the rename nor the
  `png = _fdst` reassignment happens. The item still has `quality_warning` set and its
  `it["file"]` manifest field still points into `heightmap/`/`emblem/`, contradicting the
  feature's own promise.
- Trigger: two different jobs producing a flagged item with the identical final filename
  (same pack/type/seed/job_id-prefix - low probability, not impossible across jobs).
- Impact: inconsistency between "this item is flagged" (manifest field) and "this item is
  quarantined" (file location) - undermines the exact guarantee LIB-FLAGGED-1 exists for.
- Fix (applied): replaced with the file's own established numeric-suffix convention
  (`_migrate_folders`'s pattern, including the `.height.png` double-extension special
  case) via a small `_unique_flagged_dest()` helper - the move now always succeeds.

## Missing safeguards (bullets)

- (Closed by this review) Test coverage: `AF-QUALITY-FLOOR` previously only asserted a
  PNG *count* of 2 under the job dir, never that the flagged item actually landed in
  `flagged/` specifically - strengthened to assert `it["file"]` starts with `flagged/`
  and the file exists at that path on disk.

## Fixed since last review

N/A - supersedes `asset-forge__forge__library_gen.py__bug__30f01d27.md` (the pre-fix sha),
same review session, not a separate later pass.
