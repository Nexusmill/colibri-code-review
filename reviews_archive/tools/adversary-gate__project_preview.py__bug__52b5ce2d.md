# Workspace preview Colibri review

Source: C:\Users\User\source\repos\Tools\adversary-gate\project_preview.py
Reviewer: Codex (in-session)
SHA-256: 52b5ce2d0717a869ee6ced577f92a3bc4729f082a2ae5695f402b2d45bf617bb
Date: 2026-09-19 13:38
Mode: bug
Context: user capability/lifecycle contract; canonical writer, loader, policy and hook adapter; current preview implementation and tests; exact-byte independent review evidence.

## Verdict
No remaining confirmed defect in this scoped change after the recorded repairs.

## Bugs & vulnerabilities
Replaced missing lifecycle authority with workspace-relative discovery, bounded snapshots, owned workers, content reuse, review-backed configuration and live URL proofs. Verified directory/link exclusions, exact current config approval and cleanup state transitions. Fixed non-object receipt crashes and retained failed-cleanup ownership. Same-user hostile state tampering is outside this tool-boundary model.

## Fixed since last review
The prior fixed-application policy and absent preview route are replaced for project workspaces. Earlier review findings are resolved only as described above; no claim of a broader broker/security audit.

## Adversarial verification
See adversary-gate/PREVIEW_ACCEPTANCE.md for executed commands, acceptance layers and limits. Independent pre-write evidence matching this exact hash: .adversary/write-reviews/8d9d308caa5d4ed29befb4b60499065a.json. Normal Git commit review is additional.
