# colibri bug review — tests/test_hunt_r8_fixes.py

- source: tests/test_hunt_r8_fixes.py
- model: GLM-5.3-Flash (in-session)
- sha256: 047a752f825c (full sha in manifest row)
- reviewed_at: 2026-10-13 · mode: bug
- context pack: live execution under junk/venv-battery (PASS, 0 failures, exit 0); R10-1 material-slot semantics (newest apply lands in LAST slot); pin provenance verified (`try: o.select_set(True)` = 2 in __init__ + 1 in apply_core = 3, threshold `>= 2` met); `_PSCancellableApply.modal` ESC containment read from current bytes.

## Verdict
Shippable except for one row that lies: the R8-2 image pin is a tautology that prints "ok" unconditionally, and the provenance check it defers to ("image pin below") does not exist.

## Bugs & vulnerabilities

**[MEDIUM] R8-2's image-provenance row can never fail — `or True` tautology, the exact banned class** - `line 88`
- Verbatim: `check(t_a.endswith("hex") or "hex" not in t_a.lower() or True, "R8-2 (image pin below)")`
- What: `X or Y or True` is a theorem — the row reports "ok" for every possible file path. `t_a` is referenced only at lines 87-88 (fetch + dead check); lines 89-102 assert material identity (`is m_a` / `is m_10`) but never the texture-image filepath, so the deferred pin never happens.
- Trigger: any regression that swaps, forks, or blanks the pattern image behind a shared material — e.g. the PS_PatternTex node pointing at the wrong image datablock.
- Producing caller: an edit to `_apply_finish`'s material/image reuse key.
- Broken behavior: a real behavioral pin reports green while verifying nothing — the G35 class ("or True" predicate, PS-AA precedent in tests/harness/bpy_patternskin.py).
- Fix: either delete the dead row, or make it the real pin: `check(t_a.lower().endswith(...expected...), "R8-2 image provenance")` against the pattern path actually passed (`p1`/`p2`), or assert `m_a.node_tree.nodes["PS_PatternTex"].image.filepath == bpy.path.abspath(p1)`.
- Status: **CONFIRMED** (always-true expression verified by evaluation of the boolean structure; `t_a` usage census verified).

## Missing safeguards
- Scrape concatenates `__init__ + apply_core` only; benign today (all pins verified present, incl. "ONLY what a failure left here" in apply_core) — same common.py fragility note as p2.
