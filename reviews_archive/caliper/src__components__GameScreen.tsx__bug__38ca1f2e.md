# colibri bug review - src/components/GameScreen.tsx

reviewer: ZCode (GLM-5.3, in-session) - sha256 38ca1f2e - 2026-08-26
mode: bug (first bug-mode review; a feature-mode review exists at a23a28cc) - context: read end to end (1503 lines); harness arcade-boot green; the four cabinet loops traced (brick collision/wall-descent, serpent hunger/rivals/gates, paddle deuce/smash, silo batteries/fallout)

## Verdict

Shippable after the one fix below. Arcade-stakes file, but the defect was a visible freeze, not a cosmetic.

## Fixed since this review (same session)

- [MEDIUM] SILO's killer-satellite block sat NESTED inside `if (bomber) { ... }` (the bomber block closed ~28 lines late, swallowing the sat spawn/update/remove code with misleading indentation). Consequences: the wave-3+ satellite only spawned while a bomber was airborne, and it FROZE mid-screen (drawn, never updated) the moment the bomber left - its comment and independent wave gating clearly intend it to run like the bomber. FIX: brace relocation; the sat block now stands at step level beside the bomber's.

## Missing safeguards

- Arrow keys are preventDefault'd at window scope whenever a cabinet is mounted - the four cabinet surfaces own the screen today, but any future keyboard UI on those surfaces will fight it.
- serpent's spawnFood falls back to a possibly-occupied cell after 60 tries (an eaten-through-wall edge, cosmetic).

## Verified-correct (adversarial passes, findings deleted)

- The SAVES module table's cross-surface persistence (one cabinet per surface, remount reuses); listener/raf teardown; the per-frame try/catch that survives cabinet errors; high-score migration single->list; bricks' gold/pierce/laser/wall-descent math; serpent bounty-vs-body hit rule and gate warp; paddle two-player flag capture at start; silo spawnInc mid-air materialization algebra and fallout settle/drain.
- Math.random throughout is correct for game randomness (Mimosa's crypto-scoped flag does not apply).
