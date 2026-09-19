<!-- source: src/film/autopilot.ts | reviewer: zcode-glm-5.3 | sha256: 1a1e91c9ce806185bedeead44ff58bbc49fa466ca720535b671b8d9eebce1635 | date: 2026-09-15 | mode: bug -->
<!-- context: owner vocabulary ruling 2026-09-15: COST TIERS - Tier 1 = the first combination, Tier 2 = the second; the two parts are the DRAFT MODEL and the FINISHING MODEL. Evidence: tsc 0, vitest 508/508, build OK, fast tier 77/0/7, live panel DOM-verified (banner, both buttons, both slot labels, zero old-vocabulary survivors) + screenshot read. -->

## Verdict
Shippable - the owner's vocabulary rules end to end: EngineTier is "tier1"|"tier2", the labels read TIER 1/TIER 2, the notes speak finishing passes.

## Fixed since last review (this delta)
- **[owner ruling 2026-09-15] the cost tiers are NAMED**: EngineTier keys cheap/expensive -> tier1/tier2 (contained: FilmWizard iterates keys, one test referenced them); labels "TIER 1 - p-video drafts, h3-max finishing" / "TIER 2 - h3-max drafts, h3 finishing"; the doctrine comment and the record-field doc comments speak draft model / finishing model throughout.

## Bugs & vulnerabilities (delta)
- None. The strategy VALUE "cheap-only" stays (persisted records carry it; its LABEL has read DRAFT ONLY since the owner's 09-14 rename).
