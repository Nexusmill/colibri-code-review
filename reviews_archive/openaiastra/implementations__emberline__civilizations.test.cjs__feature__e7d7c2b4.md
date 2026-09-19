# Colibri feature review: civilizations.test.cjs

Source: C:/Users/User/source/repos/OpenAIAstra/implementations/emberline/civilizations.test.cjs
Reviewer: GPT-6 Codex /root (in-session Colibri review)
SHA-256: e7d7c2b4c61ad78caa0802942b498bf71dc0d9dd7a55bd8494ced6a38a291fe7
Date: 2026-09-16 18:31 America/Denver
Mode: feature
Context pack: Indexed FakeImage and actual civilizations.js create/draw call; UI sprite callers; historical orientation assertions and current journal restrictions.
Freshness: current source read end to end with line numbers, followed by a separate fresh-byte adversarial pass; SHA unchanged. No prior feature-mode entry exists for this unit. Other review modes are not superseded.

## What this module does
Tests atlas selection, all 160 frame mappings, fractional crop bounds, readiness/fallback and per-culture orientation metadata with fake images.

## Suggested add-ons
### Shipped-atlas audit and contact sheets — Value High · Effort M
- **What:** Add a release-facing audit that decodes the shipped atlases and generates labelled contact sheets for frame occupancy, alpha margins and heading inspection.
- **Why:** The mapping checks currently inject image dimensions. Real asset bytes can change without altering those fixture dimensions or source metadata.
- **How / hook points:** Keep FakeImage tests at lines 4–23. Add an opt-in real-asset pass using paths created by civilizations.js create at lines 36–41 and the same frame keys, recording image hash, dimensions and nontransparent bounds per crop. Produce contact sheets under work/ for a human heading review using expectations at lines 27–39. Avoid a production atlas editor or new selection controls.

## Adversarial verification and contracts
CONFIRMED testing capability opportunity: the complete unit does not decode PNG bytes, while current runtime readiness checks only positive square dimensions and draws fractional cells. Existing historical visual inspection is acknowledged by the heading assertions; it is not current-byte asset verification. PLAUSIBLE detection of visual defects; no current atlas corruption is claimed.
This is a proposed addition, not a confirmed bug or an implemented feature. Preserve offline operation, assigned vehicles and sequential gardens. Test tooling must use fixture-owned data and scratch outputs, not production saves or semantic stores. Value/effort are engineering estimates, not measured player outcomes.

## Nice-to-haves
Low value / S effort: a stable-id/lore coverage table using C.civilizations, complemented by the actual-entry journal tests already in ui.test.cjs lines 325–335.

## Review boundary
No source edits, new tests, live browser/device/listening validation or optional paid second opinion were performed for this review. Mandatory exact-byte artifact review and the repository commit gate are separate. Cross-file ranking: .colibri_reviews/2026-09-16-emberline-next-ten-feature-synthesis.md.
