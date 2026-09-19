<!-- source: comfy/caliper_vram.py | reviewer: zcode-glm-5.3 | sha256: 4efa3fb3e9e0a3df65d2eded909fbba98d6c7fd9c7ff676cbdb2891810164a68 | date: 2026-09-15 | mode: bug -->
<!-- context: post adversarial-gate remediation (KV clamp 32k, all download paths verify, batched WMI). Evidence: tsc 0, vitest 508/508, tier 77/0/7, live node 1.2.1. -->

## Verdict
Shippable - node 1.2.1, synced, live-verified with the batched query.

## Fixed since last review (this delta, per the adversarial gate)
- **[LOW|FIXED] the per-process WMI round-trip** is now ONE batched Get-CimInstance for every GPU pid (filter ProcessId=a OR ProcessId=b ...), joined to the counter rows by hashtable - the read stays flat on slow-WMI boxes. Live: 39 of 47 processes carry cmdlines (the silent 8 are system processes like dwm - honest nulls).

## Bugs & vulnerabilities (delta)
- None.
