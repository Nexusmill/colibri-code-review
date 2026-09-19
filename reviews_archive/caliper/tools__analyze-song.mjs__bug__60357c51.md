<!-- source: tools/analyze-song.mjs | reviewer: zcode-glm-5.3 | sha256: 60357c51e3a0d6517a4858408c3cb35068f150ff9e82af17703a46eaeed8cc7b | date: 2026-09-15 | mode: bug -->
<!-- context: Wave 7 (the analysis trio: beat-snapped carves, phrase grid for joins, legacy grid retirement) FINAL delta review. Live evidence: tsc -b --force 0, vitest 502/502, build OK, fast tier 76/0/8 incl. cut-on-the-music, live tool run on a real song: 74/74 interior cuts exactly on a beat, 69 phrases. -->

## Verdict
Shippable - the tool prints the carve the pipeline actually cuts on; the JSON keeps its shotGrid key (film-proof reads .start/.end only - GridSlot satisfies both) and gains phrases.

## Bugs & vulnerabilities (delta)
- None. The section column uses slot midpoints (a straddling slot is assigned one section - an honest diagnostic approximation); the decode guards are untouched.
