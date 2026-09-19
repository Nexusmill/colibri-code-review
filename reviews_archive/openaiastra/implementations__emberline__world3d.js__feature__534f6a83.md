# world3d.js — Colibri feature review

Source: C:/Users/User/source/repos/OpenAIAstra/implementations/emberline/world3d.js
Reviewer: GPT-6 Codex, in-session primary reviewer
SHA-256: 534f6a83a48c72ab9656213967cc362f8a14c898a5f553514a9eb1014ef3c966
Bytes: 10286
Date: 2026-09-16
Mode: feature
Context: native jCodemunch module outlines; exact current runtime dependencies and callers; README, AGENT_STATE, ACTIVITY, FEATURES, REMEDIATION, DEFERRED and progression/combat task; relevant test assertions inspected where available. No prior feature-mode cache entry. Existing bug/spec/quality clearances are not feature reviews or current gameplay acceptance.

## What this module does
Software projection and lighting of shared terrain geometry, material textures, back/front passes, bounded cached sprites, drill damage and underwater overlays.

## Suggested add-ons
### Optional terrain readability overlay — Value Med · Effort M
- What: Let players distinguish obstacles their assigned craft can clear from those it must avoid, and see the ground footprint of tall structures.
- Why / evidence: project() line 5 offsets tall geometry, passFor() line 14 selects depth layers, and draw() lines 39–60 caches rendered meshes. terrain.js overlaps() lines 13–18 defines authoritative altitude and footprint collision. game.js physicalWorld()/physicalPlayer() lines 522–523 supplies terrain and actor position.
- How / hook points: Add an opt-in outline or footprint overlay based on shared terrain collision metadata and current vehicle altitude. Render dynamic highlights after cached art, or include the new visual state in cache keys; do not silently reuse stale tinted sprites. Use symbols/line patterns as well as color and preserve reduced motion.

## Adversarial verification
CONFIRMED static integration points; whether silhouettes are hard to read is PLAUSIBLE and unverified without browser/player QA. Terrain rendering and drill labels already exist, so the proposed addition is a tactical clarity mode. Test high/low solids, broken terrain, front/back passes and cached-versus-uncached agreement before visual acceptance.

The complete file was read, then re-read through native read_file; SHA-256 was unchanged. Calls, existing functionality and recorded decisions were checked separately. CONFIRMED describes the static code basis, not proven player benefit. Proposed behavior has not been implemented or runtime-tested. No bug/spec clearance is issued in this feature review.

## Nice-to-haves
A player-visible graphics-quality selector could reduce decorative water/texture detail. PLAUSIBLE; no measured FPS bottleneck or current performance defect is asserted.
