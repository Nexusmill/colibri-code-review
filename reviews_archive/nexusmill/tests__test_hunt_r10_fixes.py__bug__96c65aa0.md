# colibri bug review — tests/test_hunt_r10_fixes.py

- source: tests/test_hunt_r10_fixes.py · model: GLM-5.3-Flash (in-session)
- sha256: 96c65aa054 (full sha in manifest row) · reviewed_at: 2026-10-13 · mode: bug
- context pack: live execution (PASS, 0 failures, exit 0); both `check(True` sites verified at lines 79 and 89; the crash-enforcement path traced (a raise in the guarded call aborts the battery → nonzero exit → runner FAIL).

## Verdict
Shippable, with one LOW class finding: two verdict rows are unfailable by construction. Their contracts ARE enforced — but by crash, not by the check.

## Bugs & vulnerabilities

**[LOW] Two `check(True, ...)` rows cannot fail — enforcement is crash-based only** - `lines 78-79, 89`
- Verbatim (l.79): `check(True, "R10-3 sel_click.cancel on a dead context completes (stubbed)")`; (l.89): `check(True, "R10-4 _check_3mf_ceilings: 4M/4M pass, over-either raises")`
- What: both rows print "ok" for every outcome. The real assertions live elsewhere: a raise in `cancel()` (l.78) or in the pass-case `_check_3mf_ceilings` call (l.82) escapes uncaught and aborts the battery (nonzero exit, runner FAIL) — loud, but no FAIL row ever prints, and any drift that makes the call merely misbehave (not raise) is unchecked.
- Trigger: `sel_click.cancel` regressing to a wrong-but-non-raising outcome; nothing observes it.
- Producing caller: an edit to `cancel()`/`_ui_teardown` semantics.
- Broken behavior: none today — recorded as the banned unfailable-row class (G35) at its mildest.
- Fix: the r11 pattern — `try: ...; ok = True; except Exception: ok = False` then `check(ok, ...)`.
- Status: **CONFIRMED** (unfailable expressions verified; crash path traced).

## Missing safeguards
- None beyond the above; the R10-1 material-slot rows are exemplary (user materials survive, vanished-selection SKIP sentinel).
