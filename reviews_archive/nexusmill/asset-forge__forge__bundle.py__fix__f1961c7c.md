# Colibri fix-pass record - asset-forge/forge/bundle.py (GROK-BD replay residual)
- source: asset-forge/forge/bundle.py
- model: claude-fable-5 (in-session)
- sha256: f1961c7c1c656f294658f43f64b1a40978c181f3224337290caf53c060684b22
- date: 2026-08-15
- mode: fix (GROK-BD finding 3 replay half)
- context pack: full read of build_bundle recipe restore + _build_one worker + recipe_out writer
  (tranche-1 state: requested_seed/delivered_seed/quality_warning already persisted); GROK-BD #4
  validation belt; deferred_manifest GROK-BD done-note; _run_bundle out_dir uniqueness (job_id
  suffix) checked for the finding-5 marker question.

## Verdict
The replay consumption half of finding 3 re-verified OPEN against current bytes and fixed: replay
of a floor-retried item now generates once at the delivered seed, floor off, warning carried,
requested-seed keying preserved for refs/filenames. Finding 5's unlink half FIXED (success clears stale INCOMPLETE markers; reachable via the CLI
regen path only - app runs use unique job_id dirs); the finals-overwrite half recorded as a
CLI-operator caveat.
Probe grok_bd_replay.py 11/11. Twin byte-identical.

## Fixed since last review
- GROK-BD #3 replay half -> delivered-seed replay branch, no floor re-run, strict delivered_seed validation
- GROK-BD #5 marker half -> success unlinks stale INCOMPLETE markers (CLI dir-reuse path)
