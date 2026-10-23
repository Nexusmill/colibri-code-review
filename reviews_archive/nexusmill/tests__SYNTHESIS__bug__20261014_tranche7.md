# colibri bug hunt synthesis — PatternSkin test suite, tranche 7 (2026-10-14)

- date: 2026-10-14 · model: GLM-5.3-Flash (in-session) · mode: bug
- scope: seven root files — projections, projection_degeneracy, ai_sdf (same-sha cache-hit passes), watermark_robustness (same-sha pass2), blender_smoke (delta), assetforge + critic_freshness (fresh). Six run live: PASS, exit 0 each (blender_smoke static by design — needs `blender -b -P`).
- cumulative: 37 of 193; 36 of 38 ROOT suite files reviewed — remaining: skill_census, session_grounding_hook, zcode_hooks (dedicated final tranche) + the 116-file probe tree.

## Findings
1. **[LOW, NEW] watermark_robustness has no red-able threshold** (l.76-86) — the grid prints "Recovered tracer in N/M" and exits 0 regardless; as a suite test its green certifies only "ran without crashing". Live baseline 10/11. Fix: pin a minimum. The prior's 2 MEDIUMs (unclosed handles, /tmp/wm) stand against the same sha.
2. **blender_smoke delta: the prior MEDIUM (unfailable hasattr registration check) is FIXED** in current bytes (bl_rna_get_subclass_py l.41 + scar l.39-40); nothing new.
3. **projections / projection_degeneracy / ai_sdf: new: 0** — prior clean verdicts stand (the area_spread density method and metric-sanity anchors re-derived this pass).
4. **assetforge + critic_freshness: clean** (fresh reviews); assetforge's mkdtemp root leak noted.

## G35 closures
- assetforge row (Mock.generate + run_job docstring): verified-stale IN BOTH HALVES (extra=None scar l.28-32; library_gen.py:899 documents the contract).

## Cache-protocol note
This tranche applied the tranche-6 lesson UP FRONT: the full tests\-keyed manifest dump found the five prior rows before reading began — four same-sha cache-hits (pass2 lineage recorded, new findings only), one delta. No from-scratch re-review waste, no silent skips.
