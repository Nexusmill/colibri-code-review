# Colibri Review - bug (DELTA) - PatternSkin/accel_bootstrap.py

- **Source path:** `PatternSkin/accel_bootstrap.py`
- **Reviewer:** claude-fable-5-1 (in-session), Colibri G37 protocol, campaign item 1 (product cores), rank 46
- **sha256 reviewed:** `b49d0864eba763536b3cce0674fcd6178fdd0ba03319c108bb818ea6318dbfb0` (sha8 `b49d0864`) - the PRE-fix bytes
- **Date:** 2026-09-10 · **Mode:** bug, stale-file DELTA against `2eeb0332` (2026-08-06 review; the GLM-AB fix pass `b49d0864` of 2026-08-15 is the delta)
- **Delta reviewed:** 1 commit / 165 diff lines: c0a7a75c (GLM-AB #1 undeletable stale lock no longer spins, #2 heartbeat survives a transient utime failure, #3 timeouts raise BootstrapError, #4 Authenticode list path via env var, #5 per-process partial name, #6 unpinned on-disk artefact verified/captured, capture file written atomically, fd closed on a write raise) - every hunk read.
- **Context pack:** the prior review record(s) for the file, `docs/remediation_manifest.json` rows from 2026-07-24 on, `docs/deferred_manifest.json`, `_hunt_plan.json` + `_refuted_ledger.json` loaded; jCodemunch `get_symbol_source` on the symbols each finding depended on.

## Fixed since last review
- Every remediation row dated after the base review was verified present at the bytes (they are the delta).

## Verdict
Shippable after the one fix below (applied this session, RED-first). The GLM-AB lock state machine reads correct at the bytes; the one gap is a side effect of its own #5.

## Bugs & vulnerabilities

**[LOW] Per-process partial downloads orphan on a hard kill** - `download_and_verify`, the `partial = "%s.%d.partial" % (dest_path, os.getpid())` line (GLM-AB #5)
- What: the staging name became per-process to stop two bootstraps interleaving one file. The function removes its own partial on any exception, but a HARD kill (Blender crash, power loss mid-download) leaves `<dest>.<pid>.partial` behind, and nothing sweeps such siblings - the old fixed name was simply overwritten by the next attempt.
- Trigger: a crash or forced exit while the multi-GB AMD worker artefacts download.
- Impact: up to the artefact's size (the tier is ~2 GB) left in `~/.patternskin/wheels_ml` per crashed attempt, forever.
- Fix (applied): before opening its own partial, `download_and_verify` removes sibling `<dest>.*.partial` files older than an hour (a live download touches its file continuously), never its own, and a sweep failure never blocks the download. Battery `tests/harness/probes/sweep_accel_bootstrap_r3.py` (pure python, file:// URL): a two-hour-old sibling is removed while a fresh one survives (watched RED), and a denied removal still lets the download verify; GREEN after; `glm_ab_lock.py` still ALL PASS.
- Verification: CONFIRMED by structure (no sweep anywhere in the module) and by the reproducer.

## Remediation postscript (same session)
The fix was applied after this review hashed the bytes above; the file is now `21afa6a59c6644ba437a5b9fcc5a7914200df2278f4ac8c37b286beb5617f533`. Row PS-PARTIAL-ORPHAN-SWEEP in `docs/remediation_manifest.json`, same commit.
