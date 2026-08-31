Unit: tools/pin_py312.py, tools/promote_captured_pins.py, tests/gpu/run_bootstrap_tests.py,
tests/test_projection_degeneracy.py, tests/test_projections.py
Reviewer: claude-sonnet-5 (in-session)
Date: 2026-07-27
Mode: bug
shas: tools/pin_py312.py 59cb53ab84d05e730f77ebfc887507532a71a6d7a7ed04db3faff5a4231ac820;
tools/promote_captured_pins.py 1ef8a742d9c5c1ab55b7e327c2af104e6b27d19fb0177fb614553e1e270148c7;
tests/gpu/run_bootstrap_tests.py b5082bde496469a7b2d21f8c04b358fb6e97b71df0583ec49d615c7bd91cb2c0;
tests/test_projection_degeneracy.py a6bfbaf68c194c14bfef173856ef53f5ec477f48dff807e6546b8f1b81e7ae98;
tests/test_projections.py 7f3af91456783b50181bc723a4c70e04ebb400aa78e0ef271fc1802cf5b29b16

Grouped into one unit: all five are dev-only tooling/tests, not shipped runtime code, so a
lighter single pass covers them; each was still read in full before judging.

## Verdict
Shippable as dev tooling. No bugs found. Confirmed, via grep, that the existing test suite does
NOT exercise the three accel_bootstrap.py findings (lock heartbeat, ensure_python312 locking,
ensure_python312 cancellation) - which is *why* they survived, not evidence they're fine.

## Bugs & vulnerabilities
None found in tools/pin_py312.py or tools/promote_captured_pins.py.

## Missing safeguards
- `promote_captured_pins.py` never flags capture entries that exist in `captured_pins.json` for
  an artifact name no longer present in the manifest's `artifacts` list (e.g. after a rename) -
  it only reports the reverse (manifest artifact with no captured hash). Purely a dev workflow
  tool with human review of the printed diff before `--write`; LOW, not worth a manifest entry.
- Both tools write the manifest via plain `open(path, "w", encoding="utf-8")` with no
  `newline=""`; CRLF preservation relies on Windows' default text-mode translation. Fine on the
  only machine these run on today; would silently flip to LF if ever run on Linux/Mac. LOW.

## Test-validity spot check
- `tests/gpu/run_bootstrap_tests.py` line 73-77 tests that a lock past `stale_after` IS reclaimed
  (a real, correct feature test) but has no case for "still-active, still past stale_after" -
  consistent with the accel_bootstrap.py review's HIGH finding being a genuine gap, not something
  already caught and silently working.
- `tests/test_projections.py`'s "AUTO ball -> BALL" rename (8-line diff) is a straight
  find-and-replace of the assertion plus an explanatory comment; re-ran the logic by hand against
  `_resolve_auto_mode` and it matches BALL's actual dispatch.
- `tests/test_projection_degeneracy.py`'s sphere/pole fixtures were exercised live in this
  session (per docs/AGENT_STATE.md) and match the numbers cited in the BALL commit message;
  no new issue found on a fresh read.
