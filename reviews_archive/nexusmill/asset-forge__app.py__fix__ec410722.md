# Colibri fix-pass record - asset-forge/app.py (GROK-APP residual: findings 2, 3, 5)
- source: asset-forge/app.py
- model: claude-fable-5 (in-session)
- sha256: ec4107227f59579f56a763d631586c8b6b2915b2a4d45c9a961f89af26b160e0
- date: 2026-08-15
- mode: fix (GROK-APP findings 2+3+5)
- context pack: prepare_job source read in full (param consumption + DOCTRINE-4 prompt_upgrade
  ignore + internal estimate pinned False); libgen_estimate/libgen_regen contracts; bundle.py
  build_bundle signature + _build_one worker read (NO alpha pipeline exists); templates/index.html
  outputOpts()/startBundle()/background select (emblem class DEFAULTS to transparent);
  bundle_poll passthrough; deferred_manifest GROK-APP tranche-1 done-note.

## Verdict
Findings 2+3 re-verified CONFIRMED against 01619d37 (finding 2 with a NARROWED mechanism -
prompt_upgrade dead per DOCTRINE-4, the raw-body class and 500-vs-400 divergence live).
Finding 5 re-verified OPEN despite tranche 1's done-note omitting it; advisor consult resolved the
scope fork: the G19 floor ships now (shared _bundle_output_floor, surfaced transparent downgrade),
the dual-pass FEATURE is re-docketed as AF-BUNDLE-ALPHA rather than built under a fix mandate.
Probe grok_app_residual.py 16/16. Twin byte-identical.

## Fixed since last review
- GROK-APP #2 raw body -> allow-listed job dict + ValueError->400
- GROK-APP #3 model literal divergence -> single catalog-default resolution, written back, worker-identical
- GROK-APP #5 defect half -> bundle estimate/start output parity floor; feature half -> AF-BUNDLE-ALPHA docket
