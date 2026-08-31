Source: PatternSkin/accel_worker.py
Reviewer: claude-sonnet-5 (in-session)
sha256: 5f9c334b23730c04d64670d50ec31fb0d993b85aea515e6174401c94a2139c3e
Date: 2026-08-06
Mode: bug (FIRST review - never in .colibri_reviews/_manifest.json or _hunt_plan.json)
Context pack: full 171-line file read; find_importers=0 (spawned as a subprocess via
_WorkerClient._spawn() in accel.py, not statically imported); confirmed sole caller is
accel.py's _WorkerClient (script_path defaults to this file, spawned with a fresh venv
interpreter, never Blender's own python); cross-read PatternSkin/accel.py::_nearest_numpy
and ::nearest (rank-3 unit, already reviewed/fixed 2026-07-24 for float32 catastrophic
cancellation) since this file has its own independent copy of the nearest-neighbour math -
traced the public entry point accel.py::nearest() to see whether the two implementations'
edge-case handling could ever diverge in a live-reachable way.

## Verdict
Shippable. No confirmed defect. One duplication-of-logic note worth flagging for future
maintenance (see below) and one hypothesis that traced clean through the actual call chain.

## Bugs & vulnerabilities
None confirmed.

Traced and REFUTED:
- Hypothesis: _nearest_numpy's `kk = max(1, min(int(k), T.shape[0]))` forces kk=1 even when
  T.shape[0]==0 (empty tree), and np.argmin() on a zero-length reduction axis raises
  ValueError, which would only be caught generically by _serve()'s per-op try/except and
  returned as an "error" frame (not a crash, but a spurious failure on legitimate empty input).
  REFUTED: accel.py::nearest() - the only code path that can ever reach this worker's "nearest"
  op - has its own explicit guard: `if len(tree_pts) == 0: raise ValueError(...)` BEFORE ever
  calling _worker_request(). The worker's op is unreachable with an empty tree in the current
  codebase. (accel.py's own in-process _nearest_numpy has the identical kk-clamp pattern and
  would have the identical crash-on-empty-tree if ever reached without that guard - it is
  covered by the same upstream check, not by anything in either _nearest_numpy.)

## Missing safeguards
- Logic duplication: this file's _nearest_numpy/_nearest_torch are a second, independently
  written implementation of the exact same k-nearest-neighbour math as accel.py's own
  _nearest_numpy/_nearest_mathutils (both float64-centered for the same catastrophic-
  cancellation reason, per accel.py's fix comment from the 2026-07-24 hunt). A future numerical
  fix applied to one copy (as already happened once, to accel.py's) has no mechanism forcing it
  to be mirrored here - the two are currently in agreement by inspection, but nothing enforces
  that they stay that way. Not a live bug; worth a shared-helper refactor if this file grows.
- main()'s srv.accept() is called exactly once (listen(1), single accept, no loop) with no
  handshake secret beyond the OS-assigned ephemeral port. On a shared/multi-user machine a
  different local process that guessed or scanned the port in the narrow window between spawn
  and Blender's own connect() could occupy the one accept slot, causing Blender's real
  connection to sit unserved until its own client-side timeout falls back to CPU. Bound to
  127.0.0.1 only (never 0.0.0.0) as documented; this is a local-multi-tenant edge case, not a
  network-facing one, and requires a malicious process already running as another local user.
  Traced as real but LOW severity - not reported as a bug.
