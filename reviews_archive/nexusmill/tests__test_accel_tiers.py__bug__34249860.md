# colibri bug review — tests/test_accel_tiers.py

- source: tests/test_accel_tiers.py · model: GLM-5.3-Flash (in-session)
- sha256: 3424986055 (full sha in manifest row) · reviewed_at: 2026-10-13 · mode: bug
- context pack: live execution (ALL PASSED, exit 0); the G35 row's three sub-parts re-verified against current bytes (label ASCII l.51; cKDTree spy + _SCIPY_OK flag l.91-115; gpu-mock save/restore+finally l.132-148); the async-wait bound (60s) read with its flake-history comment.

## Verdict
Clean — no defects. Section 5's spy-proof design (assert the tier RAN, not merely that it agreed) and section 7's bounded async wait with documented flake history are the file's best rows.

## Bugs & vulnerabilities
None CONFIRMED.

## G35 closure
The open row "(line 51 label; section 5; section 7 gpu mock)" is now verified-stale IN FULL: sub-part (1) ASCII label with scar comment (l.51); sub-part (2) the GROK-AC3 overlay addressed — `accel._SCIPY_OK = True` set alongside force (l.102) AND the `_SpyKD` cKDTree spy proving the tier engaged (l.97-100, checked l.112), flag restored (l.110); sub-part (3) the gpu mock has save/restore + finally (l.132-148, the K3 2026-07-20 finding's fix). Exit-on-_F at l.194-195.

## Missing safeguards
- The pytorch/scipy rows degrade to printed skips when absent (dormant on this machine — the venv carries both).
