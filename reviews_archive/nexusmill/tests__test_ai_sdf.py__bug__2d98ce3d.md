# BUG review: tests/test_ai_sdf.py

- source: `tests/test_ai_sdf.py`
- model: claude-fable-5-1 (in-session, colibri-review protocol)
- sha256: `2d98ce3daa717c74eab83abfe3e5ca8a5ecd1d5aef70468de5ae67f11c7cb0b2`
- reviewed: 2026-09-19 07:25
- mode: bug (test-unit hunt per the 2026-09-19 doctrine: tests are units)
- context pack: contract source ai_select.refine_parts_by_geometry (350; signature verified against all four calls); ai_select.py import header (1-25: no relative imports, so spec_from_file_location is a valid load); live run PASS.

---
## Verdict
Clean. Real asserts against literal part counts, deterministic inputs, the real module under test.

## Bugs & vulnerabilities
None confirmed.

## Missing safeguards
- The `__main__` chain (line 52) stops at the first failing assert, so a red run reports one failure, not all; the exit code is non-zero, so it is honest (LOW).

## External second opinions (GLM-5.3-flash, background)
- "No real defects found" - agrees; its checklist (tautology, swallowed exceptions, runner, skips, shared state, bounds, paths, determinism, leaks) matches this pass.
