# BUG review: check_integrity.py

- source: `C:\Users\User\source\repos\Nexusmill\check_integrity.py`
- model: moonshotai/kimi-k3
- reviewed: 2026-07-19 21:01
- tokens: in 903 / out 1142
- est cost: $0.0198

---

## Verdict
Not quite safe to ship for automation: the script always exits 0, so any CI pipeline consuming it will treat total failure (all files corrupt, report unwritable) as success. Everything else is minor.

## Bugs & vulnerabilities

**[HIGH] Script always exits 0 even when corrupt files are found** - `line 36` (implicit, missing `sys.exit`)
- What: No exit-status signaling. Whether `bad` is empty or lists 500 broken files, the process returns 0.
- Trigger: Any syntax error found, and the script is invoked from CI / a pre-commit hook / `make check`.
- Impact: Broken/truncated files sail through automated gates undetected — the script's core purpose is defeated. Worse, if the report write on line 35 raises (disk full, permission), that traceback is the only nonzero exit path and is itself uncaught.
- Fix: `import sys; sys.exit(1 if bad else 0)` after writing the report.

**[MEDIUM] `__pycache__` filter is a substring match on the whole path** - `line 17`
- What: `if "__pycache__" in dp` tests the full directory path, not path components. A legitimate directory named e.g. `tools__pycache__backup` or `not__pycache__dir` anywhere in the tree is silently skipped.
- Trigger: Any project directory whose name merely contains the substring.
- Impact: Files in such directories are never checked but still counted as "ALL CLEAN" — silent false negative.
- Fix: `if "__pycache__" in dp.split(os.sep): continue`, or better, prune `dirs[:] = [d for d in dirs if d != "__pycache__"]` in the `os.walk` loop (also avoids descending into them).

**[MEDIUM] File-handle leak / unflushed report write** - `line 35`
- What: `open(...).write(...)` on a temporary object relies on CPython refcounting to close and flush. On other interpreters (PyPy) or if the process is killed, the report may be truncated or never flushed; the handle leak also triggers `ResourceWarning`.
- Trigger: Non-CPython runtime, crash between write and GC, or embedded use.
- Impact: `_integrity_report.txt` silently missing or incomplete.
- Fix: `with open(path, "w", encoding="utf-8") as fh: fh.write(...)`.

**[LOW] Transient filesystem errors misreported as corruption** - `lines 23–29`
- What: The bare `except Exception` lumps `FileNotFoundError` (file deleted between `os.walk` and `open` — a real race), `PermissionError`, and `IsADirectoryError` (odd symlinks) into the same "Corrupt / invalid" list as genuine `SyntaxError`s.
- Trigger: Concurrent modification of the tree during the scan, or unreadable files.
- Impact: Report claims files are "truncated / syntactically broken" when they are fine — misleading output erodes trust in the tool.
- Fix: Catch `OSError` separately and report it as an I/O error, not corruption.

**[LOW] Write of report is unguarded** - `line 35`
- What: If `ROOT` is read-only (the docstring explicitly contemplates odd mount setups) or the disk is full, this raises an unhandled traceback after all checking is done.
- Fix: Wrap in try/except and fall back to stdout-only output with a nonzero exit.

## Missing safeguards
- No nonzero exit code on failure (see HIGH) — add `sys.exit` and a test asserting it.
- No test that a deliberately broken `.py` file is actually detected (trivial regression risk).
- `os.walk` is called without `onerror`, so permission-denied subdirectories are silently skipped — pass `onerror` to surface them.
- No guard against symlinked directories inside `DIRS` pointing outside `ROOT` (low risk for a local audit tool, but `followlinks=False` only protects the walk, not the top-level `base`).
- No validation that `e.lineno`/`e.msg` are non-None before formatting (rarely None for some `SyntaxError` subclasses; would produce confusing `line None: None` entries).