# Colibri Review - bug (DELTA) - PatternSkin/accel_ipc.py

- **Source path:** `PatternSkin/accel_ipc.py`
- **Reviewer:** claude-fable-5-1 (in-session), Colibri G37 protocol, campaign item 1 (product cores), rank 47
- **sha256 reviewed:** `b1e6560871f6cb78a822656361da10b6f04259015207b248d5af180a3e355b3d` (sha8 `b1e65608`)
- **Date:** 2026-09-10 · **Mode:** bug, stale-file DELTA against `743b5f4a` (2026-08-06 review)
- **Delta reviewed:** 2 commits / 36 diff lines: 2a06c299 (GLM-IPC: `arrays` must be a list; frombuffer failures become FrameError), 53e12489 (GROK-IPC4: `op` must be a str, `meta` must be a dict) - every hunk read.
- **Context pack:** the prior review record(s) for the file, `docs/remediation_manifest.json` rows from 2026-07-24 on, `docs/deferred_manifest.json`, `_hunt_plan.json` + `_refuted_ledger.json` loaded; jCodemunch `get_symbol_source` on the symbols each finding depended on.

## Fixed since last review
- Every remediation row dated after the base review was verified present at the bytes (they are the delta).

## Verdict
Clean at the delta - the documented 'FrameError on ANY malformed input' guarantee now holds for every traced escape.

## Bugs & vulnerabilities
None confirmed at the delta.

---

# FULL re-audit 2026-09-10 (appended - the record above predates the adversarial gate and is kept as history, not as baseline)

# Colibri Review - bug (FULL re-audit) - PatternSkin/accel_ipc.py

- **Source path:** `PatternSkin/accel_ipc.py` (junction twin `blender_dev/addons/PatternSkin/accel_ipc.py`, same bytes)
- **Reviewer:** claude-fable-5-1 fork (in-session), Colibri G37 protocol, campaign item 1 (product cores), rank 47
- **sha256 reviewed:** `b1e6560871f6cb78a822656361da10b6f04259015207b248d5af180a3e355b3d` (sha8 `b1e65608`)
- **Date:** 2026-09-10 · **Mode:** bug, FULL review of the current bytes (owner ruling 2026-09-10: the 08-06 review, the 08-15 GLM-IPC and 08-21 GROK-IPC4 rounds predate the gate; no delta)
- **Context pack:** jCodemunch outline (7 symbols); both peers read in full (`accel._WorkerClient.request/close`, `accel_worker._serve/main`); GLM-IPC / GROK-IPC4 remediation + deferred rows and PS-IPC-CONTRACT loaded as claims and each re-traced at the bytes (`arrays` list check 102, `op` str 106, `meta` dict 112, frombuffer guard 137-143); `tests/harness/probes/glm_ipc_contract.py` and `tests/gpu/run_worker_tests.py` read.

## Verdict
Clean. The framing keeps its promise end to end: the header length is capped before it is read, the JSON is type-checked field by field, every declared dimension is a non-negative Python int with overflow-free byte arithmetic against the 512 MB cap before any allocation, and every materialisation failure surfaces as `FrameError`. Nothing on the wire can produce anything but an ndarray. The one behavioural surprise - a `socket.timeout` from `read_exact` is not a `FrameError` - is by design and is what the worker's idle-exit defect (see `accel_worker.py`) mishandles, on its side, not here.

## Bugs & vulnerabilities
None confirmed.

## Missing safeguards
- No sender-side check against `MAX_PAYLOAD_BYTES` in `send_frame` (line 70-86): a frame the receiver is certain to refuse is still fully serialised and shipped; the refusal costs the parent a strike. Not reachable from an interactively edited mesh (22 M float64 points), so noted only.
- `read_exact(sock, n, timeout=None)` leaves whatever timeout the socket already carries (line 52-53) - correct for the callers today, but the docstring does not say so; a caller expecting "None = blocking" would be wrong. If the worker's idle fix is done at this layer instead of in `_serve`, the clean shape is an explicit `idle=True` flag that blocks on the 4-byte length and applies `timeout` to the rest of the frame.
- The returned arrays are `np.frombuffer` views: read-only. Every consumer today builds new arrays (verified at the call sites), so no defect, but a future in-place write on a worker result would raise `ValueError: assignment destination is read-only` only on the worker path.

## Adversarial verification pass (refuted claims)
- "A shape given as a string or floats bypasses the spec validation" - REFUTED: `tuple(int(d) for d in spec["shape"])` coerces each element (a string iterates to digits, a float truncates); `d < 0` and the byte cap then bound whatever came out; the only sender is our own `send_frame`, and anything unreadable ends in `FrameError` at `frombuffer`/`reshape`.
- "A zero-size declared array (`shape [0, 3]`) trips `read_exact` or `frombuffer`" - REFUTED: `read_exact` returns `b""` for n = 0 (54-55) and `np.frombuffer(b"", dtype).reshape((0, 3))` is a valid empty array.
- "`send_frame`'s header-size check runs after the payload copies, so an oversized header still costs the `tobytes()` copies" - true but not a defect (memory transient only; the header cannot legitimately approach 1 MB); refuted as a finding.
- "`recv_frame(timeout=None)` on a socket with a stale short timeout raises `socket.timeout` mid-frame" - the callers always pass an explicit timeout; refuted as a reachable defect, kept as the docstring note above.
