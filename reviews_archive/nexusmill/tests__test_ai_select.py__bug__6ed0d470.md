# BUG review: tests/test_ai_select.py

- source: `tests/test_ai_select.py`
- model: claude-fable-5-1 (in-session, colibri-review protocol)
- sha256: `6ed0d4705c9e37a0a9e80ff89d257cff3d7cb01f8aab3ead0a4b000e38b437fe`
- reviewed: 2026-09-19 07:25
- mode: bug (test-unit hunt per the 2026-09-19 doctrine: tests are units)
- context pack: contract sources ai_select.look_at_basis (38), project_points (57), lift_masks_to_parts (138), assign_unseen_to_parts (180), auto_min_views (268), flood_unseen_geodesic (216), selectcore.MeshCtx (32) - signatures verified against every call; remediation rows 2026-07-25 (PSK-SEG-1); live run PASS (geodesic=1.000 vs bfs=0.537).

---
## Verdict
Green, seeded, real asserts. One test does not build the scenario its own comment and name promise.

## Bugs & vulnerabilities

**[MEDIUM] `test_single_bridge_does_not_fuse` never builds the bridge it is named for** - `line 47-56`
- What: the comment (48) promises "two clean parts, ONE noisy bridge view on the boundary must NOT fuse them"; the body (52) tiles PERFECT labels into all 12 views. The assert (55) therefore only proves that `lift_masks_to_parts` keeps two clean parts apart - the anti-fusion behaviour under a noisy bridge view is untested, and the name/comment are stale.
- Fix: in exactly one view, flip the labels of the faces whose dual edge straddles x=0.5 (a real bridge), keep the other 11 views at truth, keep the assert. If that fails, it is a product finding - do not weaken the assert.

## Missing safeguards
- The `__main__` chain (98-100) stops at the first failure (LOW; exit code honest).

## External second opinions (grok-4.3, background)
- The missing bridge - adopted (verified by reading lines 48 vs 52).
