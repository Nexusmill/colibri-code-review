# Colibri Review - bug (DELTA) - PatternSkin/accel_worker.py

- **Source path:** `PatternSkin/accel_worker.py`
- **Reviewer:** claude-fable-5-1 (in-session), Colibri G37 protocol, campaign item 1 (product cores), rank 48
- **sha256 reviewed:** `0a1c12bb911e9948ed003c4ec76a3bdee86ee4b6546dbc79d3eef48a6285e764` (sha8 `0a1c12bb`)
- **Date:** 2026-09-10 · **Mode:** bug, stale-file DELTA against `5f9c334b` (2026-08-06 review)
- **Delta reviewed:** 1 commit / 62 diff lines: 2a06c299 (GLM-IPC one-shot token handshake: only the connector presenting the argv token owns the worker; impostors are dropped and the accept loop keeps listening within the deadline) - every hunk read.
- **Context pack:** the prior review record(s) for the file, `docs/remediation_manifest.json` rows from 2026-07-24 on, `docs/deferred_manifest.json`, `_hunt_plan.json` + `_refuted_ledger.json` loaded; jCodemunch `get_symbol_source` on the symbols each finding depended on.

## Fixed since last review
- Every remediation row dated after the base review was verified present at the bytes (they are the delta).

## Verdict
Clean at the delta - `socket.timeout` on the token read is an OSError and is caught; a legacy tokenless launch keeps the old behaviour; the loop is bounded by the accept deadline.

## Bugs & vulnerabilities
None confirmed at the delta.

---

# FULL re-audit 2026-09-10 (appended - the record above predates the adversarial gate and is kept as history, not as baseline)

# Colibri Review - bug (FULL re-audit) - PatternSkin/accel_worker.py

- **Source path:** `PatternSkin/accel_worker.py` (junction twin `blender_dev/addons/PatternSkin/accel_worker.py`, same bytes)
- **Reviewer:** claude-fable-5-1 fork (in-session), Colibri G37 protocol, campaign item 1 (product cores), rank 48
- **sha256 reviewed:** `0a1c12bb911e9948ed003c4ec76a3bdee86ee4b6546dbc79d3eef48a6285e764` (sha8 `0a1c12bb`)
- **Date:** 2026-09-10 · **Mode:** bug, FULL review of the current bytes (owner ruling 2026-09-10: the 08-06 review and the 08-15 GLM-IPC round predate the gate; no delta)
- **Context pack:** jCodemunch outline (8 symbols); the only client is `accel._WorkerClient` (`accel.py` 1185-1250: spawn with token on argv, port line under a 60 s watchdog, `request(timeout=10.0)` per call, teardown + strike on any failure, 3 strikes disable the tier); `nearest()` / `sample_tiled_xp()` hand the worker the FULL arrays before any in-process tier (`accel.py` 912, 1061); GLM-IPC remediation + deferred rows and PS-IPC-CONTRACT loaded as claims; `tests/gpu/run_worker_tests.py` and `glm_ipc_contract.py` read; the mlvenv's torch import timed (3.2 s, ROCm 7.2.1 build, warm cache, NVMe).

## Verdict
The IPC contract (FrameError on any malformed input, token handshake, single owner) holds at the bytes, but the process is not what its client believes it is: it is not persistent (it exits after 30 s of quiet), and its nearest() is the unbounded n x m brute force the in-process path was chunked to avoid - while the parent sends it the giant-mesh case first. Both fixed-shape defects; both RED on probes. (The parent never reaches this file inside Blender today - see the `accel.py` HIGH - so these bite the moment that is fixed.)

## Bugs & vulnerabilities

