# colibri review — birdcam/pipeline.py

- source: `birdcam/pipeline.py`
- reviewer: tencent/hy4-preview via hy4-review headless CLI (rung M2); grok-4.3
  effort=high via grok-review CLI (rung M3 escalation — file carried a HIGH at M2)
- sha256: eda35139cc58d968  (M2 bytes = commit f04d93d; the
  M3 pass ran on post-M2-fix bytes printed by its CLI as 7f15d3708e7b21b2)
- date: 2026-09-19 16:05 / 16:35
- mode: bug
- context pack: prior review a4da978f (delta flow — orphaned-duplicate upload and
  _title_for findings remediated earlier, not restated); gate diff-clearance
  rounds for this feature; call sites cli._run_pipeline + fakes; delete-safety
  invariants (sha256-vs-file at delete time, day-end holding, upload caps).

## Verdict
Safety machine still sound; the enrichment hook's guard had a real hole and the
escalation pass surfaced one pre-existing dry-run violation. Both fixed.

## Fixed since last review (delta flow)
- Orphaned-duplicate upload loop — remediated (1a7e00e wave), verified absent.
- _title_for None member — remediated, verified absent.

## Bugs & vulnerabilities
**[HIGH — confirmed contract gap] enrichment result-handling sat outside the
guarded region** - `compile_batches` hook (M2, hy4)
- What: only the enrich_compilation CALL was inside try/except; the unpacking
  `final_path, final_digest, note = enriched` + `relative_to` ran unguarded.
- Trigger: a malformed success value (wrong shape / path outside root).
- Impact: escaped exception aborts the whole compile run — every pending
  camera/day batch skipped, contradicting "never blocks the plain upload".
- Fix: whole handling moved inside the try; failure sets enriched="failed".
  Tests: test_malformed_success_result_still_posts_plain_batch (plus the
  existing crash test). CONFIRMED and fixed.

**[HIGH — pre-existing, found by M3] missing-archive branch mutated state under
--dry-run** - `upload`
- What: `if not path.exists(): _fail_batch(..., release=True)` ran before the
  dry_run check.
- Trigger: dry-run upload pass over a staged batch whose file is gone.
- Impact: clips released and batch failed during a no-side-effects pass.
- Fix: dry_run now prints and continues without mutation. Test:
  test_dry_run_upload_with_missing_archive_does_not_mutate_state. CONFIRMED
  and fixed. (Pre-dates this feature run; in-scope because the file was
  altered — recorded here per G35 in the same commit as the fix.)

## M3 pass lineage
- grok-4.3 effort=high, 2026-09-19 16:35, new: 1 (the dry-run finding above).
  Note: routing table names grok-4.6; the CLI ran its default grok-4.3 — still
  a third distinct family vs gate (glm-5.3-flash) and M2 (hy4-preview).
