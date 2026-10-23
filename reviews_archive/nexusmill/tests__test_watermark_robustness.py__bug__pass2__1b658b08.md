# colibri bug review (pass2) — tests/test_watermark_robustness.py

- pass2 of the 2026-07-20 review (same sha 1b658b08 — the prior's 2 MEDIUMs + LOWs stand against these bytes and are NOT restated here)
- model: GLM-5.3-Flash (in-session) · reviewed_at: 2026-10-14 · mode: bug · live run: "Recovered tracer in 10/11 attacks", exit 0.

## New finding (not in the prior)

**[LOW] The attack grid has no red-able threshold — suite-green is vacuous** - `lines 76-86`
- Verbatim: `npass += ok` ... `print(f"Recovered tracer in {npass}/{len(attacks)} attacks.")` then `main()` — no assertion anywhere on npass; the file exits 0 whether 10/11 or 0/11 recover.
- What: as a `test_*.py` collected by the runner, its green only certifies "ran without crashing". The measured property (tracer robustness) never gates.
- Trigger: a tracer regression dropping recovery to 0/11 — the suite stays green; only a human reading the transcript notices.
- Producing caller: any edit to forge/tracer/png_stego.py embedding/extract.
- Broken behavior: none at runtime — the measurement is honest; the test-status is not.
- Fix: `expect = 9; sys.exit(0 if npass >= expect else 1)` with the threshold chosen from the current 10/11 baseline (or move the grid to a probe and keep a pinned minimum here).
- Status: **CONFIRMED** (no assert on npass; exit path traced).

## Verdict
new: 1 (LOW). Prior MEDIUMs (unclosed Image handles; hardcoded /tmp/wm) remain open against the same sha.
