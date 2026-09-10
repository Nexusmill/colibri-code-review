<!-- colibri review
source: vite.library.ts
reviewer: glm-5.3 (ZCode session, colibri v0.2.0 protocol)
sha256: d378317d339f7ed6272afc63e5c38ea149a23343ea1893cb9e68c3f4662129f8
date: 2026-09-06
mode: bug
context: E-5 wave (library recycle delete, export manifest, 4GiB guard, outputs lens, show-in-library); live through the app incl. the raw-zip manifest check
-->

## Verdict
Shippable. Delete recycles (access-check first: missing = idempotent silence; recycle failure speaks and the file stays; the record still dies with the attempt - same shape as before, now with recoverable files and spoken failures). The manifest join matches request descriptors to provenance records by filename+subfolder+type; the dedup-suffix reversal in the entry-name match is best-effort and an unmatched entry says "no provenance record" honestly.

## Bugs & vulnerabilities
(none confirmed)

- CORRECTED (gate round 1, 2026-09-06): my pass-3 "best-effort" note was WRONG - a collision-renamed entry reverse-matches the ORIGINAL descriptor (still in files, earlier in the array) and silently attributes the OTHER artifact's provenance. The join is now made by pairing at build time (entrySources array, no name recovery at all).

## Postscript (adversary round 1 remediation, same session)
(1) MEDIUM FIXED at the root: entries pair with their source descriptors
at build time - collision renames can never steal another artifact's
provenance. (2) LOW FIXED: only fs.access failure is idempotent silence;
EVERY recycle failure (exit code or spawn-level) speaks its message and
the file stays. (3) Cosmetic FIXED: the manifest's totals describe the
artifacts (count and bytes of manifestFiles), not a self-referencing
zip-entry count. Re-verified live: export-manifest and library-delete
PASS through the app. Bytes advanced to b72699f3.
