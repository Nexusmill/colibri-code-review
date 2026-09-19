# Colibri bug review: implementations/emberline/ui.test.cjs

Source: C:/Users/User/source/repos/OpenAIAstra/implementations/emberline/ui.test.cjs
Reviewer: Codex, in-session context-aware review
SHA-256: a8ecdd2e8a1c971ab1fce052bafc870d85eaf7916080aeeef7b2cf3c50a47d95
Date: 2026-09-18
Mode: bug
Context: Current real game resume, engine/music/voice integration, routeReport target construction, manual/journal/HUD contracts, next-ten history and previous reset bug report 5ae66eac. Reviewed complete harness, top-level assertion groups and node:test cases.

## Verdict
2 confirmed test-oracle gap(s); the named behavior is not fully protected by the current assertions. Findings concern test evidence, not confirmed runtime failures.

## Bugs & vulnerabilities
**[MEDIUM] T3: Reachability acceptance omits all spectrum pickups** — line 300

The 150-case route test delegates its target set to routeReport and accepts every returned target. routeReport (tools/emberline-diagnostics.cjs:115–116) includes HOME, reset stations, ordinary embers and the rich patch, but no state.spectrumPickups. Therefore an opening shield pickup in an isolated clear pocket is never checked for connectivity. terrain.test.cjs checks collision clearance, which does not establish a connected route. Assert expected target identities/counts independently and include every opening spectrum pickup in the route acceptance.

Verification: Confirmed by the target-construction expression and caller. A disconnected but collision-clear spectrum pickup leaves the routeReport input fields it actually uses unchanged. This is a source-level omission; no existing generated unreachable pickup is claimed.

**[MEDIUM] T4: Focus-return test cannot detect missing canvas focus** — line 333

The test promises 'P still resumes with focus return', but only checks overlay.hidden. harness node.focus is an empty function at line 13 and document.activeElement is absent, so removing canvas.focus from game.js resume (line 101) cannot affect an assertion. Record focus in the DOM fixture, focus the summary before resuming, and assert focus returns to the arena. Keep native browser keyboard behavior as separate acceptance.

Verification: Confirmed by tracing KeyP to resume and reviewing every focus use in the harness. The optional browser test focuses the readable-HUD toggle; it does not test manual-to-arena focus restoration.

## Missing safeguards
- Passing ordinary checks is not mutation sensitivity, browser/device quality or a guarantee that all possible defects were found.

## Fixed since last review
Previous bug record: .colibri_reviews/implementations__emberline__ui.test.cjs__bug__5ae66eac.md, source SHA-256 5ae66eac6bc1c73f0350ad3c7ba72586161f27da005ae96bd6002df0d817fb00. The prior record reported no remaining open test defect. The findings above are newly identified current assertion gaps; no old finding is represented as fixed.

## Adversarial verification and validation
Current complete source was read with line numbers. Draft findings were checked against actual callers, producers and project ledgers; only the findings above survived. Findings are source-confirmed counterexamples, not executed mutation tests. Configured native run_checks: passed=true, exit_code=0, tree_unchanged=true; 37 Python tests ran, five skipped, including the nine-suite Node bridge. Tests and implementation were not changed by this review.
