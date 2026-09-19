# gardens.js — Colibri feature review

Source: C:/Users/User/source/repos/OpenAIAstra/implementations/emberline/gardens.js
Reviewer: GPT-6 Codex, in-session primary reviewer
SHA-256: ff056a7a1c144cd1e3a1a2a6b5578e21970b2ad9e4343afea9adcf2c259910bd
Bytes: 4164
Date: 2026-09-16
Mode: feature
Context: native jCodemunch module outlines; exact current runtime dependencies and callers; README, AGENT_STATE, ACTIVITY, FEATURES, REMEDIATION, DEFERRED and progression/combat task; relevant test assertions inspected where available. No prior feature-mode cache entry. Existing bug/spec/quality clearances are not feature reviews or current gameplay acceptance.

## What this module does
Shared definitions for 50 sequential gardens: biome identity, assigned vehicle, targets, roster, rich-patch position, spawn cadence and enemy caps.

## Suggested add-ons
### Briefings that explain the actual encounter role — Value High · Effort M
- What: Give each garden a compact briefing covering its assigned craft, drone versus hunter behavior, and the next newly relevant mechanic.
- Why / evidence: Lines 22–28 generate variants by spreading biome records, retaining their original lesson strings. engine.js spawnEnemy() lines 290–302 assigns tier-1/2 drones and later hunters; updateEnemy() branches on role. game.js lines 182 and 555 display g.lesson directly.
- How / hook points: Add structured briefing metadata composed with the current encounter-role policy, then render it in game.js and the paused field guide. Avoid duplicating the tier-role threshold in unrelated text logic; establish one shared policy source while preserving existing definition exports and module dependency order.

## Adversarial verification
CONFIRMED static opportunity: early mushroom lessons discuss spore rings, while newly spawned tier-2 enemies follow the drone path. This review proposes context-aware guidance, not a separate bug verdict. Preserve sequential advancement, curated vehicle assignment, score targets and existing checkpoint indices. Verify the briefings against every generated tier/role and show only information true for that level.

The complete file was read, then re-read through native read_file; SHA-256 was unchanged. Calls, existing functionality and recorded decisions were checked separately. CONFIRMED describes the static code basis, not proven player benefit. Proposed behavior has not been implemented or runtime-tested. No bug/spec clearance is issued in this feature review.

## Nice-to-haves
A small completion stamp per sequential garden could support the journey view. PLAUSIBLE; it must be read-only progress information and must not restore route or vehicle selection.
