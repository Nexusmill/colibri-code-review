# BUG review: PatternSkin\accel.py

- source: `C:\Users\User\source\repos\Nexusmill\PatternSkin\accel.py`
- model: moonshotai/kimi-k3
- reviewed: 2026-07-19 21:10
- tokens: in 13281 / out 3622
- est cost: $0.0942

---

## Verdict
Not safe to ship as-is. The biggest risk is the design's central invariant — "never import/lock optional deps in-process" — being broken by `nearest()` importing SciPy directly into Blender (line 717), which re-creates the exact WinError-5 self-lock the entire file is engineered to avoid; additionally several background threads mutate shared globals (`_CAPS`) with no synchronization despite `capabilities()` documenting "never raises."

## Bugs & vulnerabilities
**[HIGH] SciPy imported in-process in `nearest()`, locking its files and breaking `repair_scipy`** - `line 717`
- What: The whole module is built around subprocess-only probing because "importing a *broken* SciPy locks its .pyd files in Blender's process and blocks repair" (line 111). Yet `nearest()` does `from scipy.spatial import cKDTree` directly in the Blender process whenever `c["scipy"]` is true.
- Trigger: Any call to `nearest()` after a healthy probe. Once imported, SciPy's `.pyd`/`.dll` files are loaded and locked (Windows). If the install later becomes corrupted, or the user clicks "repair/reinstall SciPy," `repair_scipy()`'s `shutil.rmtree` / `pip install --upgrade` (lines 217–222) fails with WinError 5 — permanently, until restart.
- Impact: The self-lock disease the comments repeatedly describe; the repair button silently stops working (repair errors are swallowed at lines 218–219, 224–225).
- Fix: Either run the KD-tree query in a subprocess too, or document/accept the lock but gate `repair_scipy()` on "restart required" and surface that to the UI instead of silently failing.

**[HIGH] Race: `_CAPS` set to `None` by background probe thread while `capabilities()` reads it — `capabilities()` can raise TypeError despite "never raises" contract** - `lines 67–69, 490`
- What: `probe_gpu_stack()` runs on a daemon thread (line 497) and executes `_CAPS = None` (line 490). Meanwhile `capabilities()` on the UI thread does `if _CAPS is not None and not refresh:` then `_CAPS["scipy"] = scipy_ok()` (lines 67–68). If the probe thread interleaves between the check and the subscript, `_CAPS["scipy"] = ...` raises `TypeError: 'NoneType' object does not support item assignment`.
- Trigger: Panel redraw calling `capabilities()` while the async GPU probe finishes.
- Impact: Exception in a draw/panel path explicitly documented as "never raises"; UI breakage, possible Blender draw-handler crash loop.
- Fix: Read into a local first (`c = _CAPS; if c is not None: c["scipy"] = ...; return c`), or guard all cache swaps with a `threading.Lock`.

**[MEDIUM] `_SCIPY_BUSY` is checked in `probe_scipy` but never set — duplicate concurrent probes** - `lines 147, 178, 190–192`
- What: `probe_scipy()` checks `if _SCIPY_BUSY: return` (line 147) but never sets `_SCIPY_BUSY = True`. Only `repair_scipy()` sets it (line 192). Unlike `probe_gpu_stack()` and `warm_accel_async()`, which correctly set their busy flags inside the probe.
- Trigger: Two rapid calls to `probe_scipy_async()` (e.g., install click + refresh) spawn two threads, both running 90s-timeout subprocesses and both writing `_SCIPY_OK`/`_SCIPY_ERR` unsynchronized.
- Impact: Wasted processes; torn/last-writer-wins state; UI may show the stale probe's error after the newer probe succeeded.
- Fix: Set `_SCIPY_BUSY = True` at entry of `probe_scipy()` and reset in `finally` (mirroring `probe_gpu_stack`).

**[MEDIUM] `repair_scipy` silently ignores pip failure and reports based only on re-check** - `lines 220–223`
- What: The `subprocess.run(pip install ...)` return code and stderr are discarded (`capture_output=True`, never inspected). If pip fails (network, no wheel for this Python, permission), the only signal is `healthy()` returning False → `_SCIPY_OK = False`, and `_SCIPY_ERR` is never updated with the pip output — the UI can't say WHY.
- Trigger: pip install failure.
- Impact: Silent failure; contradicts the file's "live diagnostics (no hiding)" goal; user gets an unexplained "still broken."
- Fix: Capture `r.returncode`/`r.stderr` into `_SCIPY_ERR` when non-zero.

