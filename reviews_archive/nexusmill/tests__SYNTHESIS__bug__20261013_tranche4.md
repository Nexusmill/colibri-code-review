# colibri bug hunt synthesis — PatternSkin test suite, tranche 4 (2026-10-13)

- date: 2026-10-13 · model: GLM-5.3-Flash (in-session) · mode: bug
- scope covered: tests/test_hunt_r1-r7_fixes.py — the hunt series is now COMPLETE (16/16 batteries reviewed). All seven run live: PASS, 0 failures each.
- cumulative coverage: 19 of 193 test-tree files deep-reviewed.

## Findings, ranked
1. **[MEDIUM] r2-8's failure-injection mock is inert — the row passes vacuously** (tests/test_hunt_r2_fixes.py:168-185). `PS._save_gray_png = _boom` never reaches the call: `PS._live_build` delegates to `apply_core._live_build` (`__init__.py:9487`), whose `_save_gray_png` resolves from apply_core's own `from .heightmap import` (`apply_core.py:17`). The save never fails; the row is green via the success path's own cleanup (r1 F11 proves it). The real behavior is covered by p5's D3-T2 (both homes patched) — but this row's own claim is false. Fix: twin-home patch.
2. **[MEDIUM] r1's F1 writes into the live `~/.spector/inbox` with happy-path-only cleanup** (tests/test_hunt_r1_fixes.py:59-74). A crash strands a junk STL in the user's real inbox (consumable by the running Spector app); a live daemon consuming the file mid-run makes the row spuriously red. Fix: try/finally + a sandboxed inbox.
3. **[MEDIUM] r4's R4-7 disjunctive assert lets each hostile preset key escape alone** (tests/test_hunt_r4_fixes.py:112-114). `ui_section` defaults "OBJECT" → the first disjunct is always true → a regressed `_load_preset` applying `ai_parts_active=999` ships green. Fix: two separate rows.
4. **[LOW] r5's R5-3 pin fallback (`or "1e-3" in src`) accepts any 1e-3 anywhere** (tests/test_hunt_r5_fixes.py:66) — the structural pin stops pinning on refactor; behavioral row above still guards.
5. **Hygiene:** r1 unused numpy import + the odd importlib.reload; r3:106 third `if False else None` dead expr; r4:91 mkdtemp leak; r6/r7 real-license-path writes are finally-restored (accepted pending an injection seam — noted, not charged).

## Clean units
r3, r6, r7 — zero findings (r3's busy-refusal trio, r6's race-ordering probe, r7's cache-sig and fetch-decoupling pairs are all model rows). r5 clean behaviorally.

## Series verdict (all 16 hunt batteries)
The hunt series is fundamentally sound: verdict-named rows, RED-first posture, real failure injection almost everywhere. The defect concentration is exactly where the colibri test-specific classes predict: rows whose assertion is weaker than their label (r2-8 vacuous mock, r4-7 disjunction, r10 check(True)s, r8 or-True, p2 tripped) and isolation leaks at real user paths (r1 inbox). Six of the seven findings across tranches 2-4 share ONE root pattern: **the label claims more than the check enforces** — a cheap audit target for a future sweep (one grep for `check(True`, `or True`, disjunctive asserts, and single-namespace mocks of twin-bound symbols).
