Synthesis: bug hunt across every file modified since the last commit run (9a0ee6a..c2d2f34 -
the ROCm installer ship, the RDNA3 merge, the per-loop/cap-aware/BALL projection fixes)
Reviewer: claude-sonnet-5 (in-session)
Date: 2026-07-27
Files reviewed: PatternSkin/accel_bootstrap.py, PatternSkin/__init__.py,
PatternSkin/projections.py, PatternSkin/accel.py, tools/pin_py312.py,
tools/promote_captured_pins.py, tests/gpu/run_bootstrap_tests.py,
tests/test_projection_degeneracy.py, tests/test_projections.py.
Out of scope (data/logs, not code): gpu_accel_manifest.json, docs/*_manifest.json,
docs/AGENT_STATE.md, junk/* (scratch probes already run and recorded).

## Ranked findings (all CONFIRMED unless noted)

1. **[HIGH] Two concurrent installs can corrupt each other's shared Python-3.12 runtime cache.**
   `accel_bootstrap.ensure_python312()` acquires no lock at all, unlike its sibling
   `bootstrap_ml_venv()`. Reachable via a genuine race (two Blender instances) or via
   `PATTERNSKIN_OT_install_ml_worker.cancel()` in __init__.py clearing the `_ML_WORKER_INSTALLING`
   guard before the background thread has actually stopped. Files: accel_bootstrap.py (missing
   lock), __init__.py (early guard-clear that lets a second attempt start).

2. **[HIGH] The install lock's staleness reclaim has no heartbeat, so it can fire on a live,
   still-progressing install, not only an abandoned one.** The tier is 2.19 GB; on a slow
   connection the download alone can exceed the default `stale_after=3600s` while the process is
   still correctly working. A second attempt would then legitimately see the lock as stale, remove
   it, and start writing into the same paths. File: accel_bootstrap.py.

3. **[MEDIUM] Esc-cancellation is a no-op during the Python 3.12 resolve/download/extract phase.**
   `ensure_python312()` takes no `cancel_event` and never receives one, so the UI's "Cancelling..."
   status is false for however long that phase takes. Files: accel_bootstrap.py (missing param),
   __init__.py (call site never passes one, none exists to pass).

4. **[MEDIUM] `ensure_python312()` doesn't re-verify a cached archive's hash before extracting it,**
   unlike `bootstrap_ml_venv()`'s artifact loop, which treats the identical scenario (a file left
   over from an earlier run) as untrustworthy by design. Same file, same threat model, different
   answer. File: accel_bootstrap.py.

5. **[LOW, PLAUSIBLE - unverified]** Per-loop centroid/span statistics inside
   project_cylindrical/spherical/ball/swept are implicitly weighted by loop count (face corner
   count) rather than area, which could bias axis/origin detection on meshes with very uneven
   face topology. Could not construct a case where this visibly matters on the meshes this
   product targets. File: projections.py.

Everything else read - apply_pattern's per-loop rework, uv_collapse_ratio's handling of
partially-selected faces, `_load_preset`'s AUTO reset, accel.py's already-logged
worker_tier_gap fix, both tools/ scripts, and the test suite - held up under adversarial
re-tracing. No new findings there.

## What this means practically
Findings 1-2 both require either genuinely concurrent installs (two Blender instances, unlikely
but possible) or a slow-connection multi-GB download (plausible - some customers will be on
exactly this). None of the four HIGH/MEDIUM findings has fired in this session's own dogfooding
(one machine, one install, fast connection, gfx1200) - they are latent, not observed failures.
None are in docs/remediation_manifest.json yet, since none has been fixed - these are new
findings from today's hunt, not previously-known issues being re-flagged.

## Recommendation
Findings 1 and 2 are the ones worth fixing before this ships more broadly: they're both real
concurrency gaps in a path that downloads multi-gigabyte files onto a customer's machine. 3 and 4
are smaller (a UX lie during cancel; a defense-in-depth gap that needs external corruption to
matter). 5 needs a reproducer before it's worth touching at all.
