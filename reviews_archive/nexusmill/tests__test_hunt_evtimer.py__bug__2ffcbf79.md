# colibri bug review — tests/test_hunt_evtimer.py

- source: tests/test_hunt_evtimer.py
- model: GLM-5.3-Flash (in-session, account:zai-individual-coding-plan/GLM-5.3-Flash)
- sha256: 2ffcbf799c66d0de51ee3469f36ae4c939827190490b6d66975965428147c836 (prefix recorded pre-review; full sha in manifest row)
- reviewed_at: 2026-10-13 · mode: bug
- context pack: PS-5.1-MODAL-EVTIMER debug record (.colibri_reviews/PatternSkin____init__.py__debug__ab2848c1.md), AGENT_STATE 2026-10-04 entries, G35 manifest (no prior rows on this file), current _PSCancellableApply.modal (PatternSkin/__init__.py:531-594, read from disk — index predates fix 40d5d459), live battery execution.

## Verdict
Shippable — the battery is well-built (RED-first rows, loud failure modes, live-verified green today). Single biggest risk: the 5.0-shape consumption branch it claims to pin is asserted nowhere, so a never-consume regression of exactly the kind this file exists to prevent would ship ALL PASSED.

## Bugs & vulnerabilities

**[MEDIUM] The 5.0-shape own-timer consumption branch is pinned nowhere — the T1b comment claims it** - `lines 88-98`
- What: the block comment promises "a foreign timer passes through, our own timer is consumed", but both T1b rows run idle ops (`_ps_gen=None`); the consume path (`PatternSkin/__init__.py:558-576`, `next(self._ps_gen)` at line 576) is reached by no row. T1c arms a generator but sends ESC, not TIMER.
- Verbatim (test): `r = op.modal(ctx, types.SimpleNamespace(type="TIMER", timer=_T_OWN))` followed by `check(r == {"PASS_THROUGH"}, "T1b 5.0-shape own timer (idle op) still PASS_THROUGH")`
- Trigger (surviving mutation): weaken the aliased prologue at PatternSkin/__init__.py:536 from `_evt_timer is not None and _evt_timer != self._ps_timer` to `_evt_timer is not None` (drop the own-timer distinction). Trace against current bytes: T1a/T1b/T3b all expect PASS_THROUGH (unchanged — the mutation returns the same value earlier), T1c is the ESC branch, T2 is the raise path, T3a is static. ALL six checks stay green while every 5.0-shape interactive apply hangs forever (gen never advances, `_PS_APPLY_BUSY` never releases — the original PS-5.1 wedge, 5.0 flavor).
- Producing caller: a future edit to the aliased prologue (PatternSkin/__init__.py:536) — precisely the file region this battery guards.
- Impact: a 5.0-compatibility regression ships with the battery reporting ALL PASSED.
- Fix: add a T1d row — `op = fresh_op(gen=True)`, set `op._ps_timer = _T_OWN`, send `{"TIMER", timer=_T_OWN}` with a one-tick fake gen, and assert the tick was consumed (gen advanced / non-PASS_THROUGH return), making the comment's claim a tested invariant.
- Status: **CONFIRMED** (end-to-end trace against current bytes; the GUI probe cannot cover this — Blender 5.1 events carry no `timer` attribute, so the 5.0-shape consume arm exists only here).

## Missing safeguards
- T3a's invariant scan globs only `PatternSkin/*.py` top level; subpackages (`smartselect/`) are unscanned while the check's label claims "anywhere in PatternSkin". No current trigger — zero `event.timer` reads in any subpackage pre- or post-fix — so this is a hardening note, not a defect (producing-caller rule).
- Execution evidence: battery run live 2026-10-13 under junk/venv-battery — ALL PASSED, exit 0 (16 checks).
