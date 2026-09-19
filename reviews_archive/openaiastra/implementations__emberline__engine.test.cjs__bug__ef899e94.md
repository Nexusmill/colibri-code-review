# Colibri bug review: implementations/emberline/engine.test.cjs

Source: C:/Users/User/source/repos/OpenAIAstra/implementations/emberline/engine.test.cjs
Reviewer: Codex, in-session context-aware review
SHA-256: ef899e94e8d189318b4f91006fc9435e546f2eb6fcc3bac5193721c32894f0af
Date: 2026-09-18
Mode: bug
Context: Campaign50, sequential assigned-craft and recent encounter/primary resource changes; current gardens, spawnEnemy, checkpoint/restore; previous bug report 2980b701. Reviewed all tests and fixtures.

## Verdict
1 confirmed test-oracle gap(s); the named behavior is not fully protected by the current assertions. Findings concern test evidence, not confirmed runtime failures.

## Bugs & vulnerabilities
**[MEDIUM] T2: First-two-spawns regression never observes a spawn** — line 53

The test named 'every stage mixes enemies within its first two spawns' only checks new Set(g.types).size >= 2. spawnEnemy selects types separately using spawnCount modulo roster length (engine.js:300). A regression that always picks types[0] preserves every assertion in this test. Exercise two successful real spawns for each garden and compare their observed types against an independently chosen expectation; assert both spawns actually occurred.

Verification: Confirmed by tracing the current spawnEnemy implementation against the complete test body. Other engine tests exercise one spawn or roster differences after longer runs; none asserts the first two actual types in all 50 gardens. No production spawn defect is claimed.

## Missing safeguards
- Passing ordinary checks is not mutation sensitivity, browser/device quality or a guarantee that all possible defects were found.

## Fixed since last review
Previous bug record: .colibri_reviews/implementations__emberline__engine.test.cjs__bug__2980b701.md, source SHA-256 2980b70195f165429a9ba2dbc41af7b3e3c5c553828139723d4e6d6262fd3490. The prior record reported no remaining open test defect. The findings above are newly identified current assertion gaps; no old finding is represented as fixed.

## Adversarial verification and validation
Current complete source was read with line numbers. Draft findings were checked against actual callers, producers and project ledgers; only the findings above survived. Findings are source-confirmed counterexamples, not executed mutation tests. Configured native run_checks: passed=true, exit_code=0, tree_unchanged=true; 37 Python tests ran, five skipped, including the nine-suite Node bridge. Tests and implementation were not changed by this review.
