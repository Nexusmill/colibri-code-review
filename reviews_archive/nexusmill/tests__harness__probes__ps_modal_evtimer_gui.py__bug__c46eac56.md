# colibri bug review — tests/harness/probes/ps_modal_evtimer_gui.py

- source: tests/harness/probes/ps_modal_evtimer_gui.py
- model: GLM-5.3-Flash (in-session, account:zai-individual-coding-plan/GLM-5.3-Flash)
- sha256: c46eac56dfcd (full sha in manifest row)
- reviewed_at: 2026-10-13 · mode: bug
- context pack: PS-5.1-MODAL-EVTIMER debug record + AGENT_STATE (probe PASS live 2026-10-04), G35 manifest (no prior rows), current _PSCancellableApply.modal read from disk, blender_dev twin symlink note (AGENT_STATE 2026-10-02: same inodes via directory symlink), G23 twin-build doctrine.

## Verdict
Shippable as a machine-bound probe — failure paths are loud (setup exception → FAIL verdict, 20s watchdog, 20-sample window). Biggest risk: the probe's PASS artifact cannot attest WHICH PatternSkin bytes it exercised, which undermines its purpose as RED→GREEN proof.

## Bugs & vulnerabilities

**[MEDIUM] No provenance stamp — the PASS cannot attest which PatternSkin bytes ran** - `lines 26-27, 82-83`
- What: `bpy.ops.preferences.addon_enable(module="PatternSkin")` resolves the module through Blender's own scripts path, not the repo tree. RES records blender/python versions but neither `PS.__file__` nor any hash of the exercised source.
- Verbatim: `RES = {"blender": bpy.app.version_string, "python": sys.version.split()[0],` (line 26) — no source-identity key exists anywhere in RES.
- Trigger: a fix lands in the repo while the tree Blender actually loads (an installed copy or an unsynced twin) is stale → the probe PASSes on old bytes, or FAILs misleadingly after a partial sync.
- Producing caller: any repo-side fix landing before the twin/installed copy is synced (the G23 drift guard runs at release time, not at probe time).
- Impact: the probe's core deliverable — proof the fix works on the REAL Blender the user runs — is unverifiable after the fact from its own artifact; the 2026-10-04 PASS evidence cannot be tied to bytes.
- Fix: in setup_and_invoke, stamp `RES["patternskin_file"] = PS.__file__` and its sha256 immediately after `import PatternSkin as PS`.
- Status: **CONFIRMED** (trace; RES keys enumerated at lines 26-27, no identity field added anywhere).

**[LOW] Hard-coded absolute machine paths** - `lines 25, 73` (docstring line 15)
- What: OUT and the pattern PNG live under `C:\Users\User\source\repos\Nexusmill\junk\...`. The battery sibling derives REPO from `__file__` (tests/test_hunt_evtimer.py:19-20).
- Trigger: running the probe from any other checkout/machine.
- Impact: save/write failures or cross-machine confusion; the probe is committed harness code, not scratch.
- Fix: derive both paths from `os.path.dirname(os.path.abspath(__file__))` + a `junk/` relative like the battery does.
- Status: **CONFIRMED**.

## Missing safeguards
- None beyond the above: setup exceptions set verdict FAIL (lines 118-123), the watchdog forces a verdict at 20s (128-131, 140), and the sample window cannot hang (20 samples, line 109-110).
