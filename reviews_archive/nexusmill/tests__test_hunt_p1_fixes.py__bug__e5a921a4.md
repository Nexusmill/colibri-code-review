# colibri bug review — tests/test_hunt_p1_fixes.py

- source: tests/test_hunt_p1_fixes.py · model: GLM-5.3-Flash (in-session)
- sha256: e5a921a47b (full sha in manifest row) · reviewed_at: 2026-10-13 · mode: bug
- context pack: live execution (PASS, 0 failures, exit 0); pin provenance verified (F2/F6 strings present in current __init__); F5 late-binding ordering traced; the DS-1/DS-2 sentinel-data rows read against _live_build semantics.

## Verdict
Shippable — strong behavioral battery (edit/object-mode identity, atomic 3MF write, autofit ratio, foreign PS_Live survival with stale-weight zeroing across two runs). No defects.

## Bugs & vulnerabilities
None CONFIRMED.

- F5's `reps = []` after the lambda that references it (l.118-119) verified safe by late binding (execute called at l.120, after the binding).
- F1's te=0 arm correctly sidesteps the pre-existing all-valley sampling artifact via the edit-start==object-start identity contract.

## Missing safeguards
- `line 105`: dead expression `out = PS._apply_prepare(None, ...) if False else None` — the author's disable-marker idiom (same as p2:150-151); delete or comment.
