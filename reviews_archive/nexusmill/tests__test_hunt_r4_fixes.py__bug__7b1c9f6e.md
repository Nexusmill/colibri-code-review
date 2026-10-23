# colibri bug review — tests/test_hunt_r4_fixes.py

- source: tests/test_hunt_r4_fixes.py · model: GLM-5.3-Flash (in-session)
- sha256: 7b1c9f6e8b (full sha in manifest row) · reviewed_at: 2026-10-13 · mode: bug
- context pack: live execution (PASS, 0 failures, exit 0); `ui_section` verified as StringProperty(default="OBJECT") at __init__.py:1811 — the disjunction's first term is therefore always true in the clean state.

## Verdict
Shippable except R4-7: its "runtime-only keys ignored" row lets each hostile key escape alone.

## Bugs & vulnerabilities

**[MEDIUM] R4-7's disjunctive assert never pins either hostile key individually** - `lines 112-114`
- Verbatim: `check(s.ui_section != "SYSTEM" or not hasattr(s, "ui_section") or s.ai_parts_active != 999, "R4-7 runtime-only keys ignored (ui_section=%r, active=%r)" % (...))`
- What: with `ui_section` defaulting to "OBJECT" (≠ "SYSTEM"), the FIRST disjunct is true in every clean run — so the row stays green even when the hostile `ai_parts_active=999` WAS applied by a regressed `_load_preset`. Symmetrically, a ui_section-only escape is covered by the third term. Each key individually always escapes; only both applied together trips the row.
- Trigger: `_load_preset` regressing to copy `ai_parts_active` from preset settings while leaving ui_section at its default.
- Producing caller: an edit to `_load_preset`'s key filter (`_PRESET_KEYS`).
- Broken behavior: the exact regression the row names ships green.
- Fix: two rows — `check(s.ui_section != "SYSTEM", ...)` and `check(s.ai_parts_active != 999, ...)` (the hasattr term is dead: `s.ui_section` raises before it when absent).
- Status: **CONFIRMED** (default verified; boolean structure traced).

## Missing safeguards
- `line 91`: `empty_dir = tempfile.mkdtemp()` never removed.
- The successful sleeve object from R4-3 stays in bpy.data (dies with the process — cosmetic).
