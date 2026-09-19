# engine.js — Colibri feature review

Source: C:/Users/User/source/repos/OpenAIAstra/implementations/emberline/engine.js
Reviewer: GPT-6 Codex, in-session primary reviewer
SHA-256: 306ea0d9089f0a9611ce0011c41a35bd6ed0a98ca754420974c1443fec1971f1
Bytes: 29502
Date: 2026-09-16
Mode: feature
Context: native jCodemunch module outlines; exact current runtime dependencies and callers; README, AGENT_STATE, ACTIVITY, FEATURES, REMEDIATION, DEFERRED and progression/combat task; relevant test assertions inspected where available. No prior feature-mode cache entry. Existing bug/spec/quality clearances are not feature reviews or current gameplay acceptance.

## What this module does
Deterministic simulation: collection and quadratic banking, sequential gardens, primary fire, FIFO reserve weapons, enemies, shield integration, terrain movement and validated garden-entry checkpoints.

## Suggested add-ons
### Primary-weapon progress and upgrade feedback — Value High · Effort S
- What: Expose the primary level, progress to the next level, and a one-time upgrade event so players can see why gathering light improves combat.
- Why / evidence: primary() lines 138–145 derives level from stats.collected, increases damage and lowers the base cooldown; checkpoint()/restore() lines 460–485 already preserve collected. game.js updateHUD() lines 161–183 presents reserve power but no primary progress. This is an information feature around an existing weapon, not a new weapon.
- How / hook points: Factor the existing level calculation into a pure engine query used by primary() and the HUD; emit an upgrade event at the actual collection boundary in step(). Cap at level 10, display MAX at 72 collected, and avoid inventing a level 11 target. Let game.js consume the event once.

## Adversarial verification
CONFIRMED static opportunity: re-read primary, collection, checkpoint and UI paths; the primary weapon and persistent upgrades already exist, while the display/query does not. Preserve damage, cadence, FIFO and save compatibility. Future tests: 7→8 and 71→72 collections, capped progress, restored saves, no duplicate notification.

The complete file was read, then re-read through native read_file; SHA-256 was unchanged. Calls, existing functionality and recorded decisions were checked separately. CONFIRMED describes the static code basis, not proven player benefit. Proposed behavior has not been implemented or runtime-tested. No bug/spec clearance is issued in this feature review.

## Nice-to-haves
A per-garden delivery summary could compare time, biggest bank and cargo lost. PLAUSIBLE product value; nextGarden() resets gardenTime but cumulative stats must be snapshotted before transition rather than mislabeled as garden totals.
