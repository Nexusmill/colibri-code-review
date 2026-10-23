# colibri bug review — tests/test_hunt_r2_fixes.py

- source: tests/test_hunt_r2_fixes.py · model: GLM-5.3-Flash (in-session)
- sha256: 6e75c9e022 (full sha in manifest row) · reviewed_at: 2026-10-13 · mode: bug
- context pack: live execution (PASS, 0 failures, exit 0); the delegation chain verified against current bytes — `PS._live_build` is a shim (`__init__.py:9487-9488` → `_apply_core._live_build`), apply_core binds `_save_gray_png` via `from .heightmap import` (`apply_core.py:17`, 1 unqualified call site); p5's D3-T2 twin-patch comment as in-repo corroboration.

## Verdict
One dead row: R2-8's failure-injection mock is inert for the code it targets — the row verifies nothing about failed saves.

## Bugs & vulnerabilities

**[MEDIUM] R2-8's `_save_gray_png` mock patches the wrong namespace — the row passes vacuously** - `lines 168-185`
- Verbatim: `PS._save_gray_png = _boom` (l.175) then `PS._live_build(p, s, PS.grip_pattern("HEX", 6, 128), lp)` (l.177) then `check(not os.path.exists(live_png), "R2-8 no ps_live png left after a failed save")` (l.180)
- What: `PS._live_build` delegates to `apply_core._live_build`, whose `_save_gray_png` call resolves in apply_core's own globals (`from .heightmap import`, apply_core.py:17). Patching the PatternSkin-namespace attribute never reaches it — the save never fails, the except at l.178 never fires, and the check passes because the SUCCESS path also removes the temp png (proven by r1's F11 row).
- Trigger: none needed — the row is green today without its failure condition ever occurring.
- Producing caller: any future edit; the row cannot detect a regression in the failed-save cleanup it names.
- Broken behavior: a claimed failure-path verdict row with zero failure-path coverage (the real behavior IS covered by p5's D3-T2, which patches both homes — but this row's own claim is false).
- Fix: patch both homes (p5 pattern): also `PS.apply_core._save_gray_png = _boom` with restore in the existing finally.
- Status: **CONFIRMED** (delegation + import verified against current bytes; live PASS consistent with vacuity).

## Missing safeguards
- R2-1's ast dead-code scan reads only `node.body` directly — a def-after-return inside a nested branch (if/else) escapes. Hardening note.
