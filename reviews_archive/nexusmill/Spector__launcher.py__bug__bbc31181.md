# BUG review: Spector\launcher.py

- source: `C:\Users\User\source\repos\Nexusmill\Spector\launcher.py`
- model: moonshotai/kimi-k3
- reviewed: 2026-07-20 01:20
- tokens: in 1985 / out 1758
- est cost: $0.0275

---

## Verdict
Not safe to ship as-is. The biggest risk is the free-port TOCTOU race combined with the readiness probe trusting *any* TCP listener: the window can silently open against a different local service, and several failure paths are swallowed or leave the process orphaned.

## Bugs & vulnerabilities

**[HIGH] Free-port TOCTOU race + readiness probe accepts any listener** - `lines 12-14, 30-38`
- What: `_free_port()` binds, reads the port, closes the socket — releasing the port — and only later does Flask bind it. Between close (line 14) and Flask's bind (line 25), any local process can claim that port. `_wait_for_server()` then only checks that *something* accepts a TCP connection, not that it's the Spector Flask app.
- Trigger: any other process (another Spector/Asset Forge launch, dev server, malware squatting loopback ports) binding the same port in the race window.
- Impact: `_wait_for_server` returns True and the native window / browser is pointed at an arbitrary third-party HTTP service on loopback — wrong app, or a spoofed UI harvesting user input. Also the real Flask thread fails with "Address already in use," and the user never sees `_SERVER_ERR` because the probe succeeded against the impostor.
- Fix: have Flask itself bind port 0 (or pass the still-open socket), and make the probe validate identity — e.g. `GET /` and check an expected header/token — before returning True.

**[HIGH] Orphaned server process: infinite serve loop with no window-lifecycle tie** - `lines 100, 103-109`
- What: when Chromium "delegates anyway" (`opened = True`) or the plain-browser fallback runs, the code drops into `while True: time.sleep(1)` forever. Closing the browser tab/window never terminates the launcher; only Ctrl+C in a terminal (which packaged GUI apps lack) stops it.
- Trigger: the documented delegation case (line 100), or any fallback to `webbrowser.open`.
- Impact: leaked Flask server processes holding a loopback port indefinitely; on packaged builds users accumulate invisible Spector.exe processes and port/service squatting (which then feeds the HIGH race above).
- Fix: add a shutdown path — a Flask `/shutdown` endpoint the UI calls on unload, a heartbeat the launcher polls, or at minimum an idle-timeout/`atexit` kill.

**[MEDIUM] Temp profile directory leaked on any exception** - `lines 92-102`
- What: `prof = tempfile.mkdtemp(...)` is created, but `shutil.rmtree` only runs after a successful `.wait()`. If `Popen` raises (browser binary vanished between check and exec, permission error) or `wait()` raises, the `except Exception: pass` swallows it and the profile dir (plus Chromium's cached data if it wrote any) is never removed.
- Trigger: launch failure of the browser process.
- Impact: disk leak per failed launch; silent failure hides the root cause.
- Fix: wrap the whole block in `try/finally: shutil.rmtree(prof, ignore_errors=True)` and log the exception.

**[MEDIUM] 5-second heuristic misclassifies real short sessions as delegation** - `lines 98-100`
- What: a genuine window that closes in under 5 seconds (browser crash, user immediately closing, profile-lock error dialog) is treated as "delegated anyway," setting `opened = True`, which suppresses the browser fallback and sends the process into the infinite serve loop with no visible window.
- Trigger: browser exits within 5 s for any reason other than delegation.
- Impact: user sees nothing; server runs headless forever; no error is shown.
- Fix: distinguish delegation from failure — check the child's exit code, or detect the delegated case via profile-dir lock/process signaling rather than a timing guess; on genuine early exit, fall back to `webbrowser.open` or show an error.

**[LOW] Silent swallowing of all window-launch failures** - `lines 76-77, 83-84, 101-102, 116-117`
- What: four `except Exception: pass` blocks discard tracebacks for the native host, pywebview, and browser paths.
- Trigger: any exception in those paths (e.g. pywebview installed but missing GTK/WebKit deps).
- Impact: un-debuggable "window never appears" reports; no telemetry or stderr trail.
- Fix: collect exceptions and surface them via `_show_error` when all launch paths fail, or at least `traceback.print_exc()`.

**[LOW] Windows-only native host tried on win32, but pywebview branch is never reachable there** - `lines 71-84`
- What: the `if sys.platform == "win32"` / `else` structure means a Windows machine without `AssetForgeHost.exe` skips pywebview entirely even if installed, going straight to browser mode — contradicting the docstring's "pywebview on mac/Linux; ... elsewhere" intent being platform-exclusive.
- Fix: attempt pywebview as a fallback on Windows too when the native host is absent/fails.

**[LOW] Race between server thread error and error display** - `lines 123-124`
- What: if the probe times out *before* `_run_server`'s except block writes `_SERVER_ERR` (slow import/traceback formatting), the message box shows an empty detail string. Minor, but the traceback can also be lost entirely if the thread is still formatting when `main` returns and the process exits.
- Fix: join the server thread briefly after timeout before reading `_SERVER_ERR`.

## Missing safeguards
- Readiness probe must verify the responder is actually the Spector app (secret token or expected route), not just an open port.
- A shutdown/heartbeat mechanism so the launcher exits when the UI is gone — currently no path other than KeyboardInterrupt.
- `try/finally` cleanup for the temp profile directory.
- Logging (even to a file in `%TEMP%`/stderr) for every swallowed exception in `_open_window`.
- No handling of `webbrowser.open()` returning False (no browser at all) — user gets no feedback.
- No test coverage for: port-squat race, early browser exit <5 s, missing browser binaries, pywebview import-failure fallback chain, and repeated launches leaving no orphan processes.