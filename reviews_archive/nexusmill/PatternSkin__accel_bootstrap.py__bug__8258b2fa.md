# Colibri Review - bug (perfection run 4, R1) - PatternSkin/accel_bootstrap.py

- **Source path:** `PatternSkin/accel_bootstrap.py`
- **Reviewer:** zcode GLM-5.3 main (in-session), Colibri G37 protocol inside perfection v3; adversary gate = gpt-6-luna-pro (different model, full credit)
- **sha256 reviewed:** run opened at `fdbc5b143baa4f51b981c6d880c1aa71696d2c4a3395cf1bab57b754cb6f70de` (sha8 fdbc5b14); wave landed at sha8 8258b2fa (commit ec9a6ffc)
- **Date:** 2026-09-28 · **Mode:** bug, perfection protocol (postures A-D + gate rounds)
- **Context pack:** all 894 lines read at the opening sha; sole external edge = `__init__.py` (~17 call sites, PATTERNSKIN_OT_install_ml_worker + panel); 13 prior manifest rows (all fixed); prior lineage 2026-08-06 + 2026-08-15 GLM-AB + 2026-09-10 FULL re-audit (sha8 21afa6a5); twin `blender_dev/addons/PatternSkin/accel_bootstrap.py` = same physical file (junction ancestor, sha identical at open and at landing); battery tests/gpu/run_bootstrap_tests.py + tests/test_accel_tiers.py.

## Verdict
Three LOW fixes landed (arch-gated interpreter probe; https->http redirect refusal at every hop; capture-shape guard), two of them gate-driven amendments (G-HOP HIGH, G-ARM MEDIUM). Four adjudication classes carry rows (cancel-in-pip bounded by subprocess timeouts; SP-BUILD-PINS transitive-deps G17 gap deferred with unblock condition; DRV-DATE-VER-1 existing docket; input-space class). Two candidates REFUTED at the bytes (progress total=0 - consumer guards `elif total:`; heartbeat residual - requires utime to fail persistently while os.replace succeeds, contradictory handle modes). Local-zero: two passes on sha 8258b2fa, pass 2 fresh (resolved the urllib.parse closure-capture question in the handler with mechanism; verified at three test layers).

## Findings landed (see docs/remediation_manifest.json rows, commit ec9a6ffc)
1. PS-AB-BITNESS + G-ARM - probe reports version+bits+machine; predicate accepts 3.12/64/AMD64|x86_64 only.
2. PS-AB-REDIRECT-DOWNGRADE + G-HOP - _make_downloader handler refuses any https->http hop; final-URL backstop retained.
3. PS-AB-CAPTURE-SHAPE - wrong-shape capture files reset instead of crashing.

## Gate saga (gpt-6-luna-pro)
- BLOCK gate_20260928-140001: G-HOP (HIGH, chain passes final-URL check) ACCEPTED+fixed; placeholder-address MEDIUM = IP-literal transport artifact (rebutted).
- BLOCK gate_20260928-140642: dispatched context-less (a %-format error killed the context write - G33 lesson in python form); re-raised the artifact identically.
- BLOCK gate_20260928-140805: G-ARM (ARM64 also 64-bit) ACCEPTED+fixed; artifact re-raised despite byte-evidence rebuttal (undecidable at reviewer layer).
- CLEAR gate_20260928-141517 on the final diff (bind refactored to hostname-resolved - no address literal left to redact).

## Adjudications (LEDGER rows)
ADJ-1 cancel-in-pip/create_venv (bounded 1800/300s; Esc lands at next artifact boundary; Popen restructure = G41 introduction risk). ADJ-2 SP-BUILD-PINS/accel_bootstrap instance (needs a real 2 GB resolve for constraints; blind --no-deps breaks torch). ADJ-3 DRV-DATE-VER-1 (existing open docket row). ADJ-4 input-space class (relative venv_dir, URL query-string basename, DLL basename collision - internal callers only).

## Battery
tests/test_perfection_accel_bootstrap.py 18/18 GREEN (RED transcripts on pre-fix and pre-amendment bytes); mutation ledger F1(bitness)/F1(arm)/F2(redirect)/F2(hop)/F3(shape) all flip exactly the predicted rows; run_bootstrap_tests.py all-green; test_accel_tiers.py ALL PASSED; pyflakes/py_compile clean. Full suite 30/32 at baseline with both failures characterized (numpy-2/pip-bpy environment flakes, pass standalone, zero accel_bootstrap frames).
