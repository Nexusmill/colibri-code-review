# Cross-file synthesis: LIB-FLAGGED-1 (Tranche 1)

Files reviewed: `asset-forge/app.py`, `asset-forge/forge/userlib.py`,
`asset-forge/forge/library_gen.py`, `asset-forge/forge/bundle.py`. `asset-forge-user/`
twins verified byte-identical to each reviewed file via `git diff --no-index` after every
fix, so are covered by the same review without a separate pass. `tests/harness/` files
are test code, out of scope per the review brief.

## Findings, ranked

1. **[HIGH, bundle.py] `NameError` on `os.path.splitext` with no `import os`** - would
   have crashed every bundle run that ever produced a flagged item, the opposite of the
   feature's intent. Caught in-review (introduced during the review's own remediation of
   finding #2, not present in the originally-shipped code), fixed with `Path.stem`/
   `Path.suffix` instead. CONFIRMED, FIXED.
2. **[LOW, library_gen.py + bundle.py] Silent skip-on-filename-collision** left a flagged
   item un-moved and inconsistent with its own manifest record. Fixed in both files using
   the codebase's own pre-existing numeric-suffix convention (`_migrate_folders`'s
   pattern) rather than inventing a new one. CONFIRMED, FIXED.
3. **[test coverage gap, closed]** `AF-QUALITY-FLOOR` asserted PNG *count* but never
   *location* - strengthened to assert the flagged file's actual path, which is what
   caught #1 and #2 empirically (the harness failed until both were fixed).

## Cross-file contract check

- `library_gen.py` and `bundle.py` now implement the identical "one retry, then
  keep-and-flag, move to `flagged/`, numeric-suffix on collision" contract independently
  (no shared helper - each has its own generation loop shape: single-writer consumption
  loop vs. per-item worker closure). Verified both actually produce the same *outcome*
  (file ends in `flagged/`, `quality_warning`/`quality_metrics` populated, item status
  stays "done"/present, never discarded) even though the code paths differ structurally.
- `app.py`'s `_LIB_EXTRA` exclusion is consumed correctly by both `library_gen.py` (which
  writes into `lib_root / "flagged"` directly, matching the same string) and
  `userlib.py` (which excludes by path-segment name "flagged", matching the same
  string) - the literal string `"flagged"` is the de facto contract between three files;
  no central constant ties them together, which is a real but low-severity coupling risk
  (a future rename of the folder in one file silently desyncs the others). Not fixed this
  round - flagged here for awareness rather than expanded scope on a Tranche 1 close-out.

## Overall verdict

Shippable after the two CONFIRMED fixes. The bundle.py NameError was the single highest-
value catch of this review - it would have shipped a feature that crashes on its own
primary trigger condition. Harness re-run clean (30/30) after all fixes and a final
rebuild of the compiled distribution.
