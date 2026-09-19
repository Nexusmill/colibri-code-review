# Colibri Review - bug (FULL re-audit) - Spector/build.py

- **Source path:** `Spector/build.py`
- **Reviewer:** claude-fable-5-1 (in-session), Colibri G37 protocol, campaign item 1 (product cores), rank 56
- **sha256 reviewed:** `1c08f5fdb4dfb308afe3b1816dbfbc2ff84cdf16f7d0739f7f9bb2ebce064989` (sha8 `1c08f5fd`)
- **Date:** 2026-09-10 · **Mode:** bug, FULL review of the current bytes (owner ruling 2026-09-10: this file's prior audits predate the adversarial gate and cannot be trusted - no delta against them)
- **Context pack:** FULL read of the current bytes (owner ruling 2026-09-10: the file's reviews of 2026-07-19..08-15 predate the gate and are untrusted); jCodemunch `get_file_outline` + `find_importers`; the prior review records and the remediation/deferred rows for the file loaded as CLAIMS to re-verify, not as baseline; call sites traced with `get_symbol_source`.

## Verdict
One confirmed doctrine defect, DOCKETED not fixed (a blind pin could break the three-OS build; the honest fix needs the versions the green CI runs actually installed).

## Bugs & vulnerabilities

**[MEDIUM] The shipped binary pulls the LATEST of every dependency at build time (G17: ship pinned, never auto-pull latest)** - `build.py` `deps = ["pyinstaller", "flask", "numpy", ...]` + `pip install` with no versions; `requirements.txt` is unpinned too
- What: `.github/workflows/build-spector.yml` sets up Python 3.12 and runs `python spector/build.py` with no prior install, so `pip install pyinstaller flask numpy scipy robust_laplacian trimesh DracoPy faiss-cpu` resolves to whatever PyPI serves that day.
- Trigger: every CI build; every developer build on a fresh environment.
- Impact: non-reproducible customer binaries; an upstream breaking or compromised release ships straight into `dist/Spector` with no pin and no hash check (G17 requires pinned + hash-verified).
- Fix: DEFERRED as docket SP-BUILD-PINS - pin `requirements.txt` to the versions the last green build installed on each OS (read from the CI pip logs), make `build.py` install from it, then `--require-hashes`. Not done blind here: the exact versions with wheels for all three OSes are not knowable from this machine's buildenv alone.
- Verification: CONFIRMED (workflow lines 16-21 + build.py 12-15).
