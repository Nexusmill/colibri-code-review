# BUG review: tests/harness/e2e/ps_e2e.py

- source: `tests/harness/e2e/ps_e2e.py`
- model: claude-fable-5-1 (in-session, colibri-review protocol)
- sha256: `e1c5fa83b67dc8b1523aa088482117678965ca574da6ca44e98224ffaeb12774`
- reviewed: 2026-09-19 07:25
- mode: bug (test-unit hunt per the 2026-09-19 doctrine: tests are units)
- context pack: static (Blender-bound); mode enum in __init__.py (BALL at 1744/1956; apply_pattern mode gate 2614); projections._dispatch_projection handles BALL (the degeneracy battery drives it live); memory blender-headless-testing-traps (Blender masks -P exceptions as rc 0).

---
## Verdict
The honest twin: real relief measurement, real STL re-read, real exit code, a documented soft render lane. One gap in the exception path.

## Bugs & vulnerabilities

**[MEDIUM] An uncaught exception exits 0** - `whole file` (PLAUSIBLE - unverified because the file was not executed here)
- What: the cases run at module level with no try/except; under the documented invocation (`blender -b --factory-startup -P ps_e2e.py`, line 4) Blender prints the traceback and exits 0 unless `--python-exit-code` is given (the trap recorded in memory and fixed for the smoke test by PSK-18). `sys.exit(1 if FAIL else 0)` (119) is never reached.
- Fix: wrap the cases in try/except that bumps FAIL (as test_blender_smoke.py:89-96 does), or document `--python-exit-code 1` in the run line.

## Missing safeguards
- None beyond the above.

## External second opinions (grok-4.3, background)
- "`BALL` is an unsupported mode" - REFUTED: BALL is in the mode enum (__init__.py:1744, 1956), gated in apply_pattern (2614) and dispatched by projections._dispatch_projection - test_projection_degeneracy.py drives it live and passes.
- "render_check swallows failures as SKIP" - not adopted: the docstring (8-9) declares the render check soft, `SKIP` is counted and printed (117), and a non-blank failure still reaches `hard()` before any exception path.