**[MEDIUM] `bpy.app.timers.register` called from background threads in `_redraw_ui`** - `lines 123–140, 169, 323, 491`
- What: `_redraw_ui()` is invoked at the end of `probe_scipy`, `probe_cairosvg`, and `probe_gpu_stack`, all of which run on daemon threads. Blender's Python API (including `bpy.app.timers.register`) is not thread-safe; calling it off the main thread is unsupported and can corrupt state or crash.
- Trigger: Any async probe completing while Blender is busy (render, modal operator).
- Impact: Intermittent hard crashes / undefined behavior — the worst failure mode for a "diagnostics" path.
- Fix: Marshal the registration through Blender's main thread (e.g., `bpy.app.timers.register` from a deferred queue processed by an existing main-thread timer, or use `bpy.app.handler` posted from the main thread only).

**[MEDIUM] `repair_scipy` deletes *any* `numpy*` in the user modules dir without verification** - `lines 213–219`
- What: On a broken-SciPy path it `rmtree`s everything matching `numpy`, `numpy.libs`, `numpy-*` in the shared Blender user `modules` dir — which is shared by *all* add-ons, not just Pattern Skin. A user (or another add-on) with a deliberately installed numpy there loses it, silently (exceptions swallowed at 218–219).
- Trigger: SciPy probe fails for any reason (e.g., transient) while user has a legitimate numpy in `modules`.
- Impact: Destructive deletion of unrelated packages; other add-ons break.
- Fix: Only remove numpy if it is actually shadowing Blender's (compare `numpy.__version__`/`__file__` from a subprocess probe), and log/report every deletion.

**[LOW] File-handle leaks / read-write race on `pending_installs.txt`** - `lines 351, 364, 377–395`
- What: `open(p, ...)` in lines 351 and 364 is never closed (relies on GC; on Windows the transient lock can break the concurrent writer). Also `finish_pending_installs()` rewrites the file based on a stale `pending_installs()` read (lines 393–395), racing with `mark_pending_install()` — a newly marked package can be silently dropped.
- Fix: Use `with open(...)` everywhere and serialize read-modify-write with a module-level `threading.Lock`.

**[LOW] `_nearest_mathutils` crashes on empty `tree_pts`** - `lines 747–758`
- What: With an empty tree, `KDTree(0)` then `kd.find(...)` raises (or returns a `None` result that unpacks badly at line 756). This is the last-resort fallback in `nearest()` (line 727), so the exception propagates out of a "graceful degradation" API.
- Trigger: `nearest(tree_pts=np.empty((0,3)), query_pts=...)` with SciPy absent or failing.
- Fix: Guard `if len(tree_pts) == 0: raise ValueError` early in `nearest()`, or return `-1` indices.

**[LOW] `probe_scipy` doesn't propagate `sys.path`/dep dir to the subprocess outside Blender** - `lines 152–158`
- What: Unlike `probe_cairosvg` (line 311) and `probe_gpu_stack` (line 475), `probe_scipy` only builds `PYTHONPATH` from `bpy.utils.user_resource('SCRIPTS')` and skips `ensure_dep_path()`'s `~/.patternskin/lib` fallback when `bpy` import fails. Result differs from the other probes and from `repair_scipy`'s view of health.
- Fix: Build `PYTHONPATH` from `sys.path` like the other probes.

## Missing safeguards
- No locking around any of the global caches (`_CAPS`, `_GPUSTACK`, `_REC`, `_SCIPY_*`); every async writer/main-thread reader pair is a potential torn read (only the `_CAPS` one is shown to raise, but all should share one lock).
- `repair_scipy`/`finish_pending_installs` never verify pip's exit status, never record pip stderr for diagnostics, and never check hashes or pin versions for packages installed from the default index (`finish_pending_installs`, line 389) — a supply-chain hardening gap for a feature that auto-installs packages recorded in a plaintext file at `~/.patternskin/pending_installs.txt` (writable by any process running as the user; the allowlist at line 375 is the only control — keep it, but add version pinning at minimum).
- No tests: the bilinear sampler has three divergent code paths (numpy/torch/cupy, lines 836–855) with duplicated index math and no equivalence test; `nearest()` has three fallback tiers with no tests for empty inputs, 2-D vs 3-D points, or the float32 precision path in `_nearest_numpy` (large coordinates lose accuracy — no test pins acceptable error).
- `capabilities()` documents "never raises" but has no try/except around the `_CAPS["scipy"]` live-update or the `gpu.platform.*` calls' return-type assumptions — add a top-level guard to honor the contract.