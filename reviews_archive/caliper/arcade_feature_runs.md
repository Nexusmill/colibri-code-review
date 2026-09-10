# Arcade — iterative colibri feature runs (10 per cabinet)

Client order 2026-08-18: "do the run, then implement, then do another run —
10 feature runs on each game." Method per run: propose from genre canon +
play-state reasoning, verdict each idea, implement survivors, next run
builds on the result. Runs converge honestly — a dry run is recorded as
dry, not padded (G1). File under review: src/components/GameScreen.tsx.

## BRICKS (Breakout/Arkanoid canon)
1. colours per row + row-scaled points → IMPLEMENTED (v2)
2. exploding star blocks 3×3 → IMPLEMENTED (v2, client spec)
3. power-up drops E/S/L → IMPLEMENTED (v3)
4. multi-hit silver bricks (2hp, top rows, level-scaled) → IMPLEMENTED (v4)
5. MULTIBALL drop (M splits into 3) → IMPLEMENTED (v4)
6. canon top-wall paddle shrink (per serve) → IMPLEMENTED (v4)
7. combo scoring (4+ bricks without paddle touch = ×2) + LEVEL interstitial → IMPLEMENTED (v4)
8. laser paddle → IMPLEMENTED (2026-08-19: Z power-up, 10s of twin bolts
   fired by click from the paddle ends - SILO proved click works on the glass)
9. brick-fall/shifting walls (Arkanoid DOH stages) → IMPLEMENTED (2026-08-19:
   4 rotating stage shapes; from level 3 the wall descends a row on a
   shrinking timer, capped at 5) + multiball capped at 6 with symmetric splits
10. CONVERGED — remaining canon (capsule variety, enemies) exceeds the 320px cabinet's scope.

## SERPENT (Snake canon + house twists)
1. rival snakes, 3 lives → IMPLEMENTED (v3, client spec)
2. hunger clock w/ segment loss → IMPLEMENTED (v3, client spec)
3. expiring bonus morsels → IMPLEMENTED (v3)
4. rivals EAT your food and grow (steal the meal the hunger clock needs) → IMPLEMENTED (v4)
5. tail-bite bounty (bite a rival's last two segments to kill it, +40) → IMPLEMENTED (v4)
6. wall hazards at score 60/120 → IMPLEMENTED (v4)
7. READY pause between lives → IMPLEMENTED (v4)
8. quick-eat bonus (+3 while hunger >60%) + length-scaled speed/food value → IMPLEMENTED (v4)
9. moving wall mazes → IMPLEMENTED (2026-08-19, with the wrap redesign: at
   score 60 the pit SEALS (red border, border = death) and the mazes drift
   on slow sine paths; rivals still wrap - they live in the walls)
10. CONVERGED — poison food rejected (duplicates hunger pressure), portals rejected (muddies wrap).

## PADDLE (Pong canon)
1. rally scoring + speed-up per return → IMPLEMENTED (v3)
2. serve countdown + ball trail → IMPLEMENTED (v3)
3. paddle-motion spin (your velocity bends the ball) → IMPLEMENTED (v4)
4. rubber-band AI (eases when leading, digs in behind) → IMPLEMENTED (v4)
5. deuce — win by two at 6-6, with callout → IMPLEMENTED (v4)
6. wall-bounce court flash → IMPLEMENTED (v4)
7. big ghosted score digits mid-court → IMPLEMENTED (v2)
8. two-player same-keyboard → IMPLEMENTED (2026-08-19: hold A or D on the
   howto screen at deploy to take the top paddle - A/D steer it, held-state
   keys added to the input map without stealing initials typing)
9. obstacles mid-court (Pong variants) → REJECTED (purity: the machine plays it straight)
10. CONVERGED.

## SILO (Missile Command canon + house twists)
1. three batteries, own ammo, nearest-fires → IMPLEMENTED (v3, client spec)
2. super bomb + fallout economy → IMPLEMENTED (v3, client spec)
3. MIRV splits from wave 3 → IMPLEMENTED (v3)
4. warheads destroy BATTERIES too; rebuilt each wave (canon) → IMPLEMENTED (v4)
5. bomber flyer crossing and dropping warheads; kill for +100 (canon) → IMPLEMENTED (v4)
6. chain-kill bonus per blast (CHAIN xN popups) → IMPLEMENTED (v4)
7. blast waves scatter unsettled fallout (nuke your own mess) → IMPLEMENTED (v4)
8. itemized wave-bonus readout (ammo +N / cities +N) → IMPLEMENTED (v4)
9. smart bombs that dodge blasts (canon) → IMPLEMENTED (round 2026-08-19: wave 4+,
   22% spawn, weave away from any blast within r+34 (steering clamped ±46px,
   sine wobble), gold pulsing diamond, +40 base kill, replaces MIRV roll on
   those spawns; only a dead-centre or super burst connects)
10. CONVERGED — "THE END" cinematic rejected as duplicating the shell's game-over.
11. CLIENT ORDER (2026-08-18, executed 08-19): NUCLEAR FALLOUT REMOVED - clouds,
    settle/city-sickness, tower ammo drain, blast-scatter all excised; the super
    bomb keeps its 4x blast + nukeFlash. Howto card rewritten.

Round 2026-08-19 additions: SOUND (arcadeSound.ts WebAudio synth, ~24 wired
events across all cabinets), TOP-5 dated score tables (attract-screen table,
rank callout on entry, old single-best saves migrate), and a stale-input fix
(keys typed during play no longer flood the initials screen). ALL DEFERRALS
FROM THE 10-RUN LEDGER ARE NOW CLOSED.

Verification: tsc clean, vite build ok, 62 vitest green after each wave.
Play-verification on the live machine is the client's half of the loop.
