# colibri bug review — tests/test_hunt_p4_fixes.py

- source: tests/test_hunt_p4_fixes.py · model: GLM-5.3-Flash (in-session)
- sha256: daa14b1430 (full sha in manifest row) · reviewed_at: 2026-10-13 · mode: bug
- context pack: live execution (PASS, 0 failures, exit 0); `_rna(` count verified at exactly 9 in current __init__ (threshold `>= 9` — at-threshold, loud on any removal); P4-F1/F2/F3/F5 behavioral rows traced to their contract sources.

## Verdict
Clean — no findings. The F1 counting-thread probe (asserting the malformed-cache refusal spawns ZERO workers before claiming), the freed-RNA `_rna` pair (setup-raises-then-survives), and the WAIT-cursor finally pin are all model rows.

## Bugs & vulnerabilities
None CONFIRMED.

- The `threading.Thread` / `load_scan` / `_AI_RUN` monkeypatches (l.63-67) lack a try/finally, but the only raise-capable span between patch and restore (execute) is wrapped at l.69-73 — restoration always runs.

## Missing safeguards
- None.
