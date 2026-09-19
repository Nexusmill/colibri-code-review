<!-- source: src/film/analysis.ts | reviewer: zcode-glm-5.3 | sha256: 47fe2512b8451cc95a8f4e41735d1c4caead3af4a24ed56004f5108959503077 | date: 2026-09-15 | mode: bug -->
<!-- context: Wave 7 FINAL delta review (post gate catch: the snap now keeps the carve's ceiling/floor bounds). Live evidence: tsc -b 0, vitest 503/503, build OK, fast tier 76/0/8 incl. cut-on-the-music on the fixed bytes. -->

## Verdict
Shippable - the module owns every grid (snap, phrase lattice, energy-paced carve) and the carve now honors its own bounds under snapping, red-green proven.

## Fixed since last review (this delta, in session order)
- **[RETIREMENT per pass-2 spec] the legacy per-section shotGrid is deleted** - its only code caller (tools/analyze-song.mjs) switched to the wired grid; its snap survives as the exported snapToBeat (same 0.35s tolerance).
- **[CONFIRMED by the adversarial commit gate|FIXED red-green] the snap could break the carve's own bounds** - a FORWARD beat (within tolerance, past the computed boundary) pushed a quiet-section slot past the engine ceiling (clipSeconds IS maxClipSeconds - the 2026-09-05 unrenderable-take class), and a backward beat could dip under the 2s floor; the existing ceiling test passed no beats so it could not see it. FIXED: the snap only lands on a beat inside [t+floor, min(t+ceiling, duration)] - candidates filtered to the bounds, then snapToBeat's nearest-within-0.35 (doctrine over music; no candidate keeps the computed time). Pinned by a test that failed red at exactly the gate's numbers (15.2 vs 15) and passes green.

## Bugs & vulnerabilities (delta)
- **[LOW|noted] phraseGrid's tail phrase can run past the song's true end** (no duration parameter by design) - harmless as consumed: a boundary past the song cannot fall near any shot edge.
- The bounds filter assumes ascending beats (beatGrid's contract) - consistent with snapToBeat.
