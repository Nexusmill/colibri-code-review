# colibri bug hunt synthesis — PatternSkin test suite, tranche 2 (2026-10-13)

- date: 2026-10-13 · model: GLM-5.3-Flash (in-session) · mode: bug
- scope covered: tests/test_hunt_p2_fixes.py, test_hunt_p3_fixes.py, test_hunt_p5_fixes.py, test_hunt_r8_fixes.py — the four batteries retargeted around the 2026-10-01 apply_core extraction (full per-file reviews; all four run live: PASS, 0 failures each).
- cumulative coverage after tranche 1+2: 7 of 193 test-tree files deep-reviewed.

## Findings, ranked
1. **[MEDIUM] r8-2 image-provenance row is an `or True` tautology** (tests/test_hunt_r8_fixes.py:88) — prints "ok" unconditionally; `t_a` used only in the dead check; the deferred "image pin below" never exists. The G35 banned class verbatim (PS-AA precedent). Fix: delete or assert the PS_PatternTex image filepath.
2. **[LOW] p2 P2-3 `tripped` computed, never asserted** (tests/test_hunt_p2_fixes.py:143,156) — label claims "cap refuses AND output removed", only the filesystem half is pinned; guard-message rot stays green. Fix: `check(tripped and not outs, ...)`.
3. **Hygiene (p2)**: dead `if False else None` expression (l.150-151) and unused `_poison` (l.139).
4. **Cross-file fragility note (p2/p3/r8)**: the `src` scrape is `__init__ + apply_core` — written before common.py existed (2026-10-02). Verified benign today (no pinned string lives exclusively in common.py; all thresholds met), and any future move fails LOUDLY (false FAIL) rather than vacuously — but adding `common.py` to the concatenation retires the fragility.

## Clean units
- **p3: 0 findings** — the evtimer retarget (structural `>=11` alias count + the three-arm behavioral twin/foreign/identity-less drive) is the model for contract-retargeting.
- **p5: 0 findings** — G41 posture intact (RED-first D3-T2 with twin-home patch/restore; positional C7 window re-measured and still covering).

## Not covered this tranche
test_hunt_p1/p4, r1-r7, r9-r11 (12 hunt batteries), the perfection series (7), the domain suites (math/projections/ai_*/…), and the harness/probe tree. The evtimer tranche-1 findings (T1d consume-branch row; GUI probe provenance stamp) remain open findings awaiting owner-disposition.
