# Current-byte bug review

Source: C:\Users\User\source\repos\Tools\adversary-gate\test_codex_policy.py
Reviewer: Codex in-session
SHA256: e1d0ba535cc610739ff4006ce48fc57dd5a5ee333cd3524d21ea0a71288fbc92
Date: 2026-10-01 17:44
Mode: bug
Context: fresh source bytes, refreshed symbol/call-site index, global guard, owner commit-time clarification and selected source/installation separation, integration regressions and remediation documentation.

## Verdict
No confirmed findings under the owner's revised commit-time contract. Independent exact-staged-byte review is required at the closing commit.

## Bugs & vulnerabilities
None confirmed after a separate trigger-path verification pass.

## Missing safeguards
No additional safeguard required for this change. This hook is not an OS filesystem sandbox.

## Fixed since last review
The prior per-edit denial contract is superseded by the owner's explicit 2026-10-01 clarification. Subprocess adapter regressions cover both origins and destinations, tool aliases, freeform payloads, data versus commands, malformed inputs, and unknown-command path smuggling. Temporary fixtures do not claim real Git gate acceptance.
