Source: PatternSkin/accel_bootstrap.py
Reviewer: claude-sonnet-5 (in-session)
sha256: a9a4aedd2cf41b3a08adcc460f04026db157e1743ca03faf37f21a2c9e476473
Date: 2026-07-27
Mode: bug
Context pack: full-file read; diffed 9a0ee6a..c2d2f34 to isolate this session's additions
(ensure_python312, check_driver, verify_authenticode, capture mode, tier_installable); cross-read
the call site in PatternSkin/__init__.py (PATTERNSKIN_OT_install_ml_worker); checked
tests/gpu/run_bootstrap_tests.py for existing coverage of the lock/cancel paths; checked
docs/remediation_manifest.json and docs/deferred_manifest.json for prior art (found the
lock-path-per-venv fix from the RDNA3 session, unrelated to these findings; found no prior
entry for lock staleness-vs-heartbeat or for ensure_python312's missing cancel/lock).

## Verdict
Shippable for the common case (fast connection, one install at a time). Two real concurrency
gaps exist around `ensure_python312()` — no lock at all, and no cancellation — plus one lock
whose staleness reclaim has no heartbeat, so it can fire on a legitimately slow, still-running
install rather than only on an abandoned one. All three are unexercised by the current test
suite.

## Bugs & vulnerabilities

**[HIGH] `ensure_python312()` has no lock at all** - `ensure_python312()` (line 233)
- What: `bootstrap_ml_venv()` wraps its entire critical section in `acquire_lock(lock_path_for(venv_dir))` (line 672). `ensure_python312()`, called by `__init__.py`'s `_work()` (PatternSkin/__init__.py:2704) *before* `bootstrap_ml_venv()` even starts, acquires no lock whatsoever around its own download-to-`PY312_DIR`-then-extract-to-`staging` sequence (lines 261-287).
- Trigger: two bootstrap attempts reach `ensure_python312()` concurrently. This is reachable two ways: (a) a second Blender instance clicks Install at nearly the same time; (b) `PATTERNSKIN_OT_install_ml_worker.cancel()` in `__init__.py` (line 2797) clears the `_ML_WORKER_INSTALLING` guard and removes the timer *immediately*, without joining `self._thread` or checking `self._done` — so Blender forcibly cancelling the modal operator (file close, another modal grabbing focus) lets the user re-click Install while the original daemon thread is still alive and still inside `ensure_python312()`.
- Impact: both threads independently `shutil.rmtree(staging, ignore_errors=True); os.makedirs(staging, ...)` then extract into the *same fixed* `install_dir + ".partial"` path (line 270-272), interleaving or truncating each other's extraction. `_find_python_exe()` (line 217) may then report a python.exe that exists but is paired with a mismatched/missing standard-library tree from the other thread's extraction.
- Fix: give `ensure_python312()` its own `acquire_lock()` call (it can share `lock_path_for(install_dir)` the same way `bootstrap_ml_venv` derives one per venv_dir), or fold both functions under one outer lock acquired once by the caller.

**[HIGH] Lock staleness has no heartbeat, so a live install can be reclaimed** - `acquire_lock()` / `_lock_is_stale()` (lines 73-113)
- What: `_lock_is_stale()` compares `time.time() - os.path.getmtime(lock_path)` against `stale_after` (default 3600s). The lock file's mtime is set once, at creation (`os.open(..., O_CREAT|O_EXCL...)` then `os.write` then `os.close`, line 92-107) and is never touched again for the duration of the `with acquire_lock(...): ...` block that follows — there is no periodic re-touch/heartbeat.
- Trigger: the pinned ROCm tier is 2.19 GB (`total_bytes` in gpu_accel_manifest.json). On a connection slower than ~5 Mbit/s sustained, total wall-clock time for download+install exceeds 3600s while the process is still actively, correctly working. Any second `acquire_lock()` call against the same path after that point sees `FileExistsError`, calls `_lock_is_stale()`, gets `True` (age > 3600s regardless of activity), removes the "stale" lock, and proceeds — even though the first process is still inside its own `with acquire_lock(...)` block.
- Impact: both processes now run the artifact-download loop and `install_pinned_wheel()` concurrently against the same `venv_dir`/`download_dir`, with the same failure modes as the HIGH finding above (interleaved writes to shared `.partial`/wheel paths, one process's `create_venv()` wiping the venv the other just populated).
- Fix: either extend `stale_after` well past the largest realistic total_bytes/slowest-supported-connection time, or (better) touch the lock file's mtime periodically from inside the held critical section (a `progress_cb`-adjacent heartbeat, or `os.utime(lock_path, None)` each time `_agg`/`progress_cb` fires) so staleness tracks "no activity" rather than "elapsed wall clock since acquire."

**[MEDIUM] Cancellation is silently inert during the Python 3.12 resolve/download/extract phase** - `ensure_python312()` (line 233); called from PatternSkin/__init__.py:2704
- What: `ensure_python312(tier, capture=False, progress_cb=None, install_dir=None, download_dir=None)` accepts no `cancel_event` parameter, and its internal `download_and_verify(url, sha, archive_path, progress_cb=progress_cb)` call (line 266) is likewise never passed one.
- Trigger: user presses Esc while the operator is still resolving/downloading/extracting the standalone Python 3.12 runtime (before `bootstrap_ml_venv` — which DOES check `cancel_event` — is ever reached).
- Impact: `PATTERNSKIN_OT_install_ml_worker.modal()` (PatternSkin/__init__.py:2728) sets `s.accel_status = "Cancelling AMD GPU worker install ..."` and the background thread keeps running, unaffected, until this phase finishes on its own. The status message is actively false for however long that takes.
- Fix: add a `cancel_event=None` parameter to `ensure_python312()` and thread it into its `download_and_verify()` call (which already supports `cancel_event`); check it between the download and extraction steps too.

**[MEDIUM] `ensure_python312()` trusts a cached archive's bytes without re-verifying its hash** - `ensure_python312()` (line 265)
- What: `if not os.path.isfile(archive_path): download_and_verify(url, sha, archive_path, ...)` — when `archive_path` already exists on disk, it is extracted directly with no hash check.
- Cross-file/self-inconsistency: `bootstrap_ml_venv()`'s own artifact loop (line 696-707), operating on the exact same class of "did we already download this" cached-file scenario, explicitly re-hashes and deletes-on-mismatch, with the comment "Re-verify rather than trust the filename; a stale/partial file from an earlier run is exactly what the hash is for." `ensure_python312()` doesn't apply that same rule to its own cached download.
- Impact: bit rot, antivirus quarantine-and-restore corruption, or a manually-dropped wrong file at that exact path between runs would be extracted and trusted with no detection, whereas the sibling code path in the same file treats this exact risk as worth guarding.
- Fix: re-hash `archive_path` against `sha` before reusing it (mirroring the artifacts-loop pattern), removing and re-downloading on mismatch.

## Missing safeguards
- No test exercises any of the three findings above; `tests/gpu/run_bootstrap_tests.py` tests that a stale lock *is* reclaimed (correct, as a feature) but not what happens when the original holder is still legitimately active past `stale_after`.
- `_record_capture()` (line 490) does non-atomic read-modify-write on `CAPTURE_OUT` with no locking; low severity since capture mode is a manual, single-operator dev workflow (`PATTERNSKIN_PIN_CAPTURE=1`), not a shipped end-user path.
