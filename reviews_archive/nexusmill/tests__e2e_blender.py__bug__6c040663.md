# BUG review: tests/e2e_blender.py

- source: `tests/e2e_blender.py`
- model: claude-fable-5-1 (in-session, colibri-review protocol)
- sha256: `6c0406639ae81e39bf99b44dee29a6b003de872b59609e546d69e8c72787edb3`
- reviewed: 2026-09-19 07:25
- mode: bug (test-unit hunt per the 2026-09-19 doctrine: tests are units)
- context pack: static (Blender-bound); twin tests/harness/e2e/ps_e2e.py read side by side; only references = tests/TEST_REPORT.md:12/34; CLAUDE.md (the AppData session path was retired 2026-07-21); live Blender 5.1.2 probe of wm.stl_export's ascii_format default (False).

---
## Verdict
A dead, machine-bound duplicate of tests/harness/e2e/ps_e2e.py that cannot fail. Delete it (gated deletion) or reduce it to a pointer.

## Bugs & vulnerabilities

**[HIGH] No exit code - the run cannot go red** - `line 60`
- What: prints "N FAILED" and ends; `blender --background --python` exits 0 regardless, and an uncaught exception also exits 0 unless `--python-exit-code` is passed (the class PSK-18 fixed in test_blender_smoke.py on 2026-08-15).
- Fix: `sys.exit(1 if FAIL else 0)` plus a try/except that counts an exception as a failure - or delete the file in favour of ps_e2e.py, which already does both.

**[MEDIUM] Hard-coded, retired machine path** - `line 16`
- What: the default BASE is the pre-2026-07-21 AppData session folder; without `PATTERNSKIN_BASE` the import fails on this machine (and, per the above, still exits 0).

**[MEDIUM] Duplicate of the harness twin** - whole file vs `tests/harness/e2e/ps_e2e.py`
- What: ps_e2e.py has the same three cases plus BALL, the EEVEE render check and a real exit; only tests/TEST_REPORT.md still points here.

## Missing safeguards
- (superseded by the twin)

## External second opinions (GLM-5.3-flash, background)
- No exit code - adopted. Hard-coded path - adopted.
- "ASCII STL misparsed as a triangle count" - REFUTED live: Blender 5.1.2 `bpy.ops.wm.stl_export` has `ascii_format` default False ("export as binary otherwise"), read via `--python-expr` from the operator's RNA; the trigger does not occur with the call as written.
- "mesh datablock leak" - not adopted: one-shot headless run.
