# AGENT_ERROR_RATES — error-introduction per authoring agent (v3, machine-wide)

**ERROR INTRODUCTION RATE = the percentage chance (0-100%) that a COMMIT introduces at least one error**: the share of an agent's commits whose adversarial review's INITIAL DENIAL (first BLOCK) carried at least one finding. A commit denied five times before clearing counts once. **VALIDATION STATUS: these are gate-review findings counted at the denial, NOT outcome-validated errors** — in this workflow every BLOCK finding is adjudicated (remediated as real, or factually rebutted with byte evidence and re-verified by the reviewer), but this ledger does not yet join each finding to its outcome, so the percentage is an UPPER BOUND on the true error-introduction chance; observed gate false-positive rates are low (single digits), so the validated rate sits a few points under the stated figure. Findings are severity-blind (HIGH/MEDIUM/LOW each count).

> INITIAL DENIALS ONLY, machine-wide: every repo with `.adversary/reviews` under the swept roots, denials recovered from on-disk BLOCK artifacts (notary notes keep only the final CLEAR of a multi-round episode). Attribution = git AUTHOR (repos driven via `_git_do.py` commit under the owner's identity — identity-blurred). The JSON also carries findings per counted commit (`rate`); the MD shows the percentage form.

| agent | commits (counted) | commits w/ errors | % chance error per commit | findings | findings/error-commit | repos |
|---|---|---|---|---|---|---|
| phantom-man | 615 | 260 | **42.3%** | 538 | 2.07 | 3DPrinting, Blink, Caliper, OpenAIAstra, Tools, attic, cheyenne-layers, colibri-code-review, colibri-marketplace, deepagents-quickstarts, fleet, gods-eye-view, jcodemunch-mcp, psk-glm-review, repo-memory, spector-glm-review |
| Damien Fitzgerald Osborn | 100 | 22 | **22.0%** | 52 | 2.36 | Nexusmill |

**MACHINE-WIDE: 39.4% of commits introduce at least one error** (282 of 715 counted commits).

## Sub-programs (gate episodes with a denial program match)

| agent | program | episodes | findings |
|---|---|---|---|
| Damien Fitzgerald Osborn | (root/tooling) | 18 | 47 |
| Damien Fitzgerald Osborn | PatternSkin | 3 | 4 |
| Damien Fitzgerald Osborn | asset-forge-user | 1 | 1 |

Totals: 715 episodes (715 counted, 590 findings) across 17 gate repos; 978 archive on-demand scans excluded; 0 commits unresolved; 5 UNLANDED denials (BLOCK with no subsequent commit - itemized in the JSON); 3 enumeration anomalies.
