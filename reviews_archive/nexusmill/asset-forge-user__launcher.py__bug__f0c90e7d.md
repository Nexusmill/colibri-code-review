# BUG review: asset-forge-user\launcher.py

- source: `C:\Users\User\source\repos\Nexusmill\asset-forge-user\launcher.py`
- model: moonshotai/kimi-k3
- reviewed: 2026-07-20 01:05
- tokens: in 2802 / out 1581
- est cost: $0.0321

---

## Verdict
Shippable as a desktop launcher, but it carries a classic TOCTOU port race that can cause it to attach to (and display) a *different* process's HTTP server, plus a fragile browser-close heuristic that reopens the app after the user closes it. Biggest risk: the free-port-then-rebind race.

## Bugs & vulnerabilities

**[HIGH] TOCTOU race on port selection — can bind to or display a foreign server** - `line 30-39`
- What: `_free_port()` binds port 0, reads the port, closes the socket, then the Flask thread later rebinds that port. Between close and rebind, any other process (a second launcher instance, a crashed-but-restarting app, or even a malicious local process squatting on recently-freed ephemeral ports) can claim it.
- Trigger: two instances launched near-simultaneously, or any local process grabbing the freed port in the gap.
- Impact: `_wait_for_server()` happily connects to the *other* process's listener (any accepting socket passes the check, not just Flask), so the app window opens an attacker/foreign server on loopback, or Flask fails to bind and the user gets the 20s-stall error path. A local attacker squatting the port gets their content rendered in a trusted-looking native window.
- Fix: keep the probe socket open and pass its FD to the server (or set `SO_REUSEADDR` and hand the bound socket to Werkzeug via `app.run(..., )` on a pre-bound socket / `make_server`), or bind the server first and read the actual port. At minimum, verify the listener is actually Flask (e.g., GET a known route and check the response) before opening the window.

**[MEDIUM] Browser-close heuristic reopens the app in the system browser after the user closes it** - `line 144-145`
- What: if the `--app` Chromium window is closed within 5 seconds of launch, the code treats it as "delegation happened" and falls through to step 3, opening the *default browser* and entering the infinite serve loop.
- Trigger: user opens the app and closes it quickly (< 5s) — e.g., accidental launch, or they just wanted a peek.
- Impact: the window the user deliberately closed is immediately reopened in another browser, and the process now hangs forever in the `while True: sleep(1)` loop with no UI to close it. Confusing UX and a zombie process per quick-launch.
- Fix: distinguish delegation from a real fast close — check the child's exit code/early exit only within a much shorter window (~1s), or retry `--app` once with a fresh profile instead of falling through to the system-browser fallback.

**[MEDIUM] Temporary Chromium profile directory leaked on exception** - `line 135-147`
- What: `prof = tempfile.mkdtemp(...)` is created outside the `try`; `_sh.rmtree(prof)` is only reached if `Popen().wait()` completes. If `Popen` raises (bad path, permission error) or `wait()` raises, the profile dir is abandoned.
- Trigger: browser binary found by `_find_app_browser()` but not executable, antivirus blocking spawn, etc.
- Impact: orphaned `AssetForgeApp_*` directories accumulate in %TEMP% on every failed launch.
- Fix: wrap in `try/finally: _sh.rmtree(prof, ignore_errors=True)`.

**[LOW] Startup failure stalls for the full 20s timeout even though the error is already known** - `line 55-64, 177-179`
- What: if Flask fails to bind in the first 100ms, `_SERVER_ERR` is set immediately, but `_wait_for_server()` keeps polling the dead port for the entire `timeout=20.0`.
- Trigger: any immediate server crash (port race above, import-time runtime error inside `app.run`).
- Impact: user stares at nothing for 20s before the error dialog appears.
- Fix: have `_wait_for_server()` also break early when `_SERVER_ERR is not None` (it's polled in the same process), or use an `threading.Event` set by `_run_server` on failure.

**[LOW] `os.chdir(sys._MEIPASS)` globally rewrites the process CWD** - `line 17-18`
- What: changing CWD to the (read-only, temp-extracted) `_MEIPASS` affects every relative path the app and its libraries resolve afterward — including any code that writes relative-path outputs, which will now fail or write into a transient extraction dir.
- Trigger: any app code using relative paths for writable files after launch.
- Impact: silent write failures or lost outputs; also breaks `--library-dir` if a *relative* path is passed (it's stored raw at line 15/24 and resolved against the new CWD).
- Fix: resolve `library_dir` to an absolute path *before* `os.chdir`, and prefer passing the bundle path to template/catalog loaders explicitly instead of chdir.

## Missing safeguards
- `_wait_for_server()` accepts *any* TCP listener as "server up" — add an HTTP health-check against a known Flask route to confirm it's actually this app.
- No validation of `--library-dir` (exists? writable? absolute?). It's trusted into an env var and a persisted settings file with a bare `except Exception: pass` (lines 21-28) — at least log the failure.
- The bare `except Exception: pass` around `webview.start()` (line 129) and the WebView2 host (line 120) swallow all diagnostics; log them so fallback behavior is debuggable.
- No test or guard for the double-launch case: a second instance should detect the first (lock file / named mutex) rather than racing ports and spawning a duplicate server.
- The fallback `while True: time.sleep(1)` loop (line 156) has no shutdown path other than Ctrl+C — a console-less frozen exe reaching this branch can never exit cleanly.