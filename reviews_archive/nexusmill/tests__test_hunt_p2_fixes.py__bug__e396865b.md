# colibri bug review — tests/test_hunt_p2_fixes.py

- source: tests/test_hunt_p2_fixes.py
- model: GLM-5.3-Flash (in-session)
- sha256: e396865b80d0 (full sha in manifest row)
- reviewed_at: 2026-10-13 · mode: bug
- context pack: live execution under junk/venv-battery (PASS, 0 failures, exit 0); pin-target provenance verified against current PatternSkin/{__init__,apply_core,common}.py bytes; G35 manifest; the 2026-10-01 apply_core-extraction and 2026-10-02 common.py tranches (commit histories).

## Verdict
Shippable — five solid behavioral rows (depsgraph-failure survival, autofit ratio, bomb guard, exe-name, modal conversion) plus a hostile-preset promo, all green live. Biggest gap: the bomb-guard row's "refuses" half is computed and then never asserted.

## Bugs & vulnerabilities

**[LOW] P2-3 computes `tripped` but never asserts it — the label claims more than the check pins** - `lines 143-160`
- Verbatim: line 156 `tripped = "bomb guard" in str(e)` and line 159 `check(not outs, "P2-3 lying-zip: the actual-bytes cap refuses AND the partial output is removed (no library poisoning; outs=%r)" % outs)`
- What: `tripped` occurs exactly twice in the file (init at 143, assignment at 156) — it is dead after assignment. The row's label asserts "cap refuses AND output removed" but only the filesystem half (`not outs`) is checked.
- Trigger: the bomb guard rots into a refusal with a different message/type (or a different pre-validation refuses before extraction) — the row stays green while the actual-bytes cap specifically no longer fires.
- Producing caller: an edit to the guard's message or to `_LyingInfo`-era validation ordering in `PATTERNSKIN_OT_install_default_library.execute`.
- Broken behavior: none at runtime — the escaping class is "guard-specific regression invisible to its own verdict row". The primary failure mode (guard deleted → 61MB extracts → `outs` non-empty → FAIL) IS caught, hence LOW not MEDIUM.
- Fix: fold it in — `check(tripped and not outs, ...)`.
- Status: **CONFIRMED** (occurrence count verified against current bytes).

## Missing safeguards
- `lines 150-151`: dead expression `... .invoke(sh, bpy.context, None) if False else None` — an intentional disable kept as live-looking code; delete or comment it out.
- `line 139`: `_poison = {...}` assigned and never used.
- The `src` scrape concatenates `__init__.py + apply_core.py` only ("the add-on as a whole" comment predates common.py, 2026-10-02). Verified benign today — no pinned string lives exclusively in common.py (`_forge_exe_name()`=3 in `__init__`, `def _work_fin...`=1, `_ai_begin("Load saved scan")`=1, `# Pure delegation`=1) — but any future helper move to common.py breaks pins LOUDLY (false FAIL, not vacuous pass). Adding `common.py` to the concatenation removes the fragility.
