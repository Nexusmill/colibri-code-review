# Colibri review — bug mode (test-surface audit + run synthesis)

- **Source:** `KokoroBookReader/tests/test_acceptance.py`
- **Reviewer:** GLM-5.3 (in-session, colibri-review v0.4.0 debug modality)
- **sha256:** 90d09c08ab682062606a766f458494bf8f842658bf9a68a5bf1dcb375185581b
- **Date:** 2026-09-26 21:14 · **Mode:** bug (test-surface audit, round-61 tests)
- **Context pack:** existing window-test pattern (setup_controller, qtbot, conftest
  settings isolation); KindleCandidate dataclass signature.

## Verdict
Sound. The test encodes the owner's exact scenario end-to-end at the window level.

## Audit
- Four candidates × four display outcomes: imported+sidecar-drift hidden (the
  reported bug), imported+book-file-changed SHOWN (the contract-v2 self-catch),
  legacy fingerprint-match hidden (back-compat), never-imported shown.
- `pending_kindle()` order assertion pins the shared predicate for the status count.
- Close order follows the existing passing pattern (window.close() then
  library.close()); no topLevelWidgets iteration; RED proven pre-implementation.

## Run synthesis (all five units)
One defect class across the diff (scan-side duplicate re-display) fixed at its root:
volatile-fingerprint hiding replaced by a durable origin→live-book mapping keyed on a
book-files fingerprint. Import-side (round 60) and scan-side (round 61) now share the
same identity discipline. Remaining known behavior (documented, not defects): the two
live stale folders re-show once after restart, then self-heal permanently on their
next import; a deleted book's folder re-appears as a genuine candidate by design.
