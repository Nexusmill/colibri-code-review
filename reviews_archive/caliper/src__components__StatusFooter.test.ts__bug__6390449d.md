<!-- source: src/components/StatusFooter.test.ts | reviewer: zcode-glm-5.3 | sha256: 6390449dab7567665ed2391d1d07e53c880caa9761feb522c7b6197f862467e3 | date: 2026-09-15 | mode: bug -->
<!-- context: post design-adversary remediation (docs/reviews/truth-copy-2026-09-15.md, B- -> ship). Evidence: tsc 0, vitest 508/508, tier 77/0/7. -->

## Verdict
Shippable.

## Bugs & vulnerabilities (delta)
- None. The fixture carries a real cmdline; the assertion pins the exact processes-line shape (the adversary's "no automated guard" finding closed at the pure-function level).
