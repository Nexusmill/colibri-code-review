# BUG review: tests/test_part_export.py

- source: `tests/test_part_export.py`
- model: claude-fable-5-1 (in-session, colibri-review protocol)
- sha256: `7b3589c6f904061fba2e44bcd57ff22a8fe42e618eb775214e5c8e2215ce8d59`
- reviewed: 2026-09-19 07:25
- mode: bug (test-unit hunt per the 2026-09-19 doctrine: tests are units)
- context pack: contract sources part_export.split_parts (53), write_stl_binary (86), export_parts (326), write_3mf_facecolor (168) - signatures verified against every call; remediation row 2026-07-25 (the fmt=3MF staleness this file's NOTE describes, already fixed); live run PASS.

---
## Verdict
Green and the round-trip assertions are genuine (bytes re-read, packages re-parsed). One fixture leak.

## Bugs & vulnerabilities

**[LOW] Temp directory never removed** - `line 19`
- What: `tempfile.mkdtemp()` with no cleanup and no `finally`; every run (and every failed run) leaves STL/3MF files in the system temp dir.
- Fix: `with tempfile.TemporaryDirectory() as d:` around the body, or `atexit.register(shutil.rmtree, d, ignore_errors=True)`.

## Missing safeguards
- Module-level asserts: the first failure aborts with a traceback and no summary (acceptable for a script).

## External second opinions (GLM-5.3-flash, background)
- Temp leak - adopted (its only finding; it also verified the STL size arithmetic and the 3MF re-parse, agreeing they are real checks).
