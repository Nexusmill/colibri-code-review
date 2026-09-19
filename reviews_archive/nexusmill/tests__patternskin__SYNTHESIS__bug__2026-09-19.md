# SYNTHESIS: PatternSkin test surface (13 units, bug mode, 2026-09-19)

- model: claude-fable-5-1 - in-session colibri-review under the 2026-09-19 doctrine (tests are units)
- units: tests/_runtests.py, test_patternskin_math.py (delta), test_accel_tiers.py (delta), test_heightmap.py, test_ai_sdf.py, test_part_export.py, test_ai_select.py, test_blender_smoke.py, test_projections.py, test_projection_degeneracy.py, e2e_blender.py, harness/e2e/ps_e2e.py, harness/bpy_patternskin.py
- NOT scanned (named so the owner can extend): the ~130 files under tests/harness/probes/ (probe scripts), tests/gpu/*, tests/paths/*, tests/synthetic/*, and the non-PatternSkin tests (test_assetforge, test_skill_census, test_session_grounding_hook, test_watermark_robustness).
- externals (standing cadence, background): 4x GLM-5.3-flash via hy4-review, 7x grok-4.3, 1x grok-4.6 - 12 units, list-price a few cents each; 11 of their findings adopted after verification, 6 refuted with evidence, the rest not adopted as style/no-defect.

## Cross-file findings, ranked

1. **The PatternSkin test surface has no reliable red path outside the harness critic.** `_runtests.py` exits 0 on any failure; `e2e_blender.py` has no exit code; `test_patternskin_math.py` cannot fail under pytest (8 of 9 tests); `ps_e2e.py` exits 0 on an uncaught exception under plain `-P`; and `bpy_patternskin.py` + `runner.py` + `critic.py` grade the previous run's committed results file after a crash or a no-Blender run. Four different files, one class: PASS is the default and failure has to fight to be seen.
2. **The accel matrix has been dead on Windows since day one** (`test_accel_tiers.py:51`, a non-cp1252 glyph in the first label) - and even once it runs, its SciPy section measures numpy against numpy because the GROK-AC3 async-probe redesign moved the capability under the test. Both confirmed live. The K3 review of 2026-07-20 read the file and never ran it: reviews of tests must RUN the test.
3. **Tracked run artifacts.** `tests/_testresults.txt`, `tests/test_heightmap_results.txt`, `tests/test_projections_results.txt` and `tests/harness/results/*.json` are git-tracked and rewritten by every run; with `_git_do.py`'s `add -A` that is committed noise, and for the harness it is the stale-results hazard in (1). Decision needed: gitignore the results (and make the critic demand freshness) or keep them as committed evidence with a run-id stamp.
4. **Tests whose assertions cannot fail or test the wrong target:** `test_heightmap.py:17` (tautology), `test_blender_smoke.py:39` (lazy `bpy.ops` hasattr, verified in Blender 5.1.2), `bpy_patternskin.py:91` (PS-AA `or True`), `:149-151` (PS-SEAMLESS stem on a literal), `:464-471/553-559/648-655` (split rows without own evidence), `test_accel_tiers.py:88-94` (SciPy tier never engaged), `test_ai_select.py:47-56` (the bridge that is never built).
5. **Scratch dependencies:** PS-SPECTOR-BRIDGE (registry + tester) depends on `junk/_spector_bridge_t2_repro.py`, gitignored.
6. **Fixture leaks with real side effects:** PS-DEP-LOCK can leave a genuine pip install queued in the user's add-on config; temp-dir leaks in test_part_export.py and bpy_patternskin.py.

## Clean units
test_ai_sdf.py, test_projections.py, test_projection_degeneracy.py - real asserts, deterministic, load-bearing (projections' two July catches).

## Doctrine notes
- The `.mjs` half of today's ruling had nothing to scan in this repo (no .mjs/.cjs/.mts/.cts files outside ignored trees); the console scanner's `CODE_EXT` gap in colibri-code-review `scanner.py:6` stays owed.
- Reviewing a test without running it is how the accel crash survived a paid review; the test-unit bullet should be read as "run it if it is runnable" - proposed as the next doctrine amendment.
