# Colibri feature review: spectrum.test.cjs

Source: C:/Users/User/source/repos/OpenAIAstra/implementations/emberline/spectrum.test.cjs
Reviewer: GPT-6 Codex /root (in-session Colibri review)
SHA-256: 2dd26870cb101cd11fe72375e24139314886ec033dbc99561237a0caf68c2d9a
Date: 2026-09-16 18:31 America/Denver
Mode: feature
Context pack: Indexed shield helpers and spectrum.js preview; current effect/checkpoint contracts; ui.test.cjs forecast matrix; current HOME no-camping remediation.
Freshness: current source read end to end with line numbers, followed by a separate fresh-byte adversarial pass; SHA unchanged. No prior feature-mode entry exists for this unit. Other review modes are not superseded.

## What this module does
Tests FIFO packets, resistance, blue groups, effects, checkpoint validation, docking, teleport boundaries and replacement spawning.

## Suggested add-ons
### Stateful shield scenario corpus — Value Med · Effort M
- **What:** Add a bounded seeded sequence runner that interleaves packet arrival, ticks, cleansing and serialization and retains a minimal failing prefix.
- **Why:** Handwritten boundary examples are strong; mixed operation sequences can explore interactions between resistance, expiry and grouped direction locks that are expensive to enumerate manually.
- **How / hook points:** Build on S/fill/frames at lines 2–5 and the explicit expectations at lines 22–32/57–65. Generate legal operations with a fixture RNG independent of engine RNG, assert sixteen cells, bounded queue, consistent blue groups and unchanged source for preview, and round-trip valid shield state. Reuse the preview parity coverage in ui.test.cjs lines 263–275 instead of cloning it. Store only bounded failing fixtures under work/.

## Adversarial verification and contracts
CONFIRMED opportunity after comparing both suites: malformed checkpoints, exact FIFO timing, all blue directions and preview parity already exist. The new capability is sequence generation and shrinking, not a claim those cases are untested. Do not use production code as the sole oracle for every property or expect entry checkpoints to preserve world transients.
This is a proposed addition, not a confirmed bug or an implemented feature. Preserve offline operation, assigned vehicles and sequential gardens. Test tooling must use fixture-owned data and scratch outputs, not production saves or semantic stores. Value/effort are engineering estimates, not measured player outcomes.

## Nice-to-haves
Low value / S effort: a human-readable packet timeline for a selected fixture at lines 23–26, showing resistance changes as well as inserted cells; derive labels from existing metadata.

## Review boundary
No source edits, new tests, live browser/device/listening validation or optional paid second opinion were performed for this review. Mandatory exact-byte artifact review and the repository commit gate are separate. Cross-file ranking: .colibri_reviews/2026-09-16-emberline-next-ten-feature-synthesis.md.