**[MEDIUM] The "persistent" worker exits after 30 s of idleness** - `line 124-126` (`_serve`), `line 30` (`REQUEST_TIMEOUT`)
- What: `_serve` waits for the next request with `ipc.recv_frame(conn, timeout=REQUEST_TIMEOUT)`; `read_exact` puts the 30 s timeout on the idle wait for the 4-byte length, `socket.timeout` is caught in the same `except` as a broken connection, `_serve` returns, `main()`'s `finally` closes the sockets and the process ends (rc 0).
- Trigger: two clicks more than 30 s apart - the normal way a user works.
- Impact: `_WorkerClient.request()` sees `proc.poll() is not None` and re-spawns on every such click: a fresh process, a fresh `import torch` (3.2 s measured here, more on a cold cache / HIP init), inside the parent's 10 s request deadline - see the PLAUSIBLE item below. The docstrings on both sides ("Owns one persistent accel_worker.py subprocess", GROK-ACCEL6 "the worker is persistent") describe a process that does not exist.
- Fix (minimal, this file): treat quiet as quiet, not as failure - a dead parent still ends the worker because the OS closes the socket and `recv` returns EOF (-> `FrameError` -> return; probe check 2 proves it):
  ```
          try:
              op, meta, arrays = ipc.recv_frame(conn, timeout=REQUEST_TIMEOUT)
          except socket.timeout:
              continue                    # idle between requests is not a failure - a persistent
          except (ipc.FrameError, ConnectionError, OSError):   # worker waits; a dead parent shows up as EOF
              return
  ```
  (`socket.timeout` is an `OSError` subclass, so it must be caught first. A parent that stalls mid-frame for 30 s desyncs the stream, but the parent's own 10 s deadline has torn the socket down by then, which the next `recv` sees as EOF.)
- Verification: CONFIRMED - `probe_ps_accel_worker_1.py` `WK_worker_survives_idle_gap` FAIL (worker rc 0 during a 33 s gap) and `WK_worker_exits_on_parent_close` PASS (EOF path). RED.

**[MEDIUM] nearest() builds the full n x m float64 distance matrix in one transient while the parent sends it the giant-mesh case** - `line 83-84` (`_nearest_numpy`), `line 100` (`_nearest_torch`)
- What: both paths compute `d2` as one (n, m) matrix. The docstring claims the worker "only ever sees whatever a single click sends, not accel.py's own giant-mesh in-process fallback case" - false: `accel.nearest()` (912) offers the worker the identical arrays BEFORE any in-process tier, and the in-process `_nearest_numpy` is chunked to `PATTERNSKIN_NN_MAX_BYTES` (256 MB) precisely because n x m x 8 does not fit (feathering: `nearest(co[~sel], P)` over a whole mesh, `__init__.py:438`; swept3d: `nearest(path, P)`, `projections.py:462`).
- Trigger: an enabled worker + a mesh where n x m x 8 bytes exceeds GPU then host memory (60k x 60k = 28.8 GB; 20k x 20k = 3.2 GB already blows the 10 s deadline on the host path).
- Impact: torch OOM -> numpy `MemoryError` (or a swap crawl past the parent's 10 s `recv` deadline) -> the parent tears the worker down, strikes it, falls back to the chunked CPU path; three such clicks disable the tier for the session. The GPU route is lost on exactly the meshes it was meant to speed up, with nothing but an event-log line to say so.
- Fix: chunk both paths with the in-process budget and in-place arithmetic (`d2 = qc @ T.T; d2 *= -2.0; d2 += Tn[None, :]`, argmin / argpartition per chunk, `out` preallocated int64) - a copy of `accel._nearest_numpy`'s loop with `_NN_MAX_BYTES = 256 * 1024 * 1024` at module level; the torch path chunks the query rows the same way (`d2 = Qc @ T.T; d2.mul_(-2.0).add_(Tn); topk` per chunk). Returns are unchanged: 1-D int64 for k = 1, (n, kk) nearest-first otherwise.
- Verification: CONFIRMED - `probe_ps_accel_worker_2.py` `WK_worker_nearest_memory_bounded` FAIL (977 MB peak for 8000 x 8000 vs the 256 MB budget) and `WK_parent_offers_worker_full_problem` PASS (the call order at `accel.py:912`). RED.

**[PLAUSIBLE - MEDIUM] The first request after every spawn must fit `import torch` + device init inside the parent's 10 s deadline** - `line 49/95` (lazy `import torch` inside the op) vs `accel.py:1213` (`timeout=10.0`)
- What: the worker imports torch lazily on the first `sample_tiled` / `nearest`; the parent's per-request `recv_frame(timeout=10.0)` therefore spans process start + torch import + backend init + the op. Measured here: 3.2 s for the mlvenv's `torch 2.9.1+rocm7.2.1` with a warm file cache on NVMe; a cold cache, an HDD, or HIP device/kernel initialisation on the AMD hardware the tier targets are unmeasured.
- Impact if over: the parent kills the worker mid-import, strikes it, and repeats the same cost on the next click (compounded by the idle exit above: every click is a first request); after three, the tier is disabled for the session.
- Fix: import torch in `main()` BEFORE printing the port (`try: import torch except Exception: pass`) - the parent's 60 s port watchdog (`_read_line_timeout`) already covers a slow or hanging import, and a crash at import surfaces as "did not report a valid port" exactly as designed; the request path then carries only the op.
- Verification: PLAUSIBLE - unverified because no AMD/ROCm hardware is available here to time the cold path; the 3.2 s warm figure is the floor, not the case that matters.

## Missing safeguards
- The parent's stdout pipe is never drained after the port line (`accel.py:1201` keeps `stdout=PIPE`): any later stdout write by a backend over the OS pipe buffer (~64 KB) blocks the worker on `print` -> the parent times out and strikes. No known writer in the dependency set, so noted only; the port could be handed over the socket instead, freeing stdout for DEVNULL.
- The token arrives on `argv` (see the `accel.py` LOW): read it from `PATTERNSKIN_WORKER_TOKEN` first, argv second.
- `_OPS` runs `int(meta.get("k", 1))` - a non-numeric k is a `ValueError` inside the guarded handler (fine) but is reported as a worker error, which costs the parent a teardown + strike for a request-shape problem.

## Adversarial verification pass (refuted claims)
- "The token read loop can hang on a slow impostor" - REFUTED: `cand.settimeout(2.0)` bounds it; `OSError` (timeouts included) drops the candidate and the accept deadline bounds the outer loop.
- "A single-point (1-D) query crashes the worker" - REFUTED as a defect: `einsum("ij,ij->i")` raises inside the guarded handler -> error frame -> parent falls back; every call site passes 2-D arrays.
- "`idx[:, 0] if kk == 1` disagrees with the parent's k = 1 contract" - REFUTED: 1-D int64 for k = 1 on both paths, (n, kk) nearest-first (`sorted=True` / explicit argsort) otherwise - identical to `accel.nearest()`'s documented shape.
- "`torch.as_tensor` on the read-only `frombuffer` input fails" - REFUTED: it warns (non-writable NumPy array) and copies; the numpy path only reads.

## Remediation postscript (same session)
The fixes were applied after this review hashed the bytes above; the file is now `9768f77cc04fa033cbb26c65ac4584a3360b836069e32fb8f59014bb799207dd`. Rows PS-AW-IDLE-EXIT, PS-AW-NN-FULL-MATRIX, PS-AW-TORCH-PREIMPORT in `docs/remediation_manifest.json`, same commit.

