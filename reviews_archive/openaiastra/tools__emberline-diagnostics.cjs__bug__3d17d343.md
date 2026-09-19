# Emberline diagnostics implementation review

Source: tools/emberline-diagnostics.cjs
Reviewer: Codex in-session review plus mandatory native exact-byte independent review
SHA-256: 3d17d3434be2c0c980ec82f68502dcc09104620d463e8abcd4611a1ee554e0d9
Date: 2026-09-17
Mode: bug
Context: current native engine, gardens, spectrum, terrain, diagnostics.test.cjs and tests/test_emberline.py; preserved proposal and remediation handoff. Indexed repository resolved local/OpenAIAstra. User explicitly requested exact preserved candidate acceptance.

## Verdict
The preserved candidate received native independent CLEAR and exact byte readback matched all 11191 bytes. Repository checks passed, including the existing Python bridge executing all nine Node suites and the three diagnostics regressions. This is acceptance of this helper tranche, not completion of all ten feature proposals or proof that a reviewer fallback branch executed.

## Bugs & vulnerabilities
No confirmed blocking defect found in the exercised replay, shield or route APIs. The prior missing terrain.clear finding is refuted by current native terrain.js export and the passing route regression. Candidate was applied unchanged; no substantive BLOCK was overridden.

## Missing safeguards and validation limits
- CLI JSON/SVG artifact generation, filesystem link cases and artifact byte-limit rejection have not been exercised through a dedicated CLI test in this tranche.
- Existing 150-case UI BFS still has its own implementation; shared-helper extraction remains open.
- Full-state replay hash comparison is same-version deterministic diagnostics; source hashes are recorded, not enforced as a cross-version compatibility guarantee.
- Route clearance is geometric target clearance, not inertial navigation or enemy-pressure validation.

## Adversarial verification and synthesis
The current terrain source exports clear and move, and dt=0 prevents drilling. Spectrum restore, preview and packet sizes match the helper's call sites; black inserts two cells and blue inserts four. Tests cover unchanged inputs, repeatable replay, first divergence, legal mixed operations, earliest failing prefix, unobstructed and blocked routing, and SVG label escaping. Existing gameplay tests also passed through the bridge. No engine behavior changed in this tranche.

## Native review evidence
First request: reviewer unavailable, no write; .adversary/write-reviews/2ef8211ecdf145c1a3cfe0d208ad3a63.json. A documentation request subsequently received CLEAR, providing new availability evidence for one bounded retry. Exact candidate retry: CLEAR, .adversary/write-reviews/c8d5b150891244d1a31c2b04a6e21894.json. Evidence JSON is not readable through this broker, so the actual provider/fallback sequence remains unverified.

## Verification
Fresh verification-before-completion loaded after helper application. Native run_checks: passed true, exit_code 0, tree_unchanged true; 36 tests in 48.675s, four skipped. Final post-documentation checks and automatic Git review are required separately.
