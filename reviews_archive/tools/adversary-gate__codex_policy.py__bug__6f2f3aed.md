# Full workspace enforcement review
Source: C:\Users\User\source\repos\Tools\adversary-gate\codex_policy.py
Reviewer: gpt-6-astra plus Tools independent adversary gate
SHA256: 6f2f3aeddb5d6b23e513cf84eb37a49693ec9625cb97b6c5191157bd23570ec2
Date: 2026-09-27
Mode: bug
Context: owner requires Tools and both Colibri repositories fully armed; canonical policy/guard/broker source, current Git arming checks, plugin commands, root/subdirectory regressions.

## Finding and remediation
CONFIRMED: in_scope exempted the physical Tools checkout, allowing direct patch/shell through legacy guard routing. Removed that exemption; trusted cwd validation still runs and every workspace uses the existing broker-only policy. MAINTENANCE_ROOT remains an identity compatibility constant, not an exemption. Broker schemas, path checks and z.ai implementation are unchanged.

## Adversarial verification
Independent exact-byte packet CLEAR: .adversary/write-reviews/tools-full-scope-b0a03c0fbb60492095c90745d14f47bd.json. Production/test pairing reviewed together after test-only proposal was BLOCKed. Current standard suite passes134 tests (two skips); guard selftest31/31. Installed PowerShell command matrix passes12/12 across Tools, colibri-marketplace and colibri-code-review: direct patch denied, direct shell denied, valid broker status allowed, forged broker workspace denied. Fresh MCP connections for all three select correct workspace, allow status, and reject an unprepared write.

## Limit
These are installed-command and fresh-process results. Changed global plugin hooks still require user trust through /hooks before claiming native host interception. No fabricated trust, disabled hooks, or unreviewed code writes.
