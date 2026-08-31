# ULTRA GATE (run 2): part-2 snapshot findings vs the LIVE PatternSkin tree

- Mode: external-review verification (G37) over /code-review ultra run 2 (free run 2 of 3,
  target audit/ps-part1..audit/patternskin-snapshot = 44 files / 8,603 lines) PLUS the
  audit-session's own on-disk verification pass (which ran against the SNAPSHOT branch).
- Date: 2026-08-13 - Model: claude-fable-5 (in-session). Drift check: ai_parts.py and
  filmstrip.py byte-identical between snapshot and live tree at gate time.

## Disposition of all 7 reported findings (4 were part-1 re-reports)
- Finding 1 (banner NameError) + finding 6 (SEL_STD default): ALREADY FIXED live
  (ultra-gate-1, commit fb1bba1) - the audit session verified the SNAPSHOT, which
  predates the fixes. Recorded here as fixed-prior, NOT re-fixed (G35). The SEL_STD fix
  is additionally regression-proven in the container rig (REGRESSION_BUG004 PASS).
- Finding 3 (tp:None autoload crash): already docketed PSK-ULTRA-5; enriched with run-2's
  exact crash chains and the coupling below.
- Finding 4 (stale _ap_pp snapshot): already docketed PSK-ULTRA-6; run-2 adds supporting
  (not conclusive) evidence for the attr-survival precondition.
- Finding 2 (save_parts key mismatch): NEW, CONFIRMED against live source including
  cache_key's lineage-or-signature definition. Docketed PSK-ULTRA-2, COUPLED with
  PSK-ULTRA-5 (fixing the key without self-healing tp turns a silent miss into a hard
  crash on reopen) - both land together in one Blender-verified tranche.
- Finding 5 (draw() -> mode_set): NEW, CONFIRMED (chain read end to end). FIXED
  (ultra-gate-2): count-validation gated to Object Mode; false draw-safe docstring
  corrected. G29 backing: no operator calls from draw().
- Finding 7 (vlm_nouns billing branches): NEW, CONFIRMED (side-by-side read with
  sam3_mask). FIXED (ultra-gate-2): the three money-safety branches mirrored verbatim.

## Verification of the fixes
py_compile clean; container-rig check (Blender 5.1.2): add-on registers, vlm_nouns'
live import carries the billing branches.

## Ultra scoreboard after both free runs
Part 1: 7 raw -> 4 verified -> 4 confirmed. Part 2: 3 raw -> 3 verified -> 3 confirmed.
Total: 7/7 confirmed, 0 refuted, 0 stale-at-report-time (2 became stale between report
and gate because we had already fixed them). 4 fixed same-day, 3 docketed into one
coupled Blender-verified tranche (PSK-ULTRA-2+5, PSK-ULTRA-6). One free run remains.
