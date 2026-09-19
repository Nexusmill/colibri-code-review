<!-- source: vite.film.ts | reviewer: zcode-glm-5.3 | sha256: 7ef59c3a749141e99133ef47f7cc9843b9f81b88f0542a1c67c2d4f0357b6447 | date: 2026-09-15 | mode: bug -->
<!-- context: Wave 7 (the analysis trio: beat-snapped carves, phrase grid for joins, legacy grid retirement) FINAL delta review. Live evidence: tsc -b --force 0, vitest 502/502, build OK, fast tier 76/0/8 incl. cut-on-the-music, live tool run on a real song: 74/74 interior cuts exactly on a beat, 69 phrases. -->

## Verdict
Shippable - three surgical wirings, no behavior change on any non-song path.

## Fixed since last review (this delta)
- **[CONFIRMED by the build|FIXED] block-scoped `phrases`** was consumed outside its song branch (a bare `tsc -b` had read stale buildinfo and passed; the full build caught it) - hoisted to the branch-shared declarations.

## Bugs & vulnerabilities (delta: beats+phrases at the draft site; winPhrases at the redraft)
- None. The redraft re-analyzes the song inside the fire-and-forget (cheap beside the minutes-long brain call) and stays silent without a song or film; the window filter is a true overlap test.
