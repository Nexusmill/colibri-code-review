# Colibri feature review: world3d.test.cjs

Source: C:/Users/User/source/repos/OpenAIAstra/implementations/emberline/world3d.test.cjs
Reviewer: GPT-6 Codex /root (in-session Colibri review)
SHA-256: 2a54b94b70f645eecedd7467ecab1d4280f632cc2074dea0c790fc6e0d8fdd17
Date: 2026-09-16 18:31 America/Denver
Mode: feature
Context pack: Indexed canvas factories and geometry tests; actual game.js physicalWorld call; shared collision renderer contract, cache/readability implementation and visual QA limits.
Freshness: current source read end to end with line numbers, followed by a separate fresh-byte adversarial pass; SHA unchanged. No prior feature-mode entry exists for this unit. Other review modes are not superseded.

## What this module does
Tests geometry, pass ordering, water, material cropping, cache bounds/invalidation and terrain overlay commands through canvas spies.

## Suggested add-ons
### Real-canvas scene gallery and cache parity — Value High · Effort L
- **What:** Add a deterministic real-canvas gallery that compares cached and uncached rendering and captures representative occlusion/material/overlay scenes.
- **Why:** Command assertions explain geometry and call order but cannot show the final composed pixels. A gallery would make subtle clipping, cache offsets and overlay readability inspectable.
- **How / hook points:** Reuse the box fixtures and scenes at lines 3–13/15–28 with a pinned canvas/browser backend, fixed time and explicit dimensions. Render cache on/off for the same scene, include ground/flyer and damaged/broken states, and output images/differences to work/. Use actual game.js physicalWorld at line 546 to preserve pass/actor/classifier ordering; keep finite/default-solid edge assertions.

## Adversarial verification and contracts
CONFIRMED opportunity: the current contexts are proxies and cache sprites are mocked, while geometry, invalidation and malformed-box handling already have coverage. PLAUSIBLE visual value; cross-platform raster tolerances need calibration, so no current pixel mismatch or universal exact-equality guarantee is alleged. A backend is an explicit dependency, not something the current Node bridge already provides.
This is a proposed addition, not a confirmed bug or an implemented feature. Preserve offline operation, assigned vehicles and sequential gardens. Test tooling must use fixture-owned data and scratch outputs, not production saves or semantic stores. Value/effort are engineering estimates, not measured player outcomes.

## Nice-to-haves
Med value / M effort: a bounded render-cost trend report around line 13 using controlled scenes and operation counts; label it a regression signal rather than device frame-rate evidence.

## Review boundary
No source edits, new tests, live browser/device/listening validation or optional paid second opinion were performed for this review. Mandatory exact-byte artifact review and the repository commit gate are separate. Cross-file ranking: .colibri_reviews/2026-09-16-emberline-next-ten-feature-synthesis.md.
