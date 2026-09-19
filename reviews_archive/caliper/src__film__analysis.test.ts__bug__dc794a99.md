<!-- source: src/film/analysis.test.ts | reviewer: zcode-glm-5.3 | sha256: dc794a99b314e5e0d21c16c655ee81d7899a80ded78e5acb7f475a370b421bab | date: 2026-09-15 | mode: bug -->
<!-- context: Wave 7 (the analysis trio: beat-snapped carves, phrase grid for joins, legacy grid retirement) FINAL delta review. Live evidence: tsc -b --force 0, vitest 502/502, build OK, fast tier 76/0/8 incl. cut-on-the-music, live tool run on a real song: 74/74 interior cuts exactly on a beat, 69 phrases. -->

## Verdict
Shippable - legacy grid tests replaced by snap + phrase tests with hand-verified arithmetic.

## Bugs & vulnerabilities (delta)
- None. The phrase test pins grouping, the section clamp, and the tail-length closure; the snap test pins both sides of the tolerance.
