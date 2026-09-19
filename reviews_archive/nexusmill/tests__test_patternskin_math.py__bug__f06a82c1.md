# BUG review: tests/test_patternskin_math.py

- source: `tests/test_patternskin_math.py`
- model: claude-fable-5-1 (in-session, colibri-review protocol)
- sha256: `f06a82c18cf85cf1ce7588643a627323d8d5e2a46835be2face69a44beb38949`
- reviewed: 2026-09-19 07:25
- mode: bug (test-unit hunt per the 2026-09-19 doctrine: tests are units)
- context pack: jCodemunch outline (9 tests, check(), _SCRAPED scrape); contract sources printfit.print_check/slicer_notes, projections._resample_polyline/_parallel_transport_frames, heightmap.tiling_score/make_seamless (signatures verified against every call); remediation row 2026-07-25 TEST-PSMATH-1; prior K3 review e172da66; live runs (script 14/14 green; pytest 9.0.2 9 passed; wrong-target proof).
- delta against: .colibri_reviews/tests__test_patternskin_math.py__bug__e172da66.md (moonshotai/kimi-k3, 2026-07-20) - file rewritten 2026-07-25 (TEST-PSMATH-1)

---
## Verdict
Green as a script (14/14 live) but its "Also collectable by pytest" claim (line 4) is false in the dangerous direction: under pytest eight of the nine tests cannot fail.

## Bugs & vulnerabilities

**[HIGH] `check()` never asserts, so under pytest every test but one passes unconditionally** - `line 81-85` (claim at `line 4`)
- What: `check()` prints and bumps `_F`; no test function asserts on `_F`; only `test_all_symbols_resolved` (line 92) uses `assert`. The `__main__` loop (167-181) is the only place `_F` is read.
- Trigger: `pytest tests/test_patternskin_math.py` (pytest 9.0.2 is installed here).
- Live proof: with `NS["_combine_heights"]` and `NS["print_check"]` swapped for deliberately wrong lambdas, `test_combine`, `test_print_check` and `test_frames` printed 5 FAIL lines and raised nothing; `pytest -q` reports `9 passed in 0.32s`.
- Impact: any pytest-based CI certifies broken relief math.
- Fix: make `check()` raise `AssertionError(label)` when `cond` is false - the script loop already catches AssertionError per test (174-177) - or `assert _F == 0` at the end of each test.

## Fixed since last review (K3 e172da66, 2026-07-20)
- #2 "one unexpected exception kills the entire run" - FIXED: per-test try/except at 174-179.
- #3 "`assert m` disabled under -O" - FIXED: `if not _m` at 68.
- #1 "fragile regex extraction" - STILL OPEN, reduced to LOW: a miss now lands in `_MISSING` (68-69) and fails `test_all_symbols_resolved`; a truncated-but-compiling slice (66-74) remains undetectable. Verified live: all 9 symbols resolve today.
- #4 "file handles never closed / missing-file error raw" - HALF FIXED: the missing-file half is reported via `_MISSING` (63-65); `open(ADDON).read()` at 62 still has no `with` (LOW).
- #5 "print_check tests assert exact warning counts" - STILL OPEN (129-131), LOW; verified against `print_check` (printfit.py:9-18, two independent warnings) the counts are currently right.

## Missing safeguards
- K3's degenerate-input gaps still stand: straight-line / duplicate-point frames, `_resample_polyline` with `n > len(path)`, constant-coordinate `_depth_falloff`.

## External second opinions (grok-4.3, background)
- "sys.path mutation" - not adopted: the standard standalone-script pattern, no defect.
- "open() handle" - already tracked as K3 #4.
