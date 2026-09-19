# Colibri feature review: terrain.test.cjs

Source: C:/Users/User/source/repos/OpenAIAstra/implementations/emberline/terrain.test.cjs
Reviewer: GPT-6 Codex /root (in-session Colibri review)
SHA-256: 7783e72c81cfc72277876c6c59ff0f199e59b1e03e6793c77c8f2f1cc1656699
Date: 2026-09-16 18:31 America/Denver
Mode: feature
Context pack: Indexed terrain fixtures; actual terrain.move/clear interface; companion ui.test.cjs BFS and existing 50-garden acceptance; shared collision and checkpoint regeneration constraints.
Freshness: current source read end to end with line numbers, followed by a separate fresh-byte adversarial pass; SHA unchanged. No prior feature-mode entry exists for this unit. Other review modes are not superseded.

## What this module does
Tests shared collision extents, all-garden corridors, vehicle altitude, drilling, sweep movement, safe placement and recoverable cargo scatter.

## Suggested add-ons
### Route and clearance diagnostics — Value Med · Effort M
- **What:** Add an opt-in per-garden route report with reachable cells, target paths and geometric clearance margins.
- **Why:** Current boolean reachability evidence establishes routes; a compact map and failing target path would help explain a layout change and investigate tight approaches.
- **How / hook points:** Reuse the all-garden coverage at lines 6–8/27 and the actual T.move BFS in ui.test.cjs lines 285–305 through a shared test helper. Emit a bounded JSON/SVG artifact under work/ only when requested or on failure. Keep collision authority in terrain.js move/clear, and label geometric margins separately from inertia, enemy pressure and human playability.

## Adversarial verification and contracts
CONFIRMED diagnostic opportunity: actual 50-garden, three-seed target reachability already exists in ui.test.cjs, so a second copy is not the proposal. Preserve that coverage when sharing the helper. One-shot sweep and scatter tests at lines 21/30–40 remain independent. No unreachable production route is alleged.
This is a proposed addition, not a confirmed bug or an implemented feature. Preserve offline operation, assigned vehicles and sequential gardens. Test tooling must use fixture-owned data and scratch outputs, not production saves or semantic stores. Value/effort are engineering estimates, not measured player outcomes.

## Nice-to-haves
Med value / M effort: scripted approach/departure traces around a few representative pads using the real E.step mode fixture at lines 4–5, to complement geometric reachability without claiming exhaustive player balance.

## Review boundary
No source edits, new tests, live browser/device/listening validation or optional paid second opinion were performed for this review. Mandatory exact-byte artifact review and the repository commit gate are separate. Cross-file ranking: .colibri_reviews/2026-09-16-emberline-next-ten-feature-synthesis.md.
