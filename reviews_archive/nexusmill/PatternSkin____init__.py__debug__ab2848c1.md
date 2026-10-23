# Colibri debug record - PatternSkin/__init__.py

- source: `PatternSkin/__init__.py` (sha256 ab2848c127b6069abc6722f3030bac307e01a7436d3c109295d45c85d158a548, 510,008 bytes, current at time of debug; the blender_dev/addons twin is the same bytes)
- reviewer: in-session (GLM-5.3-Flash, ZCode), colibri Phase D debug modality
- date: 2026-10-04 01:1x local
- mode: debug (user field report: Apply Pattern button refuses every click)
- context pack: field log `~/.patternskin/logs/patternskin.log` (full history), remediation_manifest rows PS-BUSY-* + EV-066, colibri reviews dbb85879/bf2f04df/1056a4ed/b9a15622/efdea574/5f4f0473, FREEZE_AND_LAUNCH_PLAN docket [7], live probe runs on Blender 5.1.2 (junk/ps_modal_probe*.py, junk/ps_probe*_stdout.log)

## Verdict

User-reported blocker reproduced and root-caused: **Blender 5.1 removed `Event.timer`, and
`_PSCancellableApply.modal()` dereferences `event.timer` on its first line.** Every TIMER
event now raises `AttributeError` inside `modal()`, the subdivision generator never advances,
the apply never completes, and the `_PS_APPLY_BUSY` guard is never released - so every later
Apply click on that object is refused with "'X' is already being processed by another Pattern
Skin apply - wait for it to finish (or press Esc on it) first."

## Failure chain (evidence)

1. Field log 2026-10-04: `PATTERNSKIN_OT_apply.invoke -> RUNNING_MODAL (0.08s)` at 01:00:46 -
   the FIRST interactive-modal apply in the entire log (all prior logged applies were
   scripted/headless synchronous `FINISHED` records). Followed by guard refusals at 01:00:53,
   01:01:08, 01:01:31, 01:02:02 (each `CANCELLED` in ~0.02s = invoke pre-flight + the guard raise).
2. Static trace: all claim/release paths in `_ps_start`/`modal`/`cancel`/`api_apply` are closed
   in the current bytes (all prior PS-BUSY findings verified fixed). The refusal is therefore a
   legitimately-held flag, not a leak - the modal itself is wedged.
3. Live reproduction (clean factory instance, Blender 5.1.2 / Python 3.13.9, probe
   `junk/ps_modal_probe.py`): `bpy.ops.patternskin.apply('INVOKE_DEFAULT')` returns
   `RUNNING_MODAL`; `_PS_APPLY_BUSY` stays 1 and mesh polygons stay 6 across 12 samples over
   ~5s - generator never advances once. Deterministic.
4. Smoking gun (Blender console captured in `junk/ps_probe_stdout.log`):
   ```
   File "...PatternSkin/__init__.py", line 534, in modal
       if event.type == "TIMER" and event.timer != self._ps_timer:
                                    ^^^^^^^^^^^
   AttributeError: 'Event' object has no attribute 'timer'
   bpy.rna | ERROR Python script error in PATTERNSKIN_OT_apply.modal
   ```
5. Attribute inventory (probe v2, 5 TIMER events): TIMER events in 5.1.2 expose **no
   timer-related attribute at all** (`dir(event)` timer attrs = []). The P3-5 foreign-timer
   identity check is no longer implementable via the event.
6. Blender does NOT call `cancel()` when a modal handler raises (busy stayed 1 through the
   whole probe) - the flag stays held with no automatic release. The ESC branch of `modal()`
   does NOT touch `event.timer`, so Esc still releases (labeled PLAUSIBLE-high: not separately
   live-verified, but traced against current bytes).

## Why it surfaced now

The interactive modal branch has never been exercised in the field log era (Aug 27 onward):
every logged apply was the synchronous/scripted path. The user's interactive Blender is
5.1.2 (Python 3.13), and 2026-10-04 01:00:46 was the first interactive modal apply since the
5.1 upgrade. Headless batteries (bpy 5.0.1) take the `bpy.app.background` sync branch and
cannot see this. Docket [18]'s lesson ("requires live Blender testing") applies to the whole
modal branch.

## Hypothesis ledger

- H-A timer-equality broken on 5.1 (RNA semantics) - KILLED by probe v2: `.timer` does not
  exist at all (AttributeError, not merely unequal).
- H-B TIMER events not delivered - KILLED: events ARE delivered (probe v2 recorded 5 TIMER
  events; the addon's modal raised on each).
- H-C generator hangs on first next() - KILLED: the exception happens before `next()` is
  ever reached (line 534 is the modal prologue).
- CONFIRMED: 5.1 API removal of `Event.timer` + unguarded prologue dereference.

## Fix design (recommendation - NOT implemented; fix tranche pending owner order)

Minimal, compatibility-preserving one-line shape:

```python
_t = getattr(event, "timer", None)      # removed in Blender 5.1
if event.type == "TIMER" and t is not None and t != self._ps_timer:
    return {"PASS_THROUGH"}
```

On <=5.0 the P3-5 foreign-timer semantics are preserved exactly; on 5.1 the op consumes TIMER
events while it owns undrained work (`self._ps_gen is not None`) and passes them through
otherwise. Overlapping PS modals each advance only their own generator - the cost of consuming
a foreign timer is at most a faster tick, never a wrong result.

Sibling hardening (same tranche, per G41): wrap the `modal()` prologue so ANY exception stops
the timer, releases `_PS_APPLY_BUSY` and reports instead of wedging - Blender's no-cancel-on-
error behavior makes every future modal-prologue raise a permanent session lockout.

Test-first: a GUI-probe RED test (windowed bpy run: INVOKE_DEFAULT apply on a default cube,
sample `_PS_APPLY_BUSY`/polygons for ~2s, assert completion) - headless coverage cannot reach
this branch (background mode takes the sync fallback).

## User recovery (immediate, no code change)

Press **Esc** with the mouse over the 3D viewport (the ESC path releases the flag and reports
"Apply cancelled - mesh unchanged"; the subdivision never started so the mesh is untouched),
or restart Blender (the busy set is per-process module state).

## Missing safeguards

- No test anywhere drives the interactive modal branch (headless batteries structurally
  cannot); the branch's only coverage was reading the source. A windowed-GUI probe harness
  (like junk/ps_modal_probe.py) is the missing T1.
- `apply_live.execute -> CANCELLED` appears ~40 times across Sep 25 - Oct 02 field logs
  (0.01-0.21s) with only three FINISHED - a separate latent failure worth its own debug pass
  when the owner next touches Live mode.


## Fix landed (same session, owner order 2026-10-04 "yes do the recommended")

All 11 sibling prologues (not just the mixin - the sweep found install_accel,
install_ml_worker, cu, generate_default_library, self_update, ai_parts, sel_text,
ai_parts_semantic, ai_parts_native and ai_load_scan carrying the identical
`event.timer != self._timer` prologue) converted to the getattr alias; the mixin
additionally got the prologue containment (T2). RED-first battery
tests/test_hunt_evtimer.py; stale P3-5/P5-C7 scrape probes retargeted to the new
contract; full suite 37/37; live GUI probe PASS on Blender 5.1.2 (393,216 faces,
guard released ~3.4s). Remediation manifest row appended in the fix commit.
Adjudicated residual: on 5.1 there is no timer-identity signal, so overlapping PS
modals cross-consume TIMER ticks (try-contained poll/redraw ticks - the 84b4937e
rate-limit class, no crash path).
