# colibri bug review — tests/test_hunt_r1_fixes.py

- source: tests/test_hunt_r1_fixes.py · model: GLM-5.3-Flash (in-session)
- sha256: 03f796991b (full sha in manifest row) · reviewed_at: 2026-10-13 · mode: bug
- context pack: live execution (PASS, 0 failures, exit 0); the send_to_spector inbox flow + Spector's real inbox semantics; cleanup-path trace of F1/F2.

## Verdict
Shippable with one isolation defect: F1 writes into the user's REAL Spector inbox with no finally — a live-path write from a test.

## Bugs & vulnerabilities

**[MEDIUM] F1 writes a real STL into the live `~/.spector/inbox` with no try/finally around cleanup** - `lines 59-74`
- Verbatim: `inbox = os.path.join(os.path.expanduser("~"), ".spector", "inbox")` ... `res = bpy.ops.patternskin.send_to_spector()` ... `for f in new: try: os.remove(os.path.join(inbox, f))`
- What: send_to_spector hardcodes the real inbox; the battery writes a junk STL there and cleans it only on the happy path.
- Trigger: (a) any exception between the write and the cleanup loop strands the junk STL in the user's live inbox — which the running Spector app may consume as a real part; (b) a live Spector daemon moving the file between the `before`/`after` snapshots makes `new` empty → the row FAILS spuriously (false red, no product bug).
- Producing caller: Spector running on this machine (it is the owner's part library); any raise inside send_to_spector after the inbox write.
- Broken behavior: user-visible inbox pollution / flaky verdict.
- Fix: wrap in try/finally for the removal; ideally drive a sandboxed inbox (env-override or monkeypatched home) as F6 already does for expanduser.
- Status: **CONFIRMED** (path trace; happy-path-only cleanup verified by reading).

## Missing safeguards
- `line 36`: `import numpy as np` unused.
- `line 38`: the odd `importlib.reload(PS)` (unique to this battery) double-executes module init — works, but worth a comment or removal.
