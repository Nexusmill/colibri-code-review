<!-- source: tools/ui-harness.mjs | reviewer: zcode-glm-5.3 | sha256: 67ffee3412cbe73993307cc9f4282fceaefbec0be65f95441ff4330470323abc | date: 2026-09-15 | mode: bug -->
<!-- context: Wave 7 (the analysis trio: beat-snapped carves, phrase grid for joins, legacy grid retirement) FINAL delta review. Live evidence: tsc -b --force 0, vitest 502/502, build OK, fast tier 76/0/8 incl. cut-on-the-music, live tool run on a real song: 74/74 interior cuts exactly on a beat, 69 phrases. -->

## Verdict
Shippable - the coverage gate itself forced the cold harness row the manifest doctrine demands, and the click-track test is a real end-to-end proof of the cut grammar.

## Bugs & vulnerabilities (delta: cut-on-the-music)
- None. The fixture dir is mkdtemp'd and removed in a finally; the tool run rejects with stderr on failure; assertions check the invariant (every interior cut AND every phrase start exactly on a beat), not implementation details.
