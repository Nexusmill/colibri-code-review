# Colibri feature review: ui.test.cjs

Source: C:/Users/User/source/repos/OpenAIAstra/implementations/emberline/ui.test.cjs
Reviewer: GPT-6 Codex /root (in-session Colibri review)
SHA-256: dcde5bfdf763a4c2a0e6446589a6ba13d646bc1f63308f98b5ec52ae4d20e39c
Date: 2026-09-16 18:31 America/Denver
Mode: feature
Context pack: Indexed harness and fixed Python-to-Node runner; actual game.js event/frame/audio callbacks; existing per-module tests and new feature release.
Freshness: current source read end to end with line numbers, followed by a separate fresh-byte adversarial pass; SHA unchanged. No prior feature-mode entry exists for this unit. Other review modes are not superseded.

## What this module does
Runs game.js in a VM with a DOM/canvas facade, records inputs and presentation, and separately checks shield forecasts and terrain routes.

## Suggested add-ons
### Real-runtime integration lane — Value High · Effort M
- **What:** Add a second harness mode that runs the real engine step and real music/voice scheduler modules together, with controlled audio/time boundaries.
- **Why:** The current isolated harness is useful for presentation and input tests, but replacing engine.step and both audio modules prevents it from exercising the full event-to-caption-to-ducking chain.
- **How / hook points:** Keep the default harness at lines 6–24. Add an explicit integration option replacing the stubs at lines 13, 15–16 with real modules, while providing deterministic Audio and AudioContext adapters. Start from fixture-owned storage, drive a real dock/reset event and inspect the caption plus music bus gain, then pause/mute/resume. Use game.js frame line 573, ensureVoice line 89 and unlockAudio line 94 as the actual chain.

## Adversarial verification and contracts
CONFIRMED scope gap, not a production bug: music.test.cjs tests setDucked locally, voice.test.cjs tests callbacks, and this file checks forwarding/settings at lines 207–223. Its music stub has no setDucked and voice stub does not exercise onDuck. Existing real shield/terrain checks at lines 263–310 do not connect these schedulers. Physical devices, focus and rendered CSS still require browser QA.
This is a proposed addition, not a confirmed bug or an implemented feature. Preserve offline operation, assigned vehicles and sequential gardens. Test tooling must use fixture-owned data and scratch outputs, not production saves or semantic stores. Value/effort are engineering estimates, not measured player outcomes.

## Nice-to-haves
High value / L effort: a small real-browser keyboard/focus and viewport smoke lane for the manual/primary controls; node() at line 11 has a no-op focus and fixed bounds, so keep browser results distinct from VM assertions.

## Review boundary
No source edits, new tests, live browser/device/listening validation or optional paid second opinion were performed for this review. Mandatory exact-byte artifact review and the repository commit gate are separate. Cross-file ranking: .colibri_reviews/2026-09-16-emberline-next-ten-feature-synthesis.md.
