# BUG review: asset-forge\launcher.py

- source: `C:\Users\User\source\repos\Nexusmill\asset-forge\launcher.py`
- model: moonshotai/kimi-k3
- reviewed: 2026-07-20 01:04
- tokens: in 2801 / out 1417
- est cost: $0.0297

---

## Verdict
Mostly ship-safe for a local desktop launcher, but the port-pick-then-bind pattern is a classic TOCTOU race that can either crash startup or, worse, serve the UI from a port another process just grabbed. Biggest risk: flaky/misattributed startup due to the free-port race plus the heuristic 5-second browser fallback.

## Bugs & vulnerabilities

**[MEDIUM] TOCTOU race on free-port selection** - `lines 30-39, 49`
- What: `_free_port()` binds port 0, reads the port, closes the socket, then the Flask thread later rebinds it. The port is unowned in between.
- Trigger: any process (another launcher instance, a dev server, Windows port-hypervisor reallocation) binding that port in the gap — most likely when two Asset Forge instances launch simultaneously.
- Impact: Flask's `run()` fails with "Address already in use"; `_wait_for_server()` then succeeds anyway if the *other* process is listening on that port (line 60 only checks connectivity), so the window opens pointing at a foreign service. Otherwise the user just gets a startup error.
- Fix: keep the probe socket open and pass its fd to the WSGI server (e.g. `werkzeug.serving.run_simple(hostname, port, app, fd=srv.fileno())` isn't supported — instead bind via `make_server` on an already-bound socket), or retry loop: try `app.run` on the chosen port, on `EADDRINUSE` pick a new port and retry. Also make `_wait_for_server` verify it's *our* app (e.g. GET a `/health` endpoint and check a token), not just "something answered".

**[MEDIUM] Unauthenticated readiness probe can match a foreign service** - `lines 55-64`
- What: `_wait_for_server` treats any TCP accept on (HOST, PORT) as success. Combined with the race above, or with a stale instance of the app, the UI window can attach to the wrong server (e.g. an old instance with a different `--library-dir`).
- Trigger: stale Asset Forge instance running; or the TOCTOU race.
- Impact: user edits/reads the wrong library; confusing state, potential data written to an unintended directory.
- Fix: after connecting, issue an HTTP request to a known endpoint and validate a per-launch random token the server returns; only then proceed.

**[MEDIUM] Silent failure persisting user settings** - `lines 21-28`
- What: `save_settings(_patch)` is wrapped in bare `except Exception: pass`. If the library dir can't be persisted (read-only config, bad path), the user is never told and the app silently uses a different output dir than requested.
- Trigger: unwritable config location, or an invalid `--library-dir`.
- Impact: assets generated to an unexpected location; user believes Pattern Skin's chosen dir is in effect when it isn't.
- Fix: at minimum log the exception to stderr and surface a non-fatal warning via `_show_error` when `_ARGS.library_dir` was explicitly provided.

**[LOW] Profile temp dir leaked on exception** - `lines 134-147`
- What: `tempfile.mkdtemp` creates `prof`; `rmtree` only runs on the happy path. If `Popen(...)` or `.wait()` raises, the dir is abandoned, and the code falls through to launch the default browser too — so the user can get both a browser window and a leaked dir.
- Trigger: browser binary vanishing between `os.path.isfile`/`which` and exec, or `wait()` interrupted.
- Impact: temp dir accumulation; possible double window.
- Fix: wrap in `try/finally: _sh.rmtree(prof, ignore_errors=True)` and `return` (or `continue` past) after handling the exception deliberately.

**[LOW] 5-second wall-clock heuristic misclassifies slow-but-successful windows** - `lines 138-145`
- What: if the chromium app window stays open ≥5s it's considered success; a user closing the window within 5s triggers fallthrough to *also* opening the system browser.
- Trigger: user quickly closes the app window (or first-run AV scan delays launch past boundaries).
- Impact: duplicate UI opens in default browser.
- Fix: check `proc.poll()` — if the process exited with a delegation/exit code quickly, only then fall back; or use `--user-data-dir` plus reading the browser's exit code rather than elapsed time.

**[LOW] Blanket exception swallowing hides window-host failures** - `lines 117-121, 124-130, 151-154, 165-171`
- What: every fallback layer swallows exceptions without logging. If the WebView2 host crashes instantly (exit code ≠ 0 is not even checked — `.wait()` returning nonzero is treated as success), the launcher silently moves on or reports nothing.
- Trigger: corrupted bundled `AssetForgeHost.exe`, missing WebView2 runtime, blocked subprocess.
- Impact: hard-to-diagnose "nothing happened" reports from users.
- Fix: check the host's return code (`if proc.wait() == 0: return`), and append each fallback failure to a log file next to the exe (or stderr) before trying the next option.

## Missing safeguards
- No validation that `--library-dir` exists / is writable before persisting it and handing it to the app.
- No single-instance guard — a second launch starts a second server on a new port rather than focusing the existing window (combined with the port race, this is the likeliest trigger for the TOCTOU bug).
- No shutdown path in fallback mode 3: `while True: sleep(1)` ignores SIGTERM-friendly shutdown and never stops the daemon server thread; closing the console window orphans nothing only because threads are daemon — add a `/shutdown` beacon or handle `SIGTERM`.
- No test covering: port race (simulated EADDRINUSE), `_wait_for_server` against a foreign listener, browser-missing path, and settings-persistence failure.
- `HOST`/`PORT`/`URL` are read by threads with no synchronization guarantee if `main()` were ever re-entered; fine today, but a `_SERVER_ERR` write/visibility note (GIL makes it OK in CPython) is worth a comment.