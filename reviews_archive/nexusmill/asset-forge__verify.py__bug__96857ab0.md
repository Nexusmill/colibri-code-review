# Colibri Review - bug (FULL re-audit) - asset-forge/verify.py

- **Source path:** `asset-forge/verify.py`
- **Reviewer:** claude-fable-5-1 (fork of the lead session), Colibri G37 protocol, campaign item 1 (Asset Forge tooling)
- **sha256 reviewed:** `96857ab0aac6c7ef5ea2c9071bc70edfea17cb3522ec7a3aa47c48b2b9b1cb84` (sha8 `96857ab0`) - the PRE-fix bytes
- **Date:** 2026-09-10 · **Mode:** bug, FULL review of the current bytes (owner ruling: pre-gate audits untrusted - no delta)
- **Context pack:** FULL read of the current bytes at e7be3d43 (owner ruling 2026-09-10: the file's pre-gate reviews are untrusted); jCodemunch get_file_outline + find_importers (none of the six is imported by product code - entry points/tools); tools/sync_builds.py WHITELIST (which of the six are shared twins); the remediation/deferred rows and the prior .colibri_reviews records for launcher/secrets/make_user_edition loaded as CLAIMS re-verified at the bytes; stdlib urllib proxy logic read from the buildenv's own source; the windowed-process stream state proven with pythonw.exe started without a console.

## Verdict
Creator-only CLI, correctly excluded from the user edition (not in KEEP, dropped from forge/, in the recursive nono scan). One LOW robustness defect in the manifest index.

## Bugs & vulnerabilities

**[LOW] _load_manifests dies on a manifest that parses but lacks set_id (KeyError) or is not an object (TypeError) - the whole verification run aborts before inspecting any file** - `line 35`
- What: Only json.load sits in the try; idx[m['set_id']] runs outside it.
- Trigger: A hand-edited, truncated-then-repaired or foreign *.manifest.json under ./output.
- Impact: The verifier exits with a traceback instead of a verdict on the suspect files - the tool exists for exactly the moment a creator needs an answer.
- Fix: Skip manifests that are not objects or carry no set_id. Battery VER_malformed_manifest_is_skipped RED (KeyError) -> GREEN.
- Verification: CONFIRMED by reproduction.

## Missing safeguards / notes
- glob only under ./output of the CWD - documented in the tool's own SOLD TO hint.

## Adversarial verification pass (refuted claims)
- verify.py could ship in the user edition -> refuted: not in KEEP, listed in DROP_IN_FORGE and in the recursive nono scan; confirmed absent from asset-forge-user
- extract_svg reads an unbounded file into memory -> refuted: a creator tool run on files the creator chose; no untrusted-input boundary

## Remediation postscript (same session)
The fixes were applied after this review hashed the bytes above; the file is now `428b36d1a08080b8a218e103c6f7c4bebaf95f9f691f263de912f12f4da6a27e`. Rows AF-VERIFY-MANIFEST-GUARD in `docs/remediation_manifest.json`, same commit.

