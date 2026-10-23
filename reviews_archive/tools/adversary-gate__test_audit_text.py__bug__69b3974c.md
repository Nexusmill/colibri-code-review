# Current-byte bug review

Source: C:\Users\User\source\repos\Tools\adversary-gate\test_audit_text.py
Reviewer: Codex in-session
SHA256: 69b3974c697ebacfd2d447f22b07d36620f626247fb5d42ea10e0c1fafdab2e1
Date: 2026-10-03 08:36
Mode: bug
Context: fresh source bytes, refreshed symbol/call-site index, global guard, owner commit-time clarification and selected source/installation separation, integration regressions and remediation documentation.

## Verdict
No confirmed findings under the owner's revised commit-time contract. Independent exact-staged-byte review is required at the closing commit.

## Bugs & vulnerabilities
None confirmed after a separate trigger-path verification pass.

## Missing safeguards
No additional safeguard required for this change. This hook is not an OS filesystem sandbox.

## Fixed since last review
The prior per-edit denial contract is superseded by the owner's explicit 2026-10-01 clarification. A disposable Git plumbing fixture verifies the auditor rejects an unnotarized text-only commit and a stale digest, then accepts matching exact committed bytes. Red verification in a separate interpreter removes only the in-memory txt rule and reproduces the original skip. Production hooks, notes and configuration are untouched; full suite passed 180 tests with 2 skips.
