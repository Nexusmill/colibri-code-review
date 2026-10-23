# colibri bug review — tests/test_hunt_r11_fixes.py

- source: tests/test_hunt_r11_fixes.py · model: GLM-5.3-Flash (in-session)
- sha256: 171cc50866 (full sha in manifest row) · reviewed_at: 2026-10-13 · mode: bug
- context pack: live execution (PASS, 0 failures, exit 0); `_DeadWS` occurrence census (1 = definition only); the subdivision-error-path comment pin verified in current __init__ (modal teardown block); the Windows case-insensitivity reasoning of R11-1's uppercase arm traced.

## Verdict
Shippable — the strongest closer of the series (idempotence refusal incl. uppercase-ext normcase, freed-copy unhide, two-try cursor restore). No defects; three hygiene items.

## Bugs & vulnerabilities
None CONFIRMED.

## Missing safeguards
- `lines 21-25`: `_DeadWS` is dead code — defined at module level, never referenced (the in-run `_WS` at l.103-107 supersedes it; its own comment records why: the property must live on the object, not the class body scope). Delete the abandoned stub.
- `line 60`: label says "R12" — there is no R12 round; mislabels the uppercase-ext row as R11's successor.
- `line 43`: `tempfile.mkdtemp()` libdir never removed (same leak class as p2:140 — system temp accumulation per run).
