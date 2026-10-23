# Colibri broker support review

Source: C:\Users\User\source\repos\Tools\adversary-gate\codex_policy.py
Reviewer: Codex (in-session)
SHA-256: 7ff5eb659f061981f8f9dc181485950b978876efac0d25637ddfba7ee6fe6b7a
Date: 2026-09-16 05:56
Mode: bug/debug
Context: Tools manifest and history a55ffa5; AST symbol map; current loader, broker, writer, policy, safe_write and their tests; installed Colibri instructions. No prior report for this unit.

## Verdict
The broker allowlist adds exactly read_file. Existing shell and direct-write denials remain in place.

## Bugs & vulnerabilities
Fixed: no allowed native read/hash capability existed. The exact-name comprehension now admits mcp__astra_enforcement__read_file without a prefix wildcard.

## Missing safeguards
None added to mutation routes: reviewed_write remains the only supported generic write API; arbitrary write_file is still denied.

## Adversarial verification
The new policy test failed before the addition. Final unit tests allow the intended name and deny lookalikes, shell and patch operations. Actual codex_guard subprocess probes with protected OpenAIAstra cwd returned 0 for the new read name and 2 for Bash Get-FileHash and apply_patch. No hook definitions or shell access changed.

## Independent exact-byte review
CLEAR: .adversary/write-reviews/e830d0cbf0744defa85ba0f884565bb3.json.
