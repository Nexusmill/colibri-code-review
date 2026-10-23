# colibri review — tests/test_cards.py (first review, test-quality hunt)

- source: `tests/test_cards.py`
- reviewer: ZCode in-session (GLM-5.3), colibri-review v0.4.0, bug mode, test-specific classes
- sha256: 3a4ce20addece595db9b55126b26ff5476c3d564e0a25dcdf076d58455edfc9a
- date: 2026-10-05 04:45
- context pack: never reviewed (born c2ae400); contract source = cards.py (reviewed this session
  at c7cbe56f); six named gate-finding regression rounds documented in the class docstrings.

## Verdict

new: 1 (added after the suite run — see the CONFIRMED finding below). The test CONTENT itself is
what gate-finding regression discipline looks like — each adversary-gate BLOCK from the
2026-09-27 rounds lives on as a named test (days-0 rejection, skipped-card manifest rows, atomic
saves, corrupt-font replacement, undersized-save refusal, date.max planning, manifest healing,
lock exclusivity, index-only lock refusal).

## Bugs & vulnerabilities (new findings only)

**[MEDIUM — CONFIRMED] The module cannot import on a clean bootstrap: Pillow is used but never declared** - `birdcam/cards.py:42` (module-level `from PIL import Image, ...`) vs `requirements.txt` (no pillow entry)
- What: `python -m unittest discover -s tests` on this machine ends FAILED (errors=1): the loader
  cannot import tests/test_cards (ModuleNotFoundError: PIL). Verified: PIL absent from the venv
  AND from requirements.txt; the 2026-09-27 klein card run must have run with a transiently
  installed Pillow that no longer exists.
- Trigger: any fresh bootstrap (scripts/bootstrap.ps1 installs exactly requirements.txt), or the
  current venv right now.
- Impact: 471 lines of six-round gate-regression coverage contribute NOTHING to the suite (the
  loader error is one red row, easy to normalize away), and the standalone card generator cannot
  run. The live hourly pipeline is unaffected (nothing in birdcam imports cards — traced this
  session).
- Fix: add `pillow>=10` to requirements.txt (one line) — or make cards.py import PIL lazily with
  a fail-loud message if the standalone-tool dependency is meant to stay optional; declare it
  either way.

Test-quality hunt results:

- Assertions are real and adversarial: pixel-band differ/equal checks pin the overlay layout;
  `mock side_effect=AssertionError("network touched")` proves the cached-font short-circuit; the
  mid-save crash is simulated by class-swapping an ExplodingImage and asserting NO partial
  destination file survives; the undersized-save test asserts the OLD card bytes are untouched.
- The one empty test (`test_lock_is_exclusive_and_stale_takeover: pass`, 381-385) is explicitly
  documented as superseded by the OS-lock design (gate 093333) — honest bookkeeping, not a silent
  pass masquerading as coverage; its replacement (test_lock_exclusive_and_released_on_close)
  exists and asserts the real property.
- skipTests carry real reasons (no TTF, font not bootstrapped). No env leaks; temp dirs cleaned;
  no order coupling.

Prior findings not restated.
