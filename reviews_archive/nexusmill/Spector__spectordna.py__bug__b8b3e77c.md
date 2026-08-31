Source: Spector/spectordna.py
Reviewer: claude-sonnet-5 (in-session)
sha256: b8b3e77c2016e184e56a187a9fcd838152937715fc6148c7a54fc43a2d14c743
Date: 2026-08-08
Mode: bug (STALE-FILE DELTA - reviewed against .colibri_reviews/Spector__spectordna.py__bug__
78ae1bec.md, 2026-07-20, moonshotai/kimi-k3; current on-disk sha did not match the cached
78ae1bec review, flagged in the prior Spector never-scanned-files sweep for a follow-up pass)
Context pack: full 125→141-line file read at dispatch; find_importers/search_text confirmed
callers - warehouse.py's _ingest_locked/inspect/_find_locked all call shape_dna() with only
k/scale_invariant varied, NEVER engine (app.py never exposes engine as a request parameter
either, so the bogus-engine finding below has no live production trigger today); dna_distance/
nearest have ZERO production callers - index.py's SearchIndex independently reimplements the
same weighted-L2 metric, so these two functions are effectively test-only dead code in the
current architecture. cotan_laplacian is only ever reached via _laplacian, itself only ever
reached via shape_dna, so shape_dna's input-validation gate covers the whole numerical path.
Checked docs/remediation_manifest.json (no prior fix entries existed for this file before this
session) and Spector/tests/ (test_spectordna.py, test_regressions_0701.py, test_warehouse.py)
for existing coverage. Numerical claims (scale invariance, multi-component zero-padding, the
engine/empty-vector behaviors) were verified by EXECUTION against the real module via
Spector/.buildenv/Scripts/python.exe (has scipy + robust_laplacian), not by inspection alone -
see junk/hunt_verify_spectordna.py (pre-fix) and junk/hunt_verify_spectordna_postfix.py
(post-fix), plus a full run of the project's own three test files.

## Verdict
The prior review's biggest risk ("silent corruption of the fingerprint database") is now
substantially reduced: 3 of its 4 MEDIUM findings are fixed this session (the 4th, negative
face-index wrapping, was ALREADY fixed by an earlier untracked commit before this session even
started). Both LOW findings addressed this session that had live behavioural evidence
(multi-component zero-padding, unhandled ARPACK failure) are fixed with proof; two remaining
LOW items (the zero-mode tolerance heuristic, unbounded cotangent weights on sliver triangles)
are numerical-methods judgment calls left open deliberately - see below.

## Fixed since last review (2026-07-20, 78ae1bec)

**Already fixed before this session (verified by inspection, not re-litigated as new):**
- Negative/out-of-range face indices now raise `ValueError` (shape_dna validates `F.min()`/
  `F.max()` against `len(V)` before ever reaching the Laplacian assembly).
- NaN/Inf vertex coordinates now raise `ValueError` (explicit `np.isfinite(V).all()` check).
- The all-near-zero-spectrum fallback that used to silently keep numerical noise (`vals =
  vals[1:]`) now raises `RuntimeError("no nonzero Laplacian modes...")` instead.

**Fixed THIS session (see docs/remediation_manifest.json 2026-08-08 for the 3 entries):**
- **[MEDIUM] Multi-component zero-padding** - the fixed `+16`-mode margin (itself a partial
  mitigation of the original K3 finding, upgraded from the original `+1`) is replaced with
  exact connected-component counting (`scipy.sparse.csgraph.connected_components`), so `kk = k
  + n_components` guarantees `k` real modes survive regardless of shell count. Verified: a
  synthetic 20-shell mesh went from 4 silently-zero-padded entries (pre-fix) to 0 (post-fix); a
  60-shell stress case (far past the old fixed margin) also 0.
- **[LOW] ARPACK non-convergence unhandled** - `eigsh()` is now wrapped; `ArpackNoConvergence`
  re-raises as a `RuntimeError` naming the vertex count and requested mode count.
- **[LOW] Bogus `engine` string silently acted like `"cotan"`** - now raises `ValueError` for
  anything not in `("auto","cotan","robust")`. Confirmed unreachable via any current production
  call site, but closes the public-API contract gap.
- **[LOW] `dna_distance` returned 0.0 (a "perfect match") for two empty vectors** - now raises
  `ValueError`. `dna_distance`/`nearest` have no production callers today, so this has no live
  behavioral effect, but closes the gap for future callers / the .spectorpack-import threat
  model (a corrupt/empty DNA blob would otherwise sort as the best match).

## Still open (unchanged from the 2026-07-20 review - deliberately not touched this session)

**[MEDIUM] Zero-mode tolerance can silently discard genuine low eigenvalues** - `line 111`
(`tol = max(float(vals[-1]) * 1e-8, 1e-12)`). Unchanged. Re-confirmed present by inspection.
Not fixed: changing the tolerance FORMULA is a numerical-methods judgment call, not a clear bug
fix - it directly changes what counts as a "real" eigenvalue and would risk shifting the
computed DNA for already-ingested parts (breaking re-ingest/dedup comparability against
existing library rows) if gotten wrong. Recommend logging to docs/deferred_manifest.json for a
dedicated pass (the original review's suggested alternative - an absolute threshold tied to the
solver's shift `sigma`, or explicit connected-component detection - is exactly what THIS
session's fix now does upstream in `kk`'s computation, which may already reduce this finding's
practical bite since real zero-modes are now reliably separated from the k real ones by
construction; not independently re-verified against the tolerance formula itself).

**[LOW] Degenerate/sliver triangles get unbounded cotangent weights** - `cotan_laplacian`,
`line 38` (`np.maximum(np.linalg.norm(np.cross(u,v),axis=1), 1e-12)`). Unchanged, re-confirmed
present by inspection. Not fixed this session - same reasoning as above (a numerical clamp
choice, not a clear-cut defect; the module docstring already states clean/manifold meshes are
the "Clean-mesh path" and robust_laplacian is the DEFAULT/preferred engine specifically for
messier geometry per `_laplacian`'s `want_robust` logic, which partially mitigates real-world
exposure to this cotan-specific issue).

## Missing safeguards
- `dna_distance`/`nearest` are dead code in production (0 callers outside tests) - index.py's
  `SearchIndex` independently reimplements the identical weighted-L2 metric. Not a bug, but the
  same duplication-of-logic risk already flagged elsewhere in this sweep (accel_worker.py vs.
  accel.py's nearest-neighbour math): if one implementation is ever tuned, nothing forces the
  other to follow, and `SearchIndex`'s copy is the one that actually matters for search quality.
- Isolated vertices (present in `V`, never referenced by `F`) get a floored mass of `1e-12` in
  `cotan_laplacian`, which can make the generalized eigenproblem ill-conditioned rather than
  being detected/stripped. Carried forward from the 2026-07-20 review, unchanged.
