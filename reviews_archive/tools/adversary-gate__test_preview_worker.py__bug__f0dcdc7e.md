# Workspace preview Colibri review

Source: C:\Users\User\source\repos\Tools\adversary-gate\test_preview_worker.py
Reviewer: Codex (in-session)
SHA-256: f0dcdc7e43c50fb6e2ed4aa67575be0e82a398d19fd075e9645d97228f444913
Date: 2026-09-19 13:38
Mode: bug
Context: user capability/lifecycle contract; canonical writer, loader, policy and hook adapter; current preview implementation and tests; exact-byte independent review evidence.

## Verdict
No remaining confirmed defect in this scoped change after the recorded repairs.

## Bugs & vulnerabilities
Boundary spy checks actual subprocess argv/env while hostile Docker variables are present. Pins remote/old engine refusal, no mounts/privileges, label cleanup, absence handling and cleanup-only retry. Actual broker termination verifies worker socket closure. Docker mocks verify construction, not actual daemon behavior.

## Fixed since last review
The prior fixed-application policy and absent preview route are replaced for project workspaces. Earlier review findings are resolved only as described above; no claim of a broader broker/security audit.

## Adversarial verification
See adversary-gate/PREVIEW_ACCEPTANCE.md for executed commands, acceptance layers and limits. Independent pre-write evidence matching this exact hash: .adversary/write-reviews/c978c267786342449299c2ef70d771b3.json. Normal Git commit review is additional.
