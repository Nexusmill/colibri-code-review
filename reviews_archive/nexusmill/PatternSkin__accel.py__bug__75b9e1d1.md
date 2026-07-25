# colibri-review — PatternSkin/accel.py — bug (DELTA, hunt round 1)

- **Source:** PatternSkin/accel.py · **Model:** claude-opus-4-8[1m] (in-session, max) · cost $0.00
- **sha256 reviewed:** 75b9e1d1e286c2d92719bb0e70c25d6369b8328073463e1134dd0e10920aa113 (53.7 KB)
- **Date:** 2026-07-23 · **Mode:** bug · **DELTA** against `PatternSkin__accel.py__bug__f6decaed.md`
- **Delta scope:** prior-review bytes = commit `2d6b146`; this pass = `2d6b146..HEAD` = **547 insertions /
  74 deletions**. The bulk is a 384-line "runtime observability + controls" block (tier override,
  fallback logging, diagnostics export, GPU memory mgmt, NN-tree cache, caps observer, benchmark,
  warmup, env knobs) plus k>1 support in `_nearest_numpy`/`_nearest_mathutils` and a `_PREFER_TIER`
  path in `get_xp`.
- **Context pack:** hunt loader (no prior refuted claims, no remediation rows for this file); the
  k>1 NN path is the one `projections.project_swept3d` depends on (`accel.nearest(cl, cl, k=k)`);
  `finish_pending_installs` pip path (security-relevant); `capabilities()` cache + `_invalidate_caps`.
  Current bytes re-hashed at dispatch (G36). Findings verified by execution (`junk/_accel_probe.py`).

## Verdict
Shippable after one small fix. The additive layer is careful — every backend touch is wrapped,
GPU paths no-op on CPU, the pip installer is allowlisted, and the NN cache keys on a content hash
(a prior `sum()`-overflow footgun explicitly avoided). One documented env knob crashes module import;
everything else I probed held up.

## Bugs & vulnerabilities

**[LOW] A negative `PATTERNSKIN_EVENT_LOG_MAX` crashes `import accel` — can brick the whole add-on** - `line ~1020` (`_EVENTS = _collections.deque(maxlen=_config("event_log_max", 80))`)
- **What:** `_config` returns the env value as an `int` with no lower bound. `deque(maxlen=-1)`
  raises `ValueError: maxlen must be non-negative` at module-load time. `EVENT_LOG_MAX` is listed
  in `_config`'s own docstring as a supported knob.
- **Trigger:** `PATTERNSKIN_EVENT_LOG_MAX` set to any negative integer, then Blender loads the
  add-on (`__init__` imports `accel` at register).
- **Impact:** the import raises, so the acceleration module — and the add-on that imports it — fails
  to load. A configuration mistake becomes a hard failure instead of graceful degradation
  (violates the works-out-of-the-box / graceful-fallback posture the rest of this file embodies).
- **Verified CONFIRMED by execution:** `import accel` with `PATTERNSKIN_EVENT_LOG_MAX=-1` raised
  `ValueError: maxlen must be non-negative`.
- **Fixed:** `maxlen=max(0, int(_config("event_log_max", 80)))` — 0 keeps no events (still valid),
  negatives clamp. Re-probe: import now survives the bad knob.

## Missing safeguards
- `benchmark_tiers` calls `cKDTree(...).query(..., workers=-1)`; on SciPy < 1.6 that `TypeError`
  is caught and reported as `"error: ..."`, so it degrades — but the same version guard
  (`try/except TypeError` re-query) used elsewhere would be tidier. Not a defect.
- `diagnostics()` documents "never raises" and wraps most calls in `_safe`, but calls
  `recommend_cached()` directly; that function only returns a module global, so it cannot raise —
  safe today, fragile if it grows logic. Noted, not fixed.

## Refuted during verification (recorded in `_refuted_ledger.json`)
- *"`_nearest_numpy(k=k)` — the signature has no `k`, so k>1 callers (swept3d) hit a TypeError"* —
  the current signature IS `_nearest_numpy(tree_pts, query_pts, max_bytes=None, k=1)`; the diff
  header showed the old context line. Probed: the k>1 path returns shape `(n,k)`, nearest-first,
  distances matching brute force. The projections dependency is sound.
- *"`gpu_healthy` unpacks `get_xp()` as a 3-tuple but `get_xp` may return 2"* — `get_xp` returns
  `(xp, to_cpu, tag)` on every one of its four return paths. No arity mismatch.
- *"`_invalidate_caps` locks `_CAPS_CB_LOCK` while `capabilities()` writes `_CAPS` lock-free — a
  race"* — reference assignment is atomic under the GIL and the read path already takes a local
  `c_snap` copy to tolerate `_CAPS` going `None` between check and use. The lock is redundant, not
  a correctness defect.
- *"`finish_pending_installs` pip-installs names from a file on disk → arbitrary-package RCE"* —
  it enforces `if pkg.lower() not in INSTALL_ALLOWLIST: continue` ({cairosvg, scipy, torch-directml}),
  runs `--only-binary=:all:`, and the file lives in the user's own `~/.patternskin` (no cross-user
  write). No injection path.
