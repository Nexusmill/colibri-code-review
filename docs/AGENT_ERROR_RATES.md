# AGENT_ERROR_RATES — error-introduction per authoring agent (v3, machine-wide)

**ERROR INTRODUCTION RATE = the percentage chance (0-100%) that a COMMIT introduces at least one error**: the share of an agent's commits whose adversarial review's INITIAL DENIAL (first BLOCK) carried at least one finding. A commit denied five times before clearing counts once. **VALIDATION STATUS: these are gate-review findings counted at the denial, NOT outcome-validated errors** — in this workflow every BLOCK finding is adjudicated (remediated as real, or factually rebutted with byte evidence and re-verified by the reviewer), but this ledger does not yet join each finding to its outcome, so the percentage is an UPPER BOUND on the true error-introduction chance; observed gate false-positive rates are low (single digits), so the validated rate sits a few points under the stated figure. Findings are severity-blind (HIGH/MEDIUM/LOW each count).

> INITIAL DENIALS ONLY, machine-wide: every repo with `.adversary/reviews` under the swept roots, denials recovered from on-disk BLOCK artifacts (notary notes keep only the final CLEAR of a multi-round episode). Attribution = git AUTHOR (repos driven via `_git_do.py` commit under the owner's identity — identity-blurred). The JSON also carries findings per counted commit (`rate`); the MD shows the percentage form.

| agent | commits (counted) | commits w/ errors | % chance error per commit | findings | findings/error-commit | repos |
|---|---|---|---|---|---|---|
| phantom-man | 636 | 264 | **41.5%** | 548 | 2.08 | 3DPrinting, Blink, Caliper, OpenAIAstra, Tools, attic, cheyenne-layers, colibri-code-review, colibri-marketplace, deepagents-quickstarts, fleet, gods-eye-view, jcodemunch-mcp, psk-glm-review, repo-memory, spector-glm-review |
| Damien Fitzgerald Osborn | 107 | 25 | **23.4%** | 74 | 2.96 | Nexusmill |

**MACHINE-WIDE: 38.9% of commits introduce at least one error** (289 of 743 counted commits).

## VALIDATED true rate (adjudicated gate episodes only)

The percentage chance that a COMMIT introduces at least one VALIDATED error, 0-100% - measured over ADJUDICATED gate episodes only (gate-recorded outcomes: fixed / rebutted-upheld / cleared-unedited / rebuttal_rejected). Pre-recording gate history (729 episodes) is flagged unadjudicated and never mixed in; 0 archive-sourced episodes predate the recording entirely and sit outside this measurement.

**MACHINE-WIDE VALIDATED: 100.0% of adjudicated commits introduced at least one VALIDATED error** (14 of 14 adjudicated; FP share of adjudicated findings: 2.4%).

Per CALLING AGENT (the gate's caller field - the per-agent error rate; 'unknown' covers pre-attribution history):

| calling agent | episodes | adjudicated | validated | validated % |
|---|---|---|---|---|
| unknown | 742 | 13 | 13 | 100.0% |
| zcode | 1 | 1 | 1 | 100.0% |

## Sub-programs (gate episodes with a denial program match)

| agent | program | episodes | findings |
|---|---|---|---|
| Damien Fitzgerald Osborn | (root/tooling) | 21 | 69 |
| Damien Fitzgerald Osborn | PatternSkin | 3 | 4 |
| Damien Fitzgerald Osborn | asset-forge-user | 1 | 1 |

Totals: 743 episodes (743 counted, 622 findings) across 17 gate repos; 991 archive on-demand scans excluded; 0 commits unresolved; 8 UNLANDED denials (BLOCK with no subsequent commit - itemized in the JSON); 3 enumeration anomalies.
