# colibri-review — asset-forge/launcher.py — bug (hunt round 1, effort=mid, PRIMED scanner) [+ twin]

- **Source:** asset-forge/launcher.py (byte-identical twin, G23) · **Scanner:** general-purpose
  subagent @ claude-sonnet, **primed with the full G6/no-grep canon** (jCodemunch-only; trace shows
  get_file_outline/get_symbol_source/Read, no grep) · **Verification + fix:** claude-opus-4-8[1m]
  (in-session, Phase 3) · cost $0.00
- **sha256 reviewed:** f0c90e7d4dbd4509492ef4a7bb2e7ed8b3f24cd5f7a15105cf3c42c3fb8791f3 · **post-fix:** b0c0b6f3
- **Date:** 2026-07-24 · **Mode:** bug · round 1 (prior cached review: K3 @f0c90e7d, re-verified).

## Verdict
The three-tier window fallback had a HIGH hole: the primary path discarded the native host's exit
code, so its single most-likely failure (WebView2 runtime missing) produced a fully silent launch.
Fixed, plus a 20s-hang, a silent settings-save, and a temp-profile leak. Four lower items deferred.

## Bugs & vulnerabilities (CONFIRMED, fixed)
- **[HIGH] Silent total failure when the WebView2 host exits nonzero** - `_open_app_window:118` —
  `Popen([host,URL,...]).wait()` discarded rc and `return`ed unconditionally, so a nonzero exit
  (WebView2 Evergreen missing/corrupt) skipped the chromeless + browser + `_show_error` fallbacks →
  user sees nothing on double-click. Fixed: `if rc == 0: return`, else fall through.
- **[MEDIUM] `_wait_for_server` ignored `_SERVER_ERR` → 20s blank-window hang** - `:55-64` — a server
  thread that died instantly (EADDRINUSE / any Flask startup error) still made `main()` wait the full
  timeout. Fixed: return False the moment `_SERVER_ERR` is set. **Verified:** pre-fix 5.49s → post-fix
  0.00s (junk/_launcher_test.py, lifted via ast).
- **[MEDIUM] Silent settings-save** - `:21-28` — bare `except: pass` around `save_settings` (persists
  `--library-dir`); assets could go to an unexpected dir with no diagnostic. Fixed: stderr write.
- **[LOW] Chromeless temp-profile leak on Popen failure** - `:135-147` — `rmtree` only on the happy
  path. Fixed: try/finally.

## Deferred (LNCH-1)
Port-selection TOCTOU; unauthenticated readiness probe (accepts a foreign listener); the 5s close
heuristic (double-window on a fast normal close); windowed-build invisible-error gap. All lower-freq
or needing a design choice, and launcher.py is a GUI/subprocess entry point that is NOT
headless-testable — each wants manual validation on a real launch.

## Verify
F4 pre/post test 2/2 (5.49s → 0.00s). F1/F5/F6 are subprocess/GUI paths — inspection + py_compile
only, NOT run in a live Asset Forge session. Mirrored to twin; sync_builds green.

## Refuted (recorded)
- `--library-dir` path traversal — a CLI arg the local user passes to their own process; no privilege
  boundary crossed (robustness, not a vuln).
- `_SERVER_ERR` cross-thread write/read without a lock — atomic single-ref under the GIL, and `main()`
  reads it only after the poll loop; a comment-worthy nit, not a defect.
- PyInstaller `sys._MEIPASS`/`frozen` desync — always set together by PyInstaller.
