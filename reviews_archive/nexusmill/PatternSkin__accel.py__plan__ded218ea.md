# PatternSkin/accel.py - remediation plan (colibri plan mode, in-session)
source: PatternSkin/accel.py sha256 ded218ea37a3e563 | model: claude-fable-5 (in-session)
date: 2026-08-30 | mode: plan (PLANS ONLY - execution is a separate TDD tranche, G35)
scope: EXACTLY the two gated findings HY4-ACCEL-PROBETIMEOUT + HY4-ACCEL-KCLAMP.
independence note: written from the current bytes only; grok's plan unread at authoring
time; hy4's PROBETIMEOUT item was partially seen earlier during the smoke (disclosed) -
everything here is re-derived from source, and the KCLAMP design below deliberately
differs from the docketed sketch after reading the whole call path.

### HY4-ACCEL-PROBETIMEOUT - wire the documented knob
- Objective: `PATTERNSKIN_PROBE_TIMEOUT` is promised in `_config`'s docstring (:1303-1304)
  but no probe consults it; timeouts are hardcoded.
- Root cause: `probe_scipy` (:183) and `probe_cairosvg` (:355) pass literal `90`,
  `probe_gpu_stack` (:538) passes literal `240`, straight into `_retry_run`.
- Fix design (smallest): at each of the three sites replace the literal with
  `_config("probe_timeout", 90)` (and `..., 240` at :538). `_config` already types by the
  default (int parse, garbage -> default, empty -> default), so no new validation code.
  SEMANTICS TO DOCUMENT in the docstring line: (1) ONE knob overrides ALL THREE probes -
  setting it raises the scipy/cairo deadlines and can LOWER the gpu one below 240; that is
  the documented contract of a single PROBE_TIMEOUT (dual knobs rejected: YAGNI, the doc
  promises one). (2) `_retry_run(attempts=2)` retries transient failures, so worst-case
  wall time is ~2x the knob - state it, don't change it.
- Test first (RED before the fix): `tests/harness/probes/accel_probe_timeout.py`, the
  repo's stub-import pattern (pskpkg + bpy stubs, as sam3_emptyzip_fixes.py does; accel
  probes also need `ensure_dep_path` left intact - it is pure sys.path work). Monkeypatch
  `ap._retry_run` with a recorder returning `types.SimpleNamespace(returncode=1, stdout=b"",
  stderr=b"")` and assert the THIRD positional arg (timeout):
    A. env unset -> probe_scipy 90, probe_cairosvg 90, probe_gpu_stack 240
    B. PATTERNSKIN_PROBE_TIMEOUT=7 -> all three record 7        (RED today: 90/90/240)
    C. PATTERNSKIN_PROBE_TIMEOUT=junk -> defaults again (typed-parse fallback)
  The battery appends a spec_results row SPEC-PS-ACCEL-PROBETIMEOUT-01.
- Steps: 1 write battery, run RED (case B fails). 2 edit the three sites via safe-edit.
  3 battery GREEN. 4 amend the `_config` docstring with the two semantic notes.
- Verification: battery green; `python -m tests.harness.runner --tiers gpu` still green
  (probes unchanged on the default path); py_compile via safe-edit gate.
- Risk & rollback: three call sites, no callers pass timeouts in; a user who exported a
  low PROBE_TIMEOUT could newly fail the gpu probe - covered by the documented single-knob
  semantics. Rollback = revert the three lines.

### HY4-ACCEL-KCLAMP - clamp k ONCE, at the top of nearest()
- Objective: `k > len(tree_pts)` yields out-of-bounds indices from the scipy branch
  (cKDTree pads misses with index == m), while numpy/mathutils clamp internally.
- Root cause: the docketed sketch (clamp the scipy branch, :923) is INSUFFICIENT once you
  read the whole function: `nearest()` (:901) tries `_worker_request("nearest", ...,
  meta={"k": k})` FIRST - the worker tier runs scipy in a subprocess and would return the
  same out-of-bounds padding with a scipy-branch-only fix. The asymmetry is a function-
  level problem, not a branch-level one.
- Fix design (smallest CORRECT): one line after the empty-tree guard (:908):
      k = max(1, min(int(k), len(tree_pts)))
  This heals all four paths (worker, scipy, numpy, mathutils) at once. Leave the internal
  `kk` clamps in `_nearest_numpy` (:955) and `_nearest_mathutils` (:976) as defense in
  depth. Amend the docstring: "k is clamped to len(tree_pts); k>1 returns (n, min(k, m)),
  nearest-first" - the uniform contract all backends already share below the clamp.
- Test first (RED before the fix): same battery file, second section:
    A. recorder on `ap._worker_request` -> nearest(5-pt tree, q, k=9) must send
       meta["k"] == 5                                            (RED today: sends 9)
    B. `_nearest_numpy(5-pt, q, k=9)` -> shape (n,5), every index in [0,5) (born green -
       regression pin)
    C. if real scipy imports in the battery env: force the scipy branch (monkeypatch
       `ap.capabilities` -> {"scipy": True, ...}, `ap._worker_request` -> None) and assert
       nearest(..., k=9) == the numpy result, shape (n,5), all indices < 5
       (RED today: scipy returns index 5 padding)
  Rows SPEC-PS-ACCEL-KCLAMP-01.
- Steps: 1 battery RED (A always; C when scipy present). 2 insert the clamp line +
  docstring amendment via safe-edit. 3 battery GREEN. 4 (worker parity) no worker-side
  change needed - the clamped k rides the meta.
- Verification: battery green; `--tiers gpu` equivalence tier green; spec tier green.
- Risk & rollback: shape change ONLY for the previously-broken k>m case ((n,k)-with-
  garbage -> (n,m)-valid); no caller passes k>m today (the landmine was future-facing);
  k=1 1-D contract untouched. Rollback = remove one line.

## Execution order & batching
One commit: "fix(accel): wire PROBE_TIMEOUT + clamp k at nearest() top" - both are small,
same file, one battery file, remediation_manifest rows same-commit, registry PS-ACCEL-*
expected rows updated same-commit (covenant). HY4-ACCEL-WARMLOCK stays a SEPARATE tranche:
it needs Damien's ordering ruling (gate-behind-pending vs row amendment) before code.
