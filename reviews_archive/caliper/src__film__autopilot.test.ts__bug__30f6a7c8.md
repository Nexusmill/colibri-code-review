<!-- source: src/film/autopilot.test.ts | reviewer: zcode-glm-5.3 | sha256: 30f6a7c83fe7a01d0e5415713472a3239023167dc45cac8632fcab79639671f3 | date: 2026-09-15 | mode: bug -->
<!-- context: Wave 7 FINAL delta review (post gate round 2: clamped phrase ends now speak). Evidence: tsc 0, vitest 504/504, build OK, tier 76/0/8, live tool 74/74 on-beat. -->

## Verdict
Shippable - the beat-snap cases pin bounds and tolerance red-green; the phrase-line test pins the clamped-end union exactly.

## Bugs & vulnerabilities (delta)
- None. The clamped-end test asserts the full boundary list (0.0/4.8/6.0/9.6/14.4), the single occurrence of a shared edge, and the no-phrases absence.
