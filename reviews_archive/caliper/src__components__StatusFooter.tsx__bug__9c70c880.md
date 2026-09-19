<!-- source: src/components/StatusFooter.tsx | reviewer: zcode-glm-5.3 | sha256: 9c70c8801cb4d4d0c18c8da3726f7f542b447e2d56381a412cd1023453289698 | date: 2026-09-15 | mode: bug -->
<!-- context: post design-adversary remediation (docs/reviews/truth-copy-2026-09-15.md, B- -> ship). Evidence: tsc 0, vitest 508/508, tier 77/0/7. -->

## Verdict
Shippable - the command line now has a copyable second face.

## Fixed since last review (this delta, per adversary round 1)
- **[MINOR|FIXED] the cmdline lived only in a native tooltip** (unselectable, unguarded) - the pasteable diagnostics block gains a processes line: name(pid) GB + command line (client-truncated 160, ellipsis-marked); pinned by an exact-shape buildDiagnostics test.

## Bugs & vulnerabilities (delta)
- None. Pre-1.2.0 nodes degrade to the old tooltip/line (cmdline?: string | null - silence over a guess).
