# Colibri Review - bug (DELTA) - PatternSkin/accel.py

- **Source path:** `PatternSkin/accel.py`
- **Reviewer:** claude-fable-5-1 (in-session), Colibri G37 protocol, campaign item 1 (product cores), rank 3
- **sha256 reviewed:** `2d53847c95f1fdbfa2a887bcb45e6e9aa11e2b3be06365f0f07fe71363ba2d23` (sha8 `2d53847c`)
- **Date:** 2026-09-10 · **Mode:** bug, stale-file DELTA against `7630793e` (2026-08-22 grok round-6 gate)
- **Delta reviewed:** 3 commits / 131 diff lines: ae8fc346 (GROK-ACCEL6 `_read_line_timeout` + stderr DEVNULL), c9ac5d08 (HY4-ACCEL-PROBETIMEOUT + KCLAMP, plan `ded218ea` executed), 84b7d80a (HY4-ACCEL-WARMLOCK) - every hunk read.
- **Context pack:** the prior review record(s) for the file, `docs/remediation_manifest.json` rows from 2026-07-24 on, `docs/deferred_manifest.json` rows naming the file, `_hunt_plan.json` + `_refuted_ledger.json` loaded; jCodemunch `get_symbol_source` on the call sites each finding depended on.

## Fixed since last review
- Every remediation row dated after the base review was verified present at the bytes (they are the delta).

## Verdict
Clean at the delta. The three executed plans match their remediation rows byte for byte: the three probe timeouts read `_config('probe_timeout', ...)`, `nearest()` clamps k once at the top for every backend, `warmup()` yields to a pending install, and the worker spawn reads its port line under a 60 s watchdog with stderr sent to DEVNULL.

## Bugs & vulnerabilities
None confirmed at the delta.

## Adversarial verification pass / notes
- "A worker that hangs at import leaves an orphan process after the watchdog gives up" - REFUTED: `_spawn` runs inside `request()`'s try; any exception reaches `_teardown()` (`accel.py:1169-1183`), which kills and waits the process, and the daemon reader thread ends on the resulting EOF.
- ACCEL-1 (deferred LOWs) unchanged and out of scope.

---

# FULL re-audit 2026-09-10 (appended - the record above predates the adversarial gate and is kept as history, not as baseline)

# Colibri Review - bug (FULL re-audit) - PatternSkin/accel.py

