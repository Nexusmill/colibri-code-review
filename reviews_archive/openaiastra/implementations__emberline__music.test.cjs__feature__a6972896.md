# Colibri feature review: music.test.cjs

Source: C:/Users/User/source/repos/OpenAIAstra/implementations/emberline/music.test.cjs
Reviewer: GPT-6 Codex /root (in-session Colibri review)
SHA-256: a6972896c35f7a4a13802b32dc55d5eedf9a1b9a7cd19841f760e3906ef0b061
Date: 2026-09-16 18:31 America/Denver
Mode: feature
Context pack: Indexed parseMidi/context; actual music.js scheduler/gain graph; current ducking callback and offline delivery contract.
Freshness: current source read end to end with line numbers, followed by a separate fresh-byte adversarial pass; SHA unchanged. No prior feature-mode entry exists for this unit. Other review modes are not superseded.

## What this module does
Checks all compositions and MIDI bytes, independently parses score events, and validates scheduling, voice bounds, gating and duck targets with a fake context.

## Suggested add-ons
### Offline audio audition and measurements — Value Med · Effort L
- **What:** Add an optional offline rendered-audio audition set and peak/RMS summaries for representative gardens and duck/unduck transitions.
- **Why:** MIDI parity and scheduled frequencies do not establish the sound of the mixed WebAudio output. Small rendered excerpts would make timbre and transition review repeatable.
- **How / hook points:** Use the existing composition matrix and public music.createPlayer; introduce a real offline-audio rendering lane alongside the fake context at lines 46–50. Render bounded excerpts with declared sample rate/time controls, include a duck transition from lines 78–88, and save samples/metrics under work/. Advance scheduling with the real offline context timeline rather than assuming its currentTime is writable. Keep the default Node suite dependency-light and retain exact MIDI asset checks at lines 74–75.

## Adversarial verification and contracts
CONFIRMED opportunity: note timing, all 50 shipped MIDI bytes and max voices already have assertions, so these are not missing deliverables. The context records scheduling but renders no PCM. PLAUSIBLE listening value; backend feasibility, device audibility and acceptable metric thresholds require implementation experiments and listening, not invented pass limits.
This is a proposed addition, not a confirmed bug or an implemented feature. Preserve offline operation, assigned vehicles and sequential gardens. Test tooling must use fixture-owned data and scratch outputs, not production saves or semantic stores. Value/effort are engineering estimates, not measured player outcomes.

## Nice-to-haves
Med value / S effort: a score summary table (tempo, part ranges, note density) derived from compose results at lines 10–14 to help choose representative audition cases.

## Review boundary
No source edits, new tests, live browser/device/listening validation or optional paid second opinion were performed for this review. Mandatory exact-byte artifact review and the repository commit gate are separate. Cross-file ranking: .colibri_reviews/2026-09-16-emberline-next-ten-feature-synthesis.md.
