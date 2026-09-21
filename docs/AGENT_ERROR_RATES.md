# AGENT_ERROR_RATES — error-introduction rate per authoring agent

> Commit-anchored adversarial reviews ONLY, TWO sources under reconciled semantics (owner orders 2026-09-21): (A) archive reviews whose sha line carries `= commit <sha>` — on disk, manifest-indexed or not; (B) GATE reviews recovered from each target repo's adversary notary notes. ONE row per (repo, commit) episode — the INITIAL denial, never the remediation rounds. On-demand bug hunts and scan-ladder passes are excluded. Attribution = git AUTHOR. `rate` divides by **counted** reviews; reviews with no parseable `new: N` are flagged and excluded from the denominator — they can deflate coverage, never a rate.

| agent | commit reviews | counted | new findings | reviews w/ findings | no count line | findings/counted | repos |
|---|---|---|---|---|---|---|---|
| phantom-man | 207 | 207 | 5 | 2 | 0 | 0.02 | blink, caliper, fleet, openaiastra |
| Damien Fitzgerald Osborn | 89 | 89 | 4 | 2 | 0 | 0.04 | nexusmill |

Totals: 296 commit-anchored episodes (296 counted), 981 on-demand scans excluded, 0 commits unresolved, 0 outputs missing/unreadable, 462 reviews RECOVERED from disk beyond the manifest index, 12 enumeration anomalies (all itemized in the JSON), 0 archive folders unmapped. Same-source archive ties break by filename order (deterministic residual).
