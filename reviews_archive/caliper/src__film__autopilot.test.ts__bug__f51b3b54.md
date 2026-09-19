<!-- source: src/film/autopilot.test.ts | reviewer: zcode-glm-5.3 | sha256: f51b3b54c61fcaf7cf94580c317bf7c22781f7fa1f7512b61510412efc79117b | date: 2026-09-15 | mode: bug -->
<!-- context: owner vocabulary ruling 2026-09-15: COST TIERS - Tier 1 = the first combination, Tier 2 = the second; the two parts are the DRAFT MODEL and the FINISHING MODEL. Post-adversary sweep: the quality dial renders from one QUALITY_LABEL map (cheap->PRICE-FIRST persisted value kept), tooltips speak lowest-priced/low-rate, brain prompt says 'engines ordered price-first'. Evidence: tsc 0, vitest 508/508, build OK, fast tier 77/0/7, live DOM of engines panel + shape pane + settings film-defaults all assert the vocabulary with zero CHEAP survivors; grok-4.3 round 2 = no findings. -->

## Verdict
Shippable - the strengths pin follows the rename.

## Bugs & vulnerabilities (delta)
- None. "lowest-rate usable motion" pinned where "cheapest usable motion" was; tier-catalog keys unchanged.
