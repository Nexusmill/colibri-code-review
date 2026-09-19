# Colibri feature review: engine.test.cjs

Source: C:/Users/User/source/repos/OpenAIAstra/implementations/emberline/engine.test.cjs
Reviewer: GPT-6 Codex /root (in-session Colibri review)
SHA-256: ef899e94e8d189318b4f91006fc9435e546f2eb6fcc3bac5193721c32894f0af
Date: 2026-09-16 18:31 America/Denver
Mode: feature
Context pack: Indexed fresh/tick and runtime bridge; end-to-end test body; engine persistence and sequential decisions; 0eba7e0 source/test changes.
Freshness: current source read end to end with line numbers, followed by a separate fresh-byte adversarial pass; SHA unchanged. No prior feature-mode entry exists for this unit. Other review modes are not superseded.

## What this module does
Exercises progression, arsenal, enemy behavior, seeded movement, persistence, resource opening and primary upgrades through the real engine.

## Suggested add-ons
### Deterministic replay diagnostics — Value Med · Effort M
- **What:** Add a bounded scenario recorder/replayer for failed simulations that reports seed, fixed-step inputs and the first divergent step.
- **Why:** Long deterministic checks already exist, but their assertions do not produce a reusable input/event trace. A failing seed could become a small repeatable regression fixture.
- **How / hook points:** Extend fresh/tick at lines 4–5 and the deterministic runs at lines 27–28/50 with an opt-in trace helper. Capture only fixture-owned state and bounded input/event summaries under work/, retaining the current pure assertions. Replay from E.create(seed); treat E.checkpoint/E.restore at lines 31–32 as garden-entry persistence, not an exact mid-flight snapshot.

## Adversarial verification and contracts
CONFIRMED opportunity: the file already compares complete deterministic states and render chunk sizes, so do not add a duplicate determinism test as the feature. No recorder/replay artifact facility is present in this unit. The runner tests/test_emberline.py lines 9–25 invokes the suite with a fixed timeout; bound traces and default seed count to retain that contract.
This is a proposed addition, not a confirmed bug or an implemented feature. Preserve offline operation, assigned vehicles and sequential gardens. Test tooling must use fixture-owned data and scratch outputs, not production saves or semantic stores. Value/effort are engineering estimates, not measured player outcomes.

## Nice-to-haves
Med value / M effort: report per-garden scripted-bot delivery/damage metrics alongside line 27, labelled diagnostics rather than a human difficulty verdict; retain sequential progression.

## Review boundary
No source edits, new tests, live browser/device/listening validation or optional paid second opinion were performed for this review. Mandatory exact-byte artifact review and the repository commit gate are separate. Cross-file ranking: .colibri_reviews/2026-09-16-emberline-next-ten-feature-synthesis.md.
