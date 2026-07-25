# BUG review: tests\test_accel_tiers.py

- source: `C:\Users\User\source\repos\Nexusmill\tests\test_accel_tiers.py`
- model: moonshotai/kimi-k3
- reviewed: 2026-07-20 01:12
- tokens: in 2516 / out 2390
- est cost: $0.0434

---

## Verdict
Mostly ship-able as a test harness, but it leaks global state (`sys.modules["gpu"]`, `accel._CAPS`) on the error path and is order-dependent: mocked modules installed in one test can contaminate later ones through `accel`'s cached imports. Biggest risk: a mid-file exception leaves the interpreter (and any later tests in the same process) permanently poisoned, turning real failures into misleading passes/crashes elsewhere.

## Bugs & vulnerabilities

**[MEDIUM] `sys.modules["gpu"]` clobbered without save/restore, no `finally`** - `lines 111–116`
- What: The test does `sys.modules["gpu"] = fake_gpu`, then unconditionally `del sys.modules["gpu"]` after `capabilities()`. If a real `gpu` module was already in `sys.modules` (e.g., running inside Blender, or a prior test imported it), the original entry is destroyed. And if `accel.capabilities(refresh=True)` raises, neither the `del` nor `accel._CAPS = None` runs.
- Trigger: Any exception in `accel.probe_scipy()` / `accel.capabilities()`, or a pre-existing `"gpu"` entry in `sys.modules`.
- Impact: Process-global state corruption; subsequent code sees the fake `gpu` module or loses the real one, and `accel._CAPS` stays forced, making all later detection tests (and any same-process code) silently test the wrong configuration.
- Fix: `saved_gpu = sys.modules.get("gpu")` and wrap in `try/finally` that restores `saved_gpu` (or deletes if it was absent) and resets `accel._CAPS = None`.

**[MEDIUM] Mocked modules can persist inside `accel` across `parity()` calls** - `lines 42–55, 69–75, 101–106`
- What: `parity()` restores `sys.modules`, but if `accel.get_xp()` (or module-level code in `accel`) does `import cupy` / `import torch` and caches the module object in a global (the standard pattern for an accel shim), the fake numpy-backed `cupy` from line 75 stays referenced inside `accel` after `sys.modules` is restored. The later "cupy claimed but not importable" check (line 101) then exercises the *cached fake*, not a real import failure.
- Trigger: `accel` caching the imported backend module (cannot be ruled out from this file; `force(cupy=True)` at line 101 only manipulates `_CAPS`, not any cached module reference).
- Impact: The fallback test at line 106 can pass for the wrong reason (using the fake) or fail spuriously, and test results become order-dependent — rerunning a subset of the file gives different behavior.
- Fix: Have `parity()` also reset any `accel`-level backend cache (e.g., `accel._XP = None` / call its cache-reset API), or reload `accel` per test.

**[LOW] Nearest-neighbour tie-break mismatch between brute force and cKDTree** - `lines 85–92`
- What: `brute` uses `argmin(1)`, which returns the *first* index on exact distance ties; `scipy.spatial.cKDTree.query` makes no such guarantee (returns an arbitrary tied index depending on tree layout).
- Trigger: Two tree points exactly equidistant from a query point (possible here: `rng.random` float64 is effectively tie-free, but any change to integer/coarse test data reintroduces it).
- Impact: Spurious `FAIL` on `idx_sci == brute` that is not an `accel` defect — the chunked-numpy path is held to a tie policy SciPy doesn't have.
- Fix: Compare distances (`tree[idx] == min distance`) or assert `dist` equality plus membership of `idx` in the tied set, instead of index equality vs `argmin`.

**[LOW] Stale `tag` masks which statement failed in the cupy-fallback check** - `lines 101–106`
- What: `xp, _, tag = accel.get_xp(); ok = True` — if `get_xp()` raises, `tag` retains its value from line 98 (`"numpy"`), so the failure is attributed to `ok` only. Worse, if `get_xp()` returns successfully but with an unexpected tag, the same single `check` conflates the two failure modes, and the printed label can't distinguish "crashed" from "returned cupy".
- Trigger: `accel.get_xp()` raising, or honoring the fake `cupy=True` capability.
- Impact: Harder diagnosis of a real regression; the check message is misleading about the root cause.
- Fix: Split into two checks (`check(ok, "...no crash")` and, only if `ok`, `check(tag == "numpy", "...falls back to numpy")`) and initialize `tag = None` before the `try`.

## Missing safeguards
- No `try/finally` around any of the global-state mutations (`accel._CAPS`, `sys.modules`) outside `parity()` — lines 88–91, 97, 101, 111–116, 122–125 all leak forced caps if an exception fires.
- Line 119 (`check(c["scipy"] is True, ...)`) is a hard failure if SciPy isn't installed in the environment, unlike the torch block (lines 61–66) which skips gracefully — detection tests should skip, not fail, on missing optional deps.
- No test that `sample_tiled_xp` handles edge inputs: empty `u`/`v` arrays, NaN/inf coordinates, non-contiguous or read-only input tiles, or `tile` with H or W of 1 — the wrap-around indexing path (`u`/`v` in `[-3, 6)`) is only exercised for the happy case.
- `check(err < tol, ...)` at line 51 would crash with `ValueError` on an empty result from `sample_tiled_xp` (`np.max` of empty array) instead of reporting a clean FAIL — guard `h.size == 0` first.
- No verification that `parity()`'s `sys.modules` restore actually leaves `accel` functional (a smoke call after restore would catch cache-poisoning bugs like the MEDIUM above).