# Colibri review — src/jcodemunch_mcp/stdio_guard.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\stdio_guard.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summary, artifacts reaudit/jcm/)
- sha256: `e41d0b36240dde7aad5834b9ed7ec147f54226c5dbcb6624422ea4c18e377c66` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: the sub-agent's summary (1 CONFIRMED with a RED probe built on fake streams over real non-std descriptors, 2 refuted); the whole 92-line module - the docstring's transport contract ("afterwards fd 1 *is* stderr for the whole process") and its fail-OPEN promise ("returns (None, False) and changes nothing"), `claim_stdout` 40-91: dup (66), dup2 stderr→stdout (71), TextIOWrapper over the duplicate (79-83) with the failure branch at 84-89; callers: `find_references(claim_stdout)` = **tests only** (`tests/test_stdio_guard.py`, 8 subprocess tests) - nothing under src/ calls it (see the observation below). No prior `.colibri_reviews` record.

## Verdict
The one failure branch that ran after fd 1 had already been moved reported "changes nothing" - the exact lie the docstring promises never to tell. Fixed: the original stdout is put back before giving up, and an unrecoverable state is reported as what it is.

## Bugs & vulnerabilities
**[HIGH] `(None, False)` after `os.dup2` had already pointed fd 1 at stderr — CONFIRMED — FIXED** - `line 84-89`
- What: the swap is three steps; a `TextIOWrapper` failure at the third returned the documented "nothing changed" answer with fd 1 already redirected. A transport reading `swapped=False` keeps writing framed JSON-RPC to `sys.stdout`; every byte lands on stderr and the client waits forever - the module's own docstring names a paying customer who waited 5 h for exactly that symptom from the other half of the problem. Trigger (audit probe, RED on these bytes): fake stdout/stderr on real descriptors, `TextIOWrapper` forced to raise → `(None, False)` and a byte written to the "stdout" fd lands in the stderr file.
- Fix: the failure branch first `os.dup2(private_fd, stdout_fd)` to restore the original, then closes the duplicate and returns `(None, False)` - now true of fd 1, not only of the tuple. If the restore itself fails, the duplicate is closed and the answer is `(None, True)`: fd 1 IS stderr, there is no working stdout, and the caller is told. The docstring states both.

## Observation (PLAUSIBLE, for the owner - not fixed here)
- `claim_stdout` has **no production caller**: `find_references` lists only `tests/test_stdio_guard.py`, and `search_text` finds the name nowhere under src/ except its definition. The module's "structural guarantee" for the JSON-RPC stream is therefore not in effect in the running server - `run_stdio_server` never claims stdout. Whether the wiring was dropped or never landed is a product question (the module cites suite parity with jdocmunch-mcp 1.129.0); wiring it into the transport is a behaviour change outside this fix.

## Refuted (recorded so they are not re-raised)
- The sub-agent's two refuted claims were re-traced against these bytes and stand (its record lists them; neither concerns the failure branch).

## Adversarial verification (Phase 3)
- Pinned with the probe's technique - fake `sys.stdout`/`sys.stderr` on real non-std descriptors, installed INSIDE each test body because pytest's capture re-binds the streams at the start of the call phase and would undo a fixture-time patch (the first draft did exactly that and operated on pytest's own capture descriptors; consistent now with and without `-p no:capture`). A wrapper failure → `(None, False)` AND a byte written to the stdout fd lands in the stdout file; a wrapper failure whose restore also fails (only the restore `dup2` is made to raise - the swap `dup2` is let through) → `(None, True)` AND the byte lands in the stderr file.
- Control: the happy path swaps, hands back the original as a private stream, and later chatter on fd 1 lands on stderr.
- `tests/test_stdio_guard.py` (8 real-subprocess tests) unchanged and green with the battery.

## Remediation postscript (same commit)
The fix was applied after this review hashed the bytes above; the file is now `acebf36cd857051fc53187748e117f6a3cc15b1cd40115dc2fc12aed60a381fe`. TDD: `tests/test_stdio_guard_reaudit.py` (3 tests) - 2 RED on the old bytes, 1 control green throughout, GREEN after. The audit probe passes 2/2 after.
