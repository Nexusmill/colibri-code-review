# colibri bug review — tests/test_hunt_p5_fixes.py

- source: tests/test_hunt_p5_fixes.py
- model: GLM-5.3-Flash (in-session)
- sha256: 7a54765d8db3 (full sha in manifest row)
- reviewed_at: 2026-10-13 · mode: bug
- context pack: live execution under junk/venv-battery (PASS, 0 failures, exit 0); C7 3400-char window re-measured against current bytes (all five probes — edit_object, _eo.data == _o0.data, _eo == _o0, mode_set order, active reassign — in-window after the evtimer containment block); G41 contracts (junk/hunt_p5_contracts.md) referenced by the docstring.

## Verdict
Clean — no confirmed defects. G41 discipline visible in the file: RED-first failure-path row (D3-T2) with twin-home patching (`PS._save_gray_png` AND `apply_core._save_gray_png` both patched and restored in `finally`), selection-restore verified by count, and the autoload round-trips (A→B→A, A→camera→A) pin the `_PS_AUTOLOAD_LAST` advance semantics.

## Bugs & vulnerabilities
None CONFIRMED.

- C7's fixed 3400-char window from the first `def modal` verified to still cover the modal-gap guard body after the ~10-line evtimer containment insertion (measured 2026-10-13). Note for the future: the window is positional — the next prologue growth should re-measure it (the comment at lines 152-153 already says so; this review confirms it holds today).

## Missing safeguards
- `src` here is `__init__.py` only (no apply_core/common) — sufficient for its single C7 pin today (guard lives in `_PSCancellableApply.modal`, `__init__.py:531+`), same fragility class as p2/r8 if the modal ever moves.