- **Source path:** `PatternSkin/accel.py` (junction twin `blender_dev/addons/PatternSkin/accel.py`, same bytes)
- **Reviewer:** claude-fable-5-1 fork (in-session), Colibri G37 protocol, campaign item 1 (product cores), rank 3
- **sha256 reviewed:** `2d53847c95f1fdbfa2a887bcb45e6e9aa11e2b3be06365f0f07fe71363ba2d23` (sha8 `2d53847c`)
- **Date:** 2026-09-10 · **Mode:** bug, FULL review of the current bytes (owner ruling 2026-09-10: every prior record for this file - 07-20/07-24 self-reviews, the 08-20/08-22 grok rounds, the 08-30 plan-triangulation and today's delta - predates the adversarial gate or leaned on a record that does; no delta)
- **Context pack:** jCodemunch `get_file_outline` (133 symbols) + `search_text` for every call site of `sample_tiled_xp` / `nearest` / `enable_worker_tier` / `disable_worker_tier` / `warmup` (`__init__.py` 364/374/438/3190/8854/8882, `projections.py` 395/434/462); the 14 remediation rows, 8 deferred rows and 5 feature-registry rows naming the file loaded as CLAIMS; the five prior `.colibri_reviews` records; `tests/test_accel_tiers.py`, `tests/gpu/run_worker_tests.py`, `tests/harness/probes/ps_mlworker_gpu.py` read for how the worker tier is exercised; `~/.patternskin/mlvenv` (torch 2.9.1+rocm7.2.1) present on this machine.

## Verdict
NOT shippable as the AMD GPU route: the experimental worker tier - the product's only GPU path for RDNA 3/4 owners on Windows Python 3.13 (PS-GPU-SUPPORT-STATES 'pinned') - has never executed inside Blender. `_WorkerClient.request()` imports the framing module by its bare name, which resolves in every standalone test (they put `PatternSkin/` itself on `sys.path`) and raises `ModuleNotFoundError` inside Blender, where `_worker_request()` swallows it and returns None: every call runs on the CPU while the panel reports "AMD GPU worker installed and active". Since 55ab26a0 (2026-07-26). Everything else in the file - the subprocess-only probes, the pending-install queue, the tier ladder, the k-clamp, the memory-bounded CPU nearest, the diagnostics layer - holds at the bytes, with one LOW budget miss and one LOW handshake weakness below.

## Bugs & vulnerabilities

**[HIGH] The worker tier never runs inside Blender - `import accel_ipc` cannot resolve there** - `line 1221` (request) and `line 1246` (close)
- What: `_WorkerClient.request()` does `import accel_ipc as _ipc` as a top-level name. Inside Blender the add-on is the package `PatternSkin`; only the addons parent directory is importable, the package directory is not (probe: `os.path.dirname(accel.__file__) in sys.path` is False). The statement raises `ModuleNotFoundError: No module named 'accel_ipc'` BEFORE the `with _worker_lock(): try:` block, so nothing logs it and nothing counts it; `_worker_request()` (1285-1288) catches the exception and returns None, and `nearest()` / `sample_tiled_xp()` fall straight through to the in-process tiers.
- Trigger: any user who installs the AMD worker (`PATTERNSKIN_OT_ml_worker_install` -> `accel.enable_worker_tier(venv_py)`, `__init__.py:3190`) and then applies a pattern. Every existing test passes because `tests/gpu/run_worker_tests.py`, `tests/test_accel_tiers.py` and the bootstrap harness all `sys.path.insert(0, PatternSkin/)`; the venv self-test runs in the venv's python, not through `_WorkerClient`.
- Impact: the feature the whole worker pipeline exists for is a silent no-op in the product - the GPU the user just spent a multi-GB download enabling never receives a request, the status line says "active", the diagnostics event log shows nothing (no `worker/request_fail`, no strike, no `disabled`). Six weeks in the tree.
- Fix: resolve the sibling both ways, and take the import inside the audited try so a future resolution failure is logged and counted:
  ```
  def _ipc_mod():
      """accel_ipc resolved BOTH ways: as a package sibling inside Blender (`from . import`) and as a
      bare module when PatternSkin/ itself is on sys.path (every standalone test). The bare form alone
      raised ModuleNotFoundError inside Blender, which _worker_request swallowed - the worker tier had
      never run in the product (full re-audit 2026-09-10)."""
      try:
          from . import accel_ipc as _ipc
      except ImportError:
          import accel_ipc as _ipc
      return _ipc
  ```
  placed after `_worker_lock()`; in `request()` replace `import accel_ipc as _ipc` + `with _worker_lock():` / `try:` by `with _worker_lock():` / `try:` / `_ipc = _ipc_mod()` (first statement inside the try); in `close()` replace `import accel_ipc as _ipc` by `_ipc = _ipc_mod()`. (`from . import` in a module loaded without a package raises ImportError - "attempted relative import with no known parent package" - so the fallback keeps every standalone test green.)
- Verification: CONFIRMED - `probe_ps_accel_3_bpy.py` inside Blender 5.1.2: `WK_bare_accel_ipc_import_in_blender` FAIL (`ModuleNotFoundError`), `WK_package_accel_ipc_import_in_blender` PASS (the fix's resolution works), `WK_worker_tier_reachable_in_blender` FAIL (worker never spawned, event log empty). RED against the current bytes.

**[LOW] The handshake token is published on the worker's command line** - `line 1195-1197`
- What: GLM-IPC's one-shot token (`secrets.token_hex(16)`) is passed as `argv[2]` of the worker. A process command line is readable by every process of the same user on Windows (`Win32_Process.CommandLine`, `NtQueryInformationProcess`) and by every user on Linux (`/proc/<pid>/cmdline` is world-readable unless `hidepid`). The threat the token was added for is "a local process that reads the port and wins the connect race" - that process can read the token the same way.
- Trigger: any local process listing processes while the worker is alive.
- Impact: the guarantee recorded in the GLM-IPC remediation row is weaker than stated; a local impostor can still claim the worker (DoS of the tier for that Blender, arbitrary arrays run on the user's GPU). Low: same-user processes are already inside the trust boundary on Windows; the cross-user Linux case is the real widening.
- Fix: carry the token in the environment (readable only by the owner: `/proc/<pid>/environ` is 0400) and keep argv only as the test/legacy path: in `_spawn`, `env = dict(os.environ); env["PATTERNSKIN_WORKER_TOKEN"] = tok` and `Popen([self.python_exe, self.script_path], ..., env=env, **kwargs)`; in `accel_worker.main()`, `token = os.environ.get("PATTERNSKIN_WORKER_TOKEN") or (sys.argv[1] if len(sys.argv) > 1 else None)` (+ `import os`).
- Verification: CONFIRMED - `probe_ps_accel_worker_4.py` reads the live worker's command line back through WMI and finds the 32-hex token. RED.

**[LOW] The chunked CPU nearest exceeds its own memory budget ~3x** - `line 958-962`
- What: `chunk` is sized so ONE (chunk x m) float64 matrix fits `nn_max_bytes`, but the expression `Tn[None, :] - 2.0 * (qc @ T.T)` materialises three of them (the product, the scaled copy, the difference). The docstring promises "the transient distance matrix stays under max_bytes".
- Trigger: any nearest() call large enough to chunk (m x n x 8 > 256 MB).
- Impact: peak ~3 x `PATTERNSKIN_NN_MAX_BYTES` (measured 721 MB against the 256 MB default with m = n = 8000). Bounded, so no crash - the knob just lies by a factor of three on the machines it exists for.
- Fix: in-place: `d = qc @ T.T` / `d *= -2.0` / `d += Tn[None, :]` (the value is unchanged: |t-c|^2 - 2 q.t; argmin/argpartition read the same numbers).
- Verification: CONFIRMED - `probe_ps_accel_worker_2.py` `WK_inprocess_nearest_memory_bounded` FAIL (721 MB vs a 320 MB allowance). RED.

## Missing safeguards
- `_worker_request()` swallows exceptions raised OUTSIDE `request()`'s try (1285-1288) with no event and no strike - that is how the HIGH stayed invisible; log `worker/request_fail` there too (the fix above moves the import inside the try, which closes this instance).
- No sender-side payload cap: `send_frame` ships arrays the worker will refuse above `MAX_PAYLOAD_BYTES` (512 MB); the refusal costs a strike. Not reachable from an interactively edited mesh (22 M verts of float64 points), so noted, not fixed.
- A healthy worker's error reply (`rop != "ok"`, 1229-1230 - an unknown op, a KeyError in a handler) makes the parent tear the worker down and strike it, although the worker recovered and kept serving; three such replies disable the tier.
- `mark_pending_install()` accepts a name outside `INSTALL_ALLOWLIST` and returns True; `finish_pending_installs` skips it silently forever and the marker suppresses `warmup()` for good. Call sites pass fixed names today.
- `worker not persistent` and `first-request budget` belong to `accel_worker.py` (see that record) but bite here: `request(timeout=10.0)` is the deadline the worker's cold `import torch` has to fit in.

## Adversarial verification pass (refuted claims)
- "`np.frombuffer` arrays from the worker are read-only and break in-place math at the call sites" - REFUTED: every consumer builds new arrays (`_combine_heights` returns fresh arrays, the feather does `h = h * ...`, `projections` reads `nbrs[cur]` / `_outs[_idx]` / `np.clip(pi - 1, ...)`); no in-place write on a returned array.
- "A worker that hangs at import leaves an orphan after the 60 s port watchdog" - REFUTED: `_spawn` runs inside `request()`'s try; `_teardown` (1169-1183) kills and waits it; the daemon reader thread ends on the resulting EOF.
- "`INSTALL_ALLOWLIST` / `_time` / `_log_event` are used before their definition (lines 428/450/40 vs 1302/1297/1360)" - REFUTED: module-level names bound at import; every use is inside a function called after the module loaded.
- "The impostor loop in the worker can starve the real parent past its 10 s budget" - REFUTED: each impostor costs at most 2 s, the parent's connection waits in the listen backlog with its token and frame buffered, and no attacker with 5+ queued connections exists in the recorded threat model.
- "`get_xp` and `active_tier_key` disagree for a torch that only has a CPU device" - REFUTED: the subprocess probe sets `torch=True` only for cuda/mps/directml, so `c["torch"]` already encodes a GPU device.
- "`_nn_key` hashes the whole tree on every call - a silent O(n) per query" - not a defect: the KD-tree build it avoids is O(n log n); refuted as a finding.

## Remediation postscript (same session)
The fixes were applied after this review hashed the bytes above; the file is now `3648d0674b74a6c9b81e26a380fca8b52f52454018e255b207deb03565cfef46`. Rows PS-ACCEL-IPC-IMPORT, PS-ACCEL-TOKEN-ENV, PS-ACCEL-NN-TRANSIENT in `docs/remediation_manifest.json`, same commit.

