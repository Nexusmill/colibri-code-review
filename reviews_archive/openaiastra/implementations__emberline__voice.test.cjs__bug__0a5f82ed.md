# Colibri bug review: implementations/emberline/voice.test.cjs

Source: C:/Users/User/source/repos/OpenAIAstra/implementations/emberline/voice.test.cjs
Reviewer: Codex, in-session context-aware review
SHA-256: 0a5f82edca0db71b26cf32880048d0da661ccb0f23c8cc63c101a197cc1bc235
Date: 2026-09-18
Mode: bug
Context: Current narrator/media fixture and UI integration, caption/ducking/event contracts and previous bug report c261f7b1. Checked stale callbacks, promise rejection, inventory advice, PCM parser and caption-only mode.

## Verdict
1 confirmed test-oracle gap(s); the named behavior is not fully protected by the current assertions. Findings concern test evidence, not confirmed runtime failures.

## Bugs & vulnerabilities
**[LOW] T5: Unclipped PCM assertion accepts positive full-scale saturation** — line 60

The WAV check takes abs(int16) and accepts peak < 32768. A valid-length PCM buffer filled with +32767 satisfies peak > 500 and peak < 32768, while -32768 is rejected. It therefore cannot support its stated unclipped claim for positive saturation. Check the signed positive and negative rails (or a documented symmetric near-full-scale threshold), ideally counting saturated runs; retain a synthetic positive-rail and negative-rail regression.

Verification: Confirmed directly from signed 16-bit endpoints and the exact assertion: 32767 > 500 && 32767 < 32768 is true. The media helper's float clipped counter does not validate these shipped voice WAVs. No claim that current audio assets are clipped.

## Missing safeguards
- Passing ordinary checks is not mutation sensitivity, browser/device quality or a guarantee that all possible defects were found.

## Fixed since last review
Previous bug record: .colibri_reviews/implementations__emberline__voice.test.cjs__bug__c261f7b1.md, source SHA-256 c261f7b11dc364cd61f95c6282873b824bd7643b12c020c0322ba7e6711bce66. The prior record reported no remaining open test defect. The findings above are newly identified current assertion gaps; no old finding is represented as fixed.

## Adversarial verification and validation
Current complete source was read with line numbers. Draft findings were checked against actual callers, producers and project ledgers; only the findings above survived. Findings are source-confirmed counterexamples, not executed mutation tests. Configured native run_checks: passed=true, exit_code=0, tree_unchanged=true; 37 Python tests ran, five skipped, including the nine-suite Node bridge. Tests and implementation were not changed by this review.
