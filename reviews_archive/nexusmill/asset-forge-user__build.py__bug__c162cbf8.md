# Colibri Review - bug (FULL re-audit) - asset-forge-user/build.py

- **Source path:** `asset-forge-user/build.py`
- **Reviewer:** claude-fable-5-1 (fork of the lead session), Colibri G37 protocol, campaign item 1 (Asset Forge tooling)
- **sha256 reviewed:** `c162cbf8b671d0734f82604d4878f6f3df1528aa2ed507cd6b930f8db70b96ac` (sha8 `c162cbf8`)
- **Date:** 2026-09-10 · **Mode:** bug, FULL review of the current bytes (owner ruling: pre-gate audits untrusted - no delta)
- **Context pack:** FULL read of the current bytes at e7be3d43 (owner ruling 2026-09-10: the file's pre-gate reviews are untrusted); jCodemunch get_file_outline + find_importers (none of the six is imported by product code - entry points/tools); tools/sync_builds.py WHITELIST (which of the six are shared twins); the remediation/deferred rows and the prior .colibri_reviews records for launcher/secrets/make_user_edition loaded as CLAIMS re-verified at the bytes; stdlib urllib proxy logic read from the buildenv's own source; the windowed-process stream state proven with pythonw.exe started without a console.

## Verdict
Same G17 doctrine defect as the creator build.py (covered by the one AF-BUILD-PINS docket row); the cross-OS packaging branches, --no-cache-dir and the freshness stamp read correctly. 0 fixed.

## Bugs & vulnerabilities

**[MEDIUM (doctrine G17)] DEPS unpinned >= ranges (same as asset-forge/build.py; one docket row covers both)** - `line 14`
- What: Identical DEPS list plus pywebview>=5.0 / pyobjc-framework-* off Windows.
- Trigger: Every build.
- Impact: See AF-BUILD-PINS.
- Fix: DOCKET AF-BUILD-PINS.
- Verification: CONFIRMED at the bytes.

## Missing safeguards / notes
- none

## Adversarial verification pass (refuted claims)
- system_site_packages=True off Windows lets host packages leak into the bundle -> refuted: deliberate: pywebview needs the system WebKit2GTK/pyobjc bindings there, and PyInstaller collects only what the app imports
