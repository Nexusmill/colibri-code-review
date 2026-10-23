# Current-byte bug review

Source: C:\Users\User\source\repos\Tools\adversary-gate\project_preview.py
Reviewer: Codex in-session
SHA256: 3b650e958f3b9f22ed0090efe2761062b2ba6e07ceef39d40aa470ce68d6f918
Date: 2026-10-03 07:15
Mode: bug
Context: fresh source bytes, refreshed symbol/call-site index, global guard, owner commit-time clarification and selected source/installation separation, integration regressions and remediation documentation.

## Verdict
No confirmed findings under the owner's revised commit-time contract. Independent exact-staged-byte review is required at the closing commit.

## Bugs & vulnerabilities
None confirmed after a separate trigger-path verification pass.

## Missing safeguards
No additional safeguard required for this change. This hook is not an OS filesystem sandbox.

## Fixed since last review
The prior per-edit denial contract is superseded by the owner's explicit 2026-10-01 clarification. Installed preview children use the protected launcher preview entry, validating and capturing the active generation before worker execution. Source execution retains the owner-authorized source route. Real subprocess regression proves spec transmission and refuses a replaced worker before a marker payload executes; ownership, cleanup, Docker isolation and project snapshot behavior remain unchanged.
