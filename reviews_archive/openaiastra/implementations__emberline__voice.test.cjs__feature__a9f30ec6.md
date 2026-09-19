# Colibri feature review: voice.test.cjs

Source: C:/Users/User/source/repos/OpenAIAstra/implementations/emberline/voice.test.cjs
Reviewer: GPT-6 Codex /root (in-session Colibri review)
SHA-256: a9f30ec6ab0555bf11c375c8b23ef55556205ccef5ebac9e4bfd5c34d1bc4c0a
Date: 2026-09-16 18:31 America/Denver
Mode: feature
Context pack: Indexed fixture and actual voice.js pump/update token guards; existing media and silent caption tests; current music duck integration.
Freshness: current source read end to end with line numbers, followed by a separate fresh-byte adversarial pass; SHA unchanged. No prior feature-mode entry exists for this unit. Other review modes are not superseded.

## What this module does
Checks narration text/counts, queue priorities, cancellation, stale callbacks, PCM assets and silent caption behavior.

## Suggested add-ons
### Controllable asynchronous audio fixture — Value High · Effort S
- **What:** Extend the fixture to explicitly resolve/reject each play promise and dispatch ended/error callbacks in chosen orders.
- **Why:** The existing fixture always resolves play immediately. A controllable scheduler can cheaply explore interruption and late media failure without real devices.
- **How / hook points:** Replace fixture-only play behavior at lines 3–8 with an optional deferred result controller, retaining the current default. Add scenarios for rejected play, audio.onerror, synchronous factory failure, and an old rejection after a newer line starts. Observe captions, queue state and duck restoration. Target voice.js pump at lines 32–45, where one sequence token guards the shared completion handler.

## Adversarial verification and contracts
CONFIRMED opportunity: lines 43–50 already test an old onended callback, and lines 64–74 test the silent factory prohibition. The proposal extends these with controlled promise/error interleavings; it does not claim cancellation is absent or that a real failure currently exists. Reuse this adapter in the ui.test.cjs integration lane rather than maintain two divergent fakes.
This is a proposed addition, not a confirmed bug or an implemented feature. Preserve offline operation, assigned vehicles and sequential gardens. Test tooling must use fixture-owned data and scratch outputs, not production saves or semantic stores. Value/effort are engineering estimates, not measured player outcomes.

## Nice-to-haves
Med value / S effort: a review-only phrase duration/word-rate table using the PCM parsing at lines 55–60 and current captions, highlighting long phrases for human review without inventing a universal reading-speed acceptance threshold.

## Review boundary
No source edits, new tests, live browser/device/listening validation or optional paid second opinion were performed for this review. Mandatory exact-byte artifact review and the repository commit gate are separate. Cross-file ranking: .colibri_reviews/2026-09-16-emberline-next-ten-feature-synthesis.md.
