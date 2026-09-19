# BUG review: tests/test_blender_smoke.py

- source: `tests/test_blender_smoke.py`
- model: claude-fable-5-1 (in-session, colibri-review protocol)
- sha256: `a43548fe793670773d20b75dcfb458e77bdc89df122fd8692d3dfeea59da99f2`
- reviewed: 2026-09-19 07:25
- mode: bug (test-unit hunt per the 2026-09-19 doctrine: tests are units)
- context pack: static (needs `blender -b -P`): __init__.py cross-checks - `_save_gray_png` re-exported at line 81 (from heightmap), bl_idnames patternskin.apply (2245) / export_stl (3431), PATTERNSKIN_OT_generate_grip (4215) assigns `s.pattern = outp` at 4242, litho_res/litho_image props (1946); remediation row 2026-08-15 PSK-18; live headless-Blender probe of `hasattr(bpy.ops.patternskin, ...)`.

---
## Verdict
The operator-driving checks are real and their targets exist. The very first check, "add-on registers", cannot fail.

## Bugs & vulnerabilities

**[MEDIUM] `hasattr(bpy.ops.patternskin, "apply")` is True whether or not the add-on registered** - `line 39`
- What: `bpy.ops.<module>.<name>` resolves lazily to an operator wrapper for ANY name; the error only surfaces on call/poll.
- Live (Blender 5.1.2, `-b --factory-startup`, add-on NOT loaded): `hasattr(bpy.ops.patternskin, "apply")` -> True, `hasattr(bpy.ops.patternskin, "nonexistent_zzz")` -> True, while `bpy.ops.patternskin.apply.poll()` raises "could not be found".
- Impact: a failed `PS.register()` (or a renamed operator) still prints "ok add-on registers"; the run only goes red two checks later when `bpy.ops.patternskin.apply()` raises inside `run()` - so no green hides behind it, but the check is decorative.
- Fix: `check(bpy.types.Operator.bl_rna_get_subclass_py("PATTERNSKIN_OT_apply") is not None, ...)` (registered-class lookup) or `check(PS.PATTERNSKIN_OT_apply.is_registered, ...)`.

## Missing safeguards
- None beyond the above; PSK-18 (2026-08-15) already made an uncaught exception count as a failure (89-96).

## External second opinions (grok-4.3, background)
- "grip check always true because `s.pattern` still holds the earlier tex" - REFUTED: `PATTERNSKIN_OT_generate_grip.execute` assigns `s.pattern = outp` (__init__.py:4242), so line 67 checks the NEW grip file.
- "sys.path never undone" / "removes every mesh" - not adopted: one-shot `--factory-startup` run, documented at line 3.
