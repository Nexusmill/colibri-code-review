# Full workspace enforcement review
Source: C:\Users\User\source\repos\Tools\adversary-gate\codex_guard_selftest.py
Reviewer: gpt-6-astra plus Tools independent adversary gate
SHA256: 2e347cc8992c533d0f5f62f65fe9d1c3ba687641808ae24f9616e97b9b9104ab
Date: 2026-09-27
Mode: bug
Context: owner requires Tools and both Colibri repositories fully armed; canonical policy/guard/broker source, current Git arming checks, plugin commands, root/subdirectory regressions.

## Finding and remediation
Updated three historical Tools-only allowance expectations to match the owner-required strict policy. Added a positive broker-status case. Existing malformed input, infrastructure, front registry, and plugin path tests retained. Real subprocess selftest passes31/31.

## Adversarial verification
Independent exact-byte packet CLEAR: .adversary/write-reviews/tools-full-scope-b0a03c0fbb60492095c90745d14f47bd.json. Production/test pairing reviewed together after test-only proposal was BLOCKed. Current standard suite passes134 tests (two skips); guard selftest31/31. Installed PowerShell command matrix passes12/12 across Tools, colibri-marketplace and colibri-code-review: direct patch denied, direct shell denied, valid broker status allowed, forged broker workspace denied. Fresh MCP connections for all three select correct workspace, allow status, and reject an unprepared write.

## Limit
These are installed-command and fresh-process results. Changed global plugin hooks still require user trust through /hooks before claiming native host interception. No fabricated trust, disabled hooks, or unreviewed code writes.
