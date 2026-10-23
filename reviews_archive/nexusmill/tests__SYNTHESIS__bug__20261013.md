# colibri bug hunt synthesis — PatternSkin test suite (partial coverage, stated)

- date: 2026-10-13 · model: GLM-5.3-Flash (in-session) · mode: bug
- scope covered: tests/test_hunt_evtimer.py, tests/harness/probes/ps_modal_evtimer_gui.py, tests/_runtests.py (full per-file reviews) + staleness verification of the open G35 rows against current bytes.
- scope NOT covered this pass: the remaining 35 suite modules (test_hunt_p*/r*_fixes.py, test_perfection_*.py, test_projections.py, …) and 116 harness probes — fresh ground for future passes; no manifest rows were written for them.

## Cross-file findings, ranked
1. **[MEDIUM] evtimer battery: the 5.0-shape consumption branch is unpinned** (tests/test_hunt_evtimer.py:88-98) — the comment claims "our own timer is consumed"; no row reaches `next(self._ps_gen)` (PatternSkin/__init__.py:576). A never-consume mutation of the aliased prologue (line 536) survives all six checks green. Fix: T1d row with gen=True + own-timer event.
2. **[MEDIUM] GUI probe: no bytes-provenance stamp** (tests/harness/probes/ps_modal_evtimer_gui.py:26-27, 82-83) — addon_enable resolves via Blender's path, RES records no `PS.__file__`/sha256, so the RED→GREEN PASS cannot be tied to the reviewed bytes. Fix: stamp both in setup_and_invoke.
3. **[LOW] GUI probe hard-coded absolute machine paths** (lines 25, 73) — derive from __file__ like the battery does.
4. **[LOW] runner exit-code-only trust + silent SKIP** (tests/_runtests.py:10-12, 25) — no live offender today (static sweep: all 38 files exit on failure count or assert); hardening notes.

## G35 staleness verification (current bytes, 2026-10-13) — 6 open rows → verified-stale
| row (file) | evidence |
|---|---|
| tests/_runtests.py (exit-0 aggregation) | worst=1 on any nonzero (l.23-24), sys.exit(1 if worst else 0) (l.31) |
| tests/test_patternskin_math.py (check() bumps _F, nothing asserts) | check() now RAISES on failure (docstring documents the 2026-09-19 fix) |
| tests/test_heightmap.py (tautology) | cited line now `R = []`; tautology survives only as a scar comment |
| tests/test_blender_smoke.py (hasattr) | cited line is now a comment documenting the lazily-resolving-name scar |
| tests/test_ai_select.py (unexercised anti-fusion) | test_single_bridge_does_not_fuse now builds the noisy-bridge input and asserts `pure and nparts == 2` |
| tests/test_part_export.py (mkdtemp leak) | line 19: TemporaryDirectory with "(was a mkdtemp leak" scar comment |
| tests/test_accel_tiers.py (glyph + exit halves) | label now ASCII (scar comment); sys.exit(1 if _F else 0) at line 195 |

Live execution evidence: tests/test_hunt_evtimer.py run 2026-10-13 under junk/venv-battery — ALL PASSED, exit 0.
