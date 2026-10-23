# colibri bug review — tests/_runtests.py

- source: tests/_runtests.py
- model: GLM-5.3-Flash (in-session, account:zai-individual-coding-plan/GLM-5.3-Flash)
- sha256: 335be5bcd8a7 (full sha in manifest row)
- reviewed_at: 2026-10-13 · mode: bug
- context pack: G35 open row "tests/_runtests.py … ended exit 0 on any child failure", current bytes read in full (31 lines), static sweep of all 38 tests/test_*.py exit paths.

## Verdict
Healthy — the historic could-never-go-red runner is fixed in current bytes; residual risk is small and structural (exit-code-only trust).

## Bugs & vulnerabilities

**[verified-stale] G35 open row "aggregated nothing and ended exit 0 on any child failure"** - `lines 14-31`
- The row targets the pre-2026-09-19 hard-coded three-file runner. Current bytes: `worst = 1` on ANY non-zero child exit including negative signal codes (lines 23-24, comment at 23), per-file PASS/FAIL lines (25), full transcript (26-29), and `sys.exit(1 if worst else 0)` (31). **Verified against current bytes — fixed; never re-fix.**

**[LOW, hardening note] Verdict = exit codes only** - `line 25`
- A battery that prints FAIL rows but exits 0 would show PASS. Static sweep of tests/test_*.py found NO live offender: every current file either exits on its failure count (e.g. test_hunt_evtimer.py:165, test_accel_tiers.py:195) or fails via bare `assert` (exception → non-zero exit; confirmed for test_ai_select.py:60-61). Recorded per the producing-caller rule: no trigger exists today; a print-FAIL-exit-0 pattern introduced tomorrow would be invisible to this runner.

**[LOW] Skipped files are silent** - `line 10-12`
- SKIP'd files (test_blender_smoke.py) produce no output line at all — a reader of the transcript cannot distinguish "skipped: needs Blender" from "vanished". One printed line closes it.

## Missing safeguards
- No per-file timeout telemetry (a file at its 1800s cap is indistinguishable from a fast pass in the summary line; only the transcript body shows TIMEOUT).
