# Emberline bug closure: emberline-diagnostics.cjs

Source: C:/Users/User/source/repos/OpenAIAstra/tools/emberline-diagnostics.cjs
Reviewer: GPT-6 Codex /root, in-session Colibri review
SHA-256: 97c3fb58fce8867fbca7dd518204b47dc9beaa9c34d65de399a7ef29db2aa28d
Date: 2026-09-17 12:48 America/Denver
Mode: bug
Context pack: native current source/dependency reads, indexed outlines, next-ten synthesis and remediation/feature ledgers; source release 054e456d577c and this continuation.
Prior review: .colibri_reviews/tools__emberline-diagnostics.cjs__bug__3d17d343.md

## Verdict
The linked-output correction is verified through the real CLI regression. Native exact-byte CLEAR cc683c1aac14441a88897739a8fcc278 applied these bytes. The helper remains a bounded local diagnostic tool, not an OS isolation boundary.

## Fixed since last review
Prior review 3d17d343 left CLI and link cases untested. CLI generation/readback now runs through the approved Node bridge; the UI uses routeReport for all 150 cases. A new hard-link regression failed first (exit 0 instead of 1), then passed after outputPath stopped gating lstat with existsSync and rejected nlink other than one (lines 151–153). Dangling links are visible to lstat and rejected. The combined test conditionally omits the dangling-link branch on EPERM/ENOTSUP; the aggregate bridge output does not establish which branch ran.

## Bugs & vulnerabilities
No unresolved confirmed defect in this delta. Before the fix, a replay destination hard-linked to another file would overwrite that file. The real work-only reproduction establishes the trigger. Current validation rejects it before writeJSON writes bytes.

## Missing safeguards
Preexisting-link validation is not race-proof confinement against another process replacing paths concurrently. JSON output is capped at two MiB; dedicated oversized-input rejection was not added. Recorded source hashes are provenance, not cross-version replay compatibility enforcement. Route clearance is geometric rather than inertial or enemy-pressure acceptance.

## Adversarial verification
Traced main → writeJSON/outputPath and check-trace; ordinary existing regular outputs still work. Read lstat errors narrowly: only ENOENT means absent. Existing terrain exports and shield contracts are unchanged. Final check after source changes: 37 repository tests, five skipped, exit 0, unchanged tree; all nine Node suites passed.

## Verification boundary
Source was read back through the native exact-byte reader. The current source-check run passed (37 repository tests, five skips, exit 0, unchanged tree). Documentation clearance is separate from source clearance. Final post-record checks and the automatic explicit-path Git gate remain required. Cross-file closure: .colibri_reviews/2026-09-17-emberline-next-ten-closure.md.
