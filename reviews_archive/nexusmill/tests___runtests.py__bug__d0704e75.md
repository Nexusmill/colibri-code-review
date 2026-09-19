# BUG review: tests/_runtests.py

- source: `tests/_runtests.py`
- model: claude-fable-5-1 (in-session, colibri-review protocol)
- sha256: `d0704e754d12e34f64fab90f1f574ecde6c93eec46a5feba4bcd260e6e8e85af`
- reviewed: 2026-09-19 07:25
- mode: bug (test-unit hunt per the 2026-09-19 doctrine: tests are units)
- context pack: directory listing of tests/ (9 PatternSkin unit tests); git ls-files (tests/_testresults.txt is tracked); only reference = tests/TEST_REPORT.md:15; live run of its children (test_accel_tiers.py exits 1 today).

---
## Verdict
Not usable as a CI runner: it cannot signal failure. It also runs a third of the suite it claims to run.

## Bugs & vulnerabilities

**[HIGH] The runner exits 0 and prints "done" whatever its children return** - `line 6-10`
- What: each child's `returncode` is written into the report file (line 7) but never aggregated; there is no `sys.exit`, so the process ends 0 on every path.
- Trigger: any child fails or crashes. Live today: `tests/test_accel_tiers.py` exits 1 with a traceback (see its review) and this runner still ends "done", exit 0.
- Impact: a caller or CI keyed on the exit code sees success; the only evidence is buried in a text file.
- Fix: `worst = max(worst, r.returncode)` per child, print one PASS/FAIL line per file on stdout, `sys.exit(1 if worst else 0)`.

**[MEDIUM] The test list is stale - 3 of 9 PatternSkin unit tests run** - `line 3`
- What: only test_patternskin_math, test_assetforge and test_accel_tiers are listed; test_heightmap, test_ai_sdf, test_ai_select, test_part_export, test_projections and test_projection_degeneracy (all headless, all green today) never run here. tests/TEST_REPORT.md:15 still says "run all CPU suites at once".
- Fix: glob `test_*.py` and skip the Blender-bound smoke test explicitly, or list every headless file.

**[MEDIUM] Every run rewrites a git-TRACKED file** - `line 4`
- What: `tests/_testresults.txt` is tracked (`git ls-files`), so each run dirties the tree, and `_git_do.py`'s `add -A` commits run output as noise.
- Fix: write under a gitignored results dir, or untrack + gitignore the file.

**[LOW] Child output decoded with the console code page** - `line 6` (PLAUSIBLE - unverified because the accel child dies before printing a non-cp1252 glyph)
- What: `text=True` without `encoding=`; a child that prints a glyph outside cp1252 would raise UnicodeDecodeError here and abort the runner mid-loop.
- Fix: `encoding="utf-8", errors="replace"` (and `PYTHONUTF8=1` in the child env).

## Missing safeguards
- No per-child `timeout`; a hung test hangs the runner.
- Nothing on stdout distinguishes a green run from a red one.
