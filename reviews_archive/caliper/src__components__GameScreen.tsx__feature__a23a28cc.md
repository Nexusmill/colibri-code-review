# Colibri review — src/components/GameScreen.tsx (feature)

- **Source:** `src/components/GameScreen.tsx` @ commit `42f69e7`
- **sha256:** `a23a28ccbb57939af8e22843e091834bd202a2e3ba7d3031f83d93f190deaa3` (see manifest)
- **Model:** claude-fable-5 (in-session) · **Date:** 2026-08-18 · **Mode:** feature

## What this module does

The chassis' left-screen arcade: four canvas games (BRICKS/SERPENT/PADDLE/SILO)
with a shared cabinet shell — attract screen (replicate CRT title art), HOW TO
PLAY, play, dated three-initial high scores in localStorage, RELOAD, return to
attract after initials. State survives surface switches via a module save table.

## Suggested add-ons — verdicts (client ordered "implement the doable good")

IMPLEMENTED this pass:
- SERPENT hunger clock (client spec): timed feeding, segment loss, bare-head
  death; hungerMax tightens with length. Value High · Effort S.
- SERPENT rival snakes / 3 lives (client spec, earlier pass) + speed and food
  value scaling with length. High · S.
- SILO super bomb (client spec): right-click/Ctrl, one per wave (cap 3), 4×
  blast, nuke flash + mushroom ring; FALLOUT: drifting gusted clouds that
  settle — battery ammo drain 1/1.5s, one cloud sickens a city (palette
  shift), two kill it. High · M — the game's signature risk/reward now.
- BRICKS power-up drops (wide paddle 12s / slow ball 8s / extra life) from
  P-marked blocks; exploding star blocks (earlier pass). High · S.
- PADDLE serve countdown + ball trail; first-to-7 match frame. Med · S.
- Shell: HOW TO PLAY phase, dated highs, initials→attract, CRT scanlines,
  SILO aim reticle + floating +25 popups. Med · S.

CONSIDERED, DEFERRED (good but not this pass):
- Sound (WebAudio bleeps): the machine is silent by design so far — needs the
  client's call on audio at all. Med · S.
- BRICKS multiball: collision loop refactor; queue behind client demand. Med · M.
- SILO screen-shake on nuke: cheap thrill, mildly at odds with the fitted-glass
  conceit (the "monitor" shaking reads as chassis damage). Low · S.
- Persistent top-5 score tables per game (vs single best): UI space on the
  attract screen is tight over the art. Med · S.
- Rival serpents eating food/growing: fun but muddies the hunger economy the
  client just specified. Low · M.

## Notes

- Digits excluded from initials deliberately: 1–5 are the chassis' surface
  hotkeys; a digit mid-entry would switch screens.
- All games clear `p.alts` when unused so Ctrl/right-click can never queue
  stale super-bomb shots across cabinets.
