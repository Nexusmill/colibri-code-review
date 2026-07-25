# BUG review: tests\test_patternskin_math.py

- source: `C:\Users\User\source\repos\Nexusmill\tests\test_patternskin_math.py`
- model: moonshotai/kimi-k3
- reviewed: 2026-07-20 01:21
- tokens: in 2364 / out 1514
- est cost: $0.0298

---

## Verdict
Mostly shippable as a dev-side test harness, but it's fragile: the regex-based source extraction can silently extract the wrong code (testing a truncated or stale function), and any unexpected error aborts the whole suite with a raw traceback instead of a clean failure. Biggest risk: tests can pass while not actually testing the real add-on code.

## Bugs & vulnerabilities

**[MEDIUM] Fragile regex extraction can test truncated/wrong code** - `line 24`
- What: `re.search(r"\ndef %s\(.*?\n(?=\ndef |\nclass |\n# |\n_[A-Z])" ...)` guesses function boundaries by what the *next* top-level line looks like. If the add-on inserts a module-level constant, a `@decorator` line, a docstring, or a bare statement between two functions, the non-greedy match stops early and `exec` either fails with `IndentationError`/`SyntaxError` or — worse — the boundary misses and silently captures the wrong slice. Conversely, code executed at import time (e.g., module-level lines between functions) is never in `NS`, so an extracted function referencing a module-level helper or constant raises `NameError` at call time inside a test, misattributing the failure.
- Trigger: any refactor of `__init__.py`/`printfit.py` that changes top-level layout (very likely — this file already survived one such split, per the line-15 comment).
- Impact: false failures that send developers chasing phantom bugs in correct math, or false passes if a truncated body happens to exec.
- Fix: parse with `ast` instead: `tree = ast.parse(SRC)` and pull `FunctionDef` nodes by name, then `exec(compile(ast.Module([node], []), ...))`. Also seed `NS` with the full module's import-block names or execute the module with a stubbed `bpy` instead of slicing.

**[MEDIUM] One unexpected exception kills the entire run** - `lines 106-108`
- What: the runner calls each test bare; a single `NameError`, `ValueError` from numpy (e.g., a degenerate input in `_resample_polyline`), or the `AttributeError` below propagates out of `fn()` and aborts before later tests and before the summary/exit-code line. CI sees a traceback but the report loses all remaining results.
- Trigger: any regression that raises rather than returns a wrong value — exactly the class of bug a test suite exists to catch.
- Impact: reduced signal precisely when the code is broken; "1 test crashed" hides how many others fail.
- Fix: wrap each call: `try: fn() except Exception as e: _F += 1; print(" FAIL ", fn.__name__, repr(e))`.

**[LOW] `assert` extraction guard is disabled under `python -O`** - `line 25`
- What: with optimization flags the `assert m` is stripped; on a failed match the code falls through to `m.group(0)` and raises an unhelpful `AttributeError: 'NoneType'`.
- Trigger: CI configured with `PYTHONOPTIMIZE=1`.
- Impact: confusing error masking the real "could not extract" condition.
- Fix: `if m is None: raise RuntimeError("could not extract " + name)`.

**[LOW] File handles never closed / missing-file error is raw** - `lines 14, 19`
- What: two `open(...).read()` calls without `with` (handles rely on GC), and if `PATTERNSKIN_INIT` points at a bad path or the add-on is moved, the user gets a bare `FileNotFoundError` traceback instead of an actionable message.
- Trigger: missing/moved add-on file; `PYTHONWARNINGS=error` turns the `ResourceWarning` into noise on PyPy/alternative runtimes.
- Impact: cosmetic-to-mild; poor failure UX.
- Fix: `with open(ADDON, encoding="utf-8") as f: SRC = f.read()` wrapped in `try/except OSError` with a clear message and `sys.exit(2)`.

**[LOW] `print_check` tests assert exact warning counts** - `lines 66-68`
- What: `len(pc(...)) == 1` couples tests to the number of independent warnings; e.g. `pc(0.1, 20, 0.2, 0.4)` asserts exactly one warning, so adding any new warning category (a feature) breaks an unrelated test.
- Fix: assert `any("relief" in w.lower() for w in pc(...))` style predicates instead of lengths.

## Missing safeguards
- No test for `_parallel_transport_frames` on a degenerate input (straight line / duplicate consecutive points) — zero-length tangent is the classic NaN path and the helix test never covers it.
- No test for `_resample_polyline` with `n > len(path)`, `n = 2`, or a closed loop — only the happy path at line 92.
- No edge-case test for `_depth_falloff` with constant coordinates (zero range → division by zero producing NaN, which `allclose` would silently pass against itself only if the expected array were also NaN — it isn't, but the NaN itself goes unasserted).
- `test_grips_seamless` collapses all seven patterns into one boolean (line 73-78); on failure you can't tell which pattern regressed. Emit one `check` per pattern.
- No guard that extracted functions actually came from the intended file (when `printfit.py` exists, a same-named function in `__init__.py` and `printfit.py` both match; the later `exec` silently overwrites the earlier one in `NS` with no warning).