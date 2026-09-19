# BUG review: tests/test_heightmap.py

- source: `tests/test_heightmap.py`
- model: claude-fable-5-1 (in-session, colibri-review protocol)
- sha256: `49a0ccc4a7161e5d70f119222472ff09b5946d3fffb9a1ce40d9c54b325c0f06`
- reviewed: 2026-09-19 07:25
- mode: bug (test-unit hunt per the 2026-09-19 doctrine: tests are units)
- context pack: contract sources heightmap.tiling_score (262-266) and make_seamless (269-292); heightmap.py import guard (lines 11-14: bpy = None headless); git ls-files (results file tracked); live run 7/7 + git status after the run.

---
## Verdict
Green (7/7 live) and the make_seamless/tiling_score checks are real. One check is a tautology and every run mutates a tracked file.

## Bugs & vulnerabilities

**[MEDIUM] Tautological check reports PASS on nothing** - `line 17`
- What: `hm.bpy is None or hm.bpy is not None` is True for every value; the label "module imports headless (bpy tolerated)" is certified by a predicate that cannot fail. The real evidence is that line 11's import did not raise.
- Impact: false confidence only - a heightmap.py that started importing bpy unconditionally would still crash line 11 in a headless run, so no regression hides behind it. (GLM-5.3-flash rated this HIGH; MEDIUM here for that reason.)
- Fix: assert the contract - `hm.bpy is None` in a headless run (heightmap.py:11-14 sets it so) - or `"bpy" not in sys.modules`.

**[MEDIUM] Every run rewrites a git-TRACKED results file** - `line 38-39`
- What: `tests/test_heightmap_results.txt` is tracked; running the test today changed all 8 lines (line-ending drift) and left the tree dirty (`git status` -> ` M`; restored by hand).
- Impact: the tree is never clean after a test run, and `_git_do.py`'s `add -A` commits run output.
- Fix: untrack + gitignore, or write under a gitignored results dir.

**[LOW] `open().write` without `with`** - `line 38`

## Missing safeguards
- No `__main__` guard: importing the module runs the suite and calls `sys.exit` (documented as a script, so LOW).

## Remediation note (same day)
- The fix as suggested (`hm.bpy is None`) FAILED on this machine: the system python carries the pip `bpy` 5.0.1 wheel, so bpy is importable headless. The landed fix blocks it for the process (`sys.modules["bpy"] = None`) before the import and then asserts `hm.bpy is None` - the PSK-13 contract stated honestly.

## External second opinions (GLM-5.3-flash, background)
- Tautology - adopted (severity adjusted, see above).
- Handle - adopted LOW.
- "Brittle float `== 0.0` on a constant tile" - REFUTED: `tiling_score` (heightmap.py:262-266) is `mean(|a[:,0]-a[:,-1]|)`; identical columns subtract to exactly 0.0.
