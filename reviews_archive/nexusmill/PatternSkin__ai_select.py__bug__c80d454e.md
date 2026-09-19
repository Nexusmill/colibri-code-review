# Colibri Review - bug (DELTA) - PatternSkin/ai_select.py

- **Source path:** `PatternSkin/ai_select.py`
- **Reviewer:** claude-fable-5-1 (in-session), Colibri G37 protocol, campaign item 1 (product cores), rank 8
- **sha256 reviewed:** `c80d454e1272556469cb0bc8ce89e0f21b388b79bd3a854f9b9a7c0b9fd1593e` (sha8 `c80d454e`)
- **Date:** 2026-09-10 · **Mode:** bug, stale-file DELTA against `bb03bb4e` (2026-07-23 hunt round 1)
- **Delta reviewed:** 4 commits / 161 diff lines: 64c7a0ab (`flood_unseen_geodesic` watershed + `auto_min_views`), 60bbde28 (GLM-POLISH length checks, `same` requires labelled faces), 7b56acd9 (GROK-AIS3 bounds guard + wave BFS), 83d109f8 (GLM-R2 the same guard in `auto_min_views`) - every hunk read.
- **Context pack:** the prior review record(s) for the file, `docs/remediation_manifest.json` rows from 2026-07-24 on, `docs/deferred_manifest.json` rows naming the file, `_hunt_plan.json` + `_refuted_ledger.json` loaded; jCodemunch `get_symbol_source` on the call sites each finding depended on.

## Fixed since last review
- Every remediation row dated after the base review was verified present at the bytes (they are the delta).

## Verdict
Clean at the delta. `csgraph.dijkstra(min_only=True, return_predecessors=True)` returns (dist, predecessors, sources) and the code unpacks exactly that; out-of-range dual edges are filtered before the graph is built and raise loudly in the two paid-data merges; the wave BFS relaxes each edge a bounded number of times and stays deterministic (sorted frontiers, `np.unique` tie-break).

## Bugs & vulnerabilities
None confirmed at the delta.

---

# FULL re-audit 2026-09-10 (appended - the record above predates the adversarial gate and is kept as history, not as baseline)

# Colibri Review - bug (FULL re-audit) - PatternSkin/ai_select.py

- **Source path:** `PatternSkin/ai_select.py` (junction twin `blender_dev/addons/PatternSkin/ai_select.py`, same bytes)
- **Reviewer:** claude-fable-5-1 (fork of the lead session), Colibri G37 protocol, campaign item 1 (product cores), rank 8
- **sha256 reviewed:** `c80d454e1272556469cb0bc8ce89e0f21b388b79bd3a854f9b9a7c0b9fd1593e` (sha8 `c80d454e`)
- **Date:** 2026-09-10 · **Mode:** bug, FULL review of the current bytes (owner ruling 2026-09-10: the 07-20..08-26 audits predate the adversarial gate and cannot be trusted - no delta against them)
- **Context pack:** all 398 lines read; every caller in `ai_parts.py` located (`look_at_basis` :30, `fibonacci_viewpoints` :636/:678/:791/:1170, the lift->flood->refine pipelines at :703-709, :723-726, :874-879, :900-905, :1439, :1780) and the consumer contract on the Blender side read: `_ai_polypart_read` (`__init__.py:8195`, per-polygon int32, -1 = unassigned) and `_ai_select_polypart` -> `_ps_apply_face_selection` (:8368-8372, :6301-6324: all-domain release, exactly `polypart == part`); the 7 remediation rows (07-20 basis + edge validation + `assign_unseen` bounds, 07-25 PSK-SEG-1 flood/auto_min_views, GLM-POLISH length checks + `same >= 0` guard, GROK-AIS3 lift guard + wave BFS, GLM-R2 `auto_min_views` guard) each re-verified present at the bytes.

## Verdict
Clean at the full read. The dual-edge validation is loud where the paid data flows (`lift_masks_to_parts`, `auto_min_views`, `refine_parts_by_geometry`) and tolerant where a skip is safe (`assign_unseen_to_parts`, `flood_unseen_geodesic`); the multi-source Dijkstra watershed, the wave BFS, the fragment merge and the re-packing all trace end to end; the selection contract with `__init__` is exclusive by construction (the canonical selector releases every domain before setting exactly the part's faces).

## Bugs & vulnerabilities
None confirmed.

## Missing safeguards (not fixed)
- `_merge_fragments` (:132-134) applies the good pairs of one iteration sequentially, so a chain (1,3),(3,5) in the same pass merges 3 into 1 and then relabels 5 as "3": the merge (1,3') is only re-tested on the next iteration. Bounded by `max_iter=64` and re-evaluated against the true aggregated boundary, so the final partition is correct - a possible extra iteration, not a wrong merge.
- `coarsen_labels` returns unpacked labels on its early exit (`len(u) <= target`) although the docstring promises 0..k-1; every caller feeds it `lift`'s packed output.
- `refine_parts_by_geometry` floods every never-visible face (-1 rows are singleton components below `min_faces`); by design after `flood_unseen_geodesic`, but a caller that skips the flood gets -1 faces relabelled silently.
- `project_points` and `_otsu` have no callers (dead code).

## Adversarial verification pass (refuted claims - deleted from findings)
- "`flood_unseen_geodesic` uses the Dijkstra `sources` array as an index into `indices`" - refuted: SciPy's `min_only=True` returns graph node indices; `labels[src[miss]]` is correct.
- "`lift_masks_to_parts` merges never-seen faces into parts" - refuted: `comp[~seen_any] = -2` before the merge and `m` requires both labels `>= 0`.
- "`auto_min_views` can return 0 and open the gate to zero-evidence edges" - refuted: `best = 1` floor, loop from 2.
- "`look_at_basis` degenerates for a camera straight above the model" - refuted: the `|fwd . up| > 0.999` branch swaps the up axis; the second `rn < 1e-9` check is unreachable after it but harmless.
- "`_sdf_levels` k-means leaves an empty cluster and divides by zero" - refuted: empty clusters keep their centre (`else centers[j]`).
- "`refine_parts_by_geometry` cuts on `sd` when `sdf` is None" - refuted: `sd` becomes zeros, `|dSDF| > step` never fires, and the thin-split branch is guarded by `sdf is not None`.
