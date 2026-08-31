# Colibri fix-pass record - PatternSkin/accel_bootstrap.py (GLM-AB)
- source: PatternSkin/accel_bootstrap.py
- model: claude-fable-5 (in-session)
- sha256: b49d0864eba763536b3cce0674fcd6178fdd0ba03319c108bb818ea6318dbfb0
- date: 2026-08-15
- mode: fix (GLM-AB findings 1-6 + 2 safeguards)
- context pack: the GLM 5.3 review (.glm_reviews/PatternSkin__accel_bootstrap.py__bug__2eeb0332.md,
  colibri-gated same day, zero refuted); file unchanged between gate and fix (2eeb0332); ledger
  remediations (multi-artifact gating, per-venv locks, heartbeat, cancel plumbing) all preserved.

## Verdict
All six findings + both safeguards fixed; battery 9/9 with live threads and mocked os
primitives. The probe hang lesson: never test subprocess timeouts with a real hanging
.bat on Windows (grandchild pipes wedge capture_output) - patch subprocess.run.

## Fixed since last review
- GLM-AB #1 undeletable-stale busy loop -> deadline+sleep fall-through
- GLM-AB #2 heartbeat permanent death -> gone-only exit
- GLM-AB #3 TimeoutExpired contract escape -> BootstrapError wrap x2
- GLM-AB #4 PS apostrophe break -> env-var listfile
- GLM-AB #5 shared .partial interleave -> pid-suffixed partials
- GLM-AB #6 capture-mode blind reuse -> byte-count + observed-hash record
- safeguards: atomic _record_capture; lock fd close in finally
