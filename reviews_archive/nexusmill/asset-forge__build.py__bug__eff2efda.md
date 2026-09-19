# Colibri Review - bug (FULL re-audit) - asset-forge/build.py

- **Source path:** `asset-forge/build.py`
- **Reviewer:** claude-fable-5-1 (fork of the lead session), Colibri G37 protocol, campaign item 1 (Asset Forge tooling)
- **sha256 reviewed:** `eff2efda4888def6ae2c50b872a591a595d74c7c13285f79fcc89acf088fd4d2` (sha8 `eff2efda`)
- **Date:** 2026-09-10 · **Mode:** bug, FULL review of the current bytes (owner ruling: pre-gate audits untrusted - no delta)
- **Context pack:** FULL read of the current bytes at e7be3d43 (owner ruling 2026-09-10: the file's pre-gate reviews are untrusted); jCodemunch get_file_outline + find_importers (none of the six is imported by product code - entry points/tools); tools/sync_builds.py WHITELIST (which of the six are shared twins); the remediation/deferred rows and the prior .colibri_reviews records for launcher/secrets/make_user_edition loaded as CLAIMS re-verified at the bytes; stdlib urllib proxy logic read from the buildenv's own source; the windowed-process stream state proven with pythonw.exe started without a console.

## Verdict
One confirmed doctrine defect (G17), to DOCKET beside SP-BUILD-PINS rather than blind-pin: the creator build resolves every dependency as a >= range from PyPI at build time. Otherwise a straightforward clean-venv build with the freshness stamp.

## Bugs & vulnerabilities

**[MEDIUM (doctrine G17)] DEPS are unpinned >= ranges installed fresh from PyPI at every build - no versions, no hashes** - `line 14`
- What: DEPS = ['flask>=3.0', 'pillow>=10.0', 'numpy>=1.24', 'scipy>=1.10', 'cryptography>=41', 'pyinstaller>=6.0'] -> pip install resolves the latest of each (and their transitive deps) into the fresh .buildenv.
- Trigger: Every build on a fresh venv.
- Impact: Non-reproducible binaries; an upstream breaking or compromised release ships straight into dist/. Same class as SP-BUILD-PINS.
- Fix: DOCKET (AF-BUILD-PINS): pin from the last known-good build's pip freeze, install from a requirements-lock, then --require-hashes. Not blind-pinned here (the owner left the sibling accelerator docket open today).
- Verification: CONFIRMED at the bytes.

## Missing safeguards / notes
- Creator build.py lacks --no-cache-dir and the non-Windows pywebview deps by design (Windows-only creator packaging, per the sync_builds whitelist).

## Adversarial verification pass (refuted claims)
- shutil.rmtree(dist) while the compiled app is running destroys the installed app -> refuted: a developer action on the developer's own box; ignore_errors=True and PyInstaller --clean then fail loudly, no stamp is written
- the freshness stamp can drift from the built bytes -> refuted: computed after the build from the same tree in the same run; only a concurrent edit could split them - dev-only
