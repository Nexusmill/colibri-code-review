# Colibri review — src/jcodemunch_mcp/tools/get_dead_code_v2.py (bug, delta)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\tools\get_dead_code_v2.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summaries, artifacts reaudit/jcm/)
- sha256: `62e4b35c2abbc6d6f2b98d982cf982f226e202d5d2a8e46d3ee4fc153f8bcc28` (current bytes at dispatch, 2026-09-13; the post-71a9a69 bytes; DELTA against `src__jcodemunch_mcp__tools__get_dead_code_v2.py__bug__da02bd8c.md`)
- date: 2026-09-13
- mode: bug
- context pack: DELTA against the 71a9a69 record `src__jcodemunch_mcp__tools__get_dead_code_v2.py__bug__da02bd8c.md` (Signal 2 protocol-method abstention; its postscript names these bytes); this pass touches only `_package_json_entries` 254-255, the byte-identical backport of `find_dead_code._package_json_entries` fixed in the same commit (see that record). Nothing else in the file re-reviewed.

## Fixed since last review
- 71a9a69's Signal-2 finding: fixed, still holds (the file's bytes at dispatch are exactly the postscript's).

## Bugs & vulnerabilities (new this pass)
**[LOW] `lstrip("./")` in `_package_json_entries` — the twin of find_dead_code's — CONFIRMED — FIXED** - `line 255`
- Same trigger, same fix as `find_dead_code.py` (literal `./` prefix loop after slash normalisation); the same battery test is parametrised over both modules.

## Adversarial verification (Phase 3)
- The parametrised test RED on these bytes (`{'src/index.js'}` only), GREEN after; `tests/test_dead_code_v2.py` and `tests/test_dead_code_v2_reaudit.py` unchanged and green.

## Remediation postscript (same commit)
The fix was applied after this review hashed the bytes above; the file is now `f073fc94624e1f5cbbd708cd3c3e715f03517ca516942fa3462d290690ab88aa`. TDD: `tests/test_tail_batch4_reaudit.py` (14 tests across the eight files of this batch) - 11 RED on the old bytes (each for its own reason, verified by the per-test failure), 3 controls green throughout, GREEN after.
