# Full workspace enforcement review
Source: C:\Users\User\source\repos\Tools\adversary-gate\test_codex_policy.py
Reviewer: gpt-6-astra plus Tools independent adversary gate
SHA256: 3533745dd6bbba6ff2214e395d206999726c8c0b97483835be971d980ed4665e
Date: 2026-09-27
Mode: bug
Context: owner requires Tools and both Colibri repositories fully armed; canonical policy/guard/broker source, current Git arming checks, plugin commands, root/subdirectory regressions.

## Finding and remediation
Replaced the exemption-allow expectation with direct-write/shell denial plus broker-status allowance at arbitrary roots, Tools root and nested adversary-gate. Added actual guard subprocess tests at Tools root and subdirectory. Executed candidate tests in memory against original production: four assertion failures, zero errors; revised production passes.

## Adversarial verification
Independent exact-byte packet CLEAR: .adversary/write-reviews/tools-full-scope-b0a03c0fbb60492095c90745d14f47bd.json. Production/test pairing reviewed together after test-only proposal was BLOCKed. Current standard suite passes134 tests (two skips); guard selftest31/31. Installed PowerShell command matrix passes12/12 across Tools, colibri-marketplace and colibri-code-review: direct patch denied, direct shell denied, valid broker status allowed, forged broker workspace denied. Fresh MCP connections for all three select correct workspace, allow status, and reject an unprepared write.

## Limit
These are installed-command and fresh-process results. Changed global plugin hooks still require user trust through /hooks before claiming native host interception. No fabricated trust, disabled hooks, or unreviewed code writes.
