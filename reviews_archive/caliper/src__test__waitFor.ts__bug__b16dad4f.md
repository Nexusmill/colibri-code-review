source: src/test/waitFor.ts
reviewer: tencent/hy4-preview (scan ladder hunt T1)
sha256: b16dad4f747a1d87f58474221ee232e8c348501464fb6962e9578619dfdd3a91
date: 2026-09-19 11:40
mode: bug
context: TESTFILEHUNT class-fix helper; poll-until-observed contract

First-ever bug scan. 3 findings:
- [MEDIUM] CONFIRMED + FIXED: the deadline could overshoot by up to one step (`>` + uncapped sleep) - a condition met past timeoutMs passed as if within it. FIXED: hard deadline, sleep capped at remaining.
- [MEDIUM] REFUTED: default 2000ms < vitest 5000ms. Deliberate design (fail fast at 20x the observed settle times; callers override with timeoutMs).
- [MEDIUM] REFUTED: pending setTimeout never cleared. At 10ms step granularity in a test-only helper there is no reachable harm; an AbortSignal API for an unraced helper is over-engineering.
