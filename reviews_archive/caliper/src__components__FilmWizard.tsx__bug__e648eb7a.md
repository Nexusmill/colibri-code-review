<!-- source: src/components/FilmWizard.tsx | reviewer: zcode-glm-5.3 | sha256: e648eb7a7628994bd6fff56de7555b3ac069a9c930eb04895ce02c581fd8b97a | date: 2026-09-15 | mode: bug -->
<!-- context: owner vocabulary ruling 2026-09-15: COST TIERS - Tier 1 = the first combination, Tier 2 = the second; the two parts are the DRAFT MODEL and the FINISHING MODEL. Post-adversary sweep: the quality dial renders from one QUALITY_LABEL map (cheap->PRICE-FIRST persisted value kept), tooltips speak lowest-priced/low-rate, brain prompt says 'engines ordered price-first'. Evidence: tsc 0, vitest 508/508, build OK, fast tier 77/0/7, live DOM of engines panel + shape pane + settings film-defaults all assert the vocabulary with zero CHEAP survivors; grok-4.3 round 2 = no findings. -->

## Verdict
Shippable - grok-4.3 round 2 on this exact sha: NO findings; all user-facing strings align with the cost-tiers vocabulary and the shared QUALITY_LABEL map.

## Fixed since last review (this delta)
- **[adversary round-1 MEDIUM] CHEAP-FIRST is gone**: the step-3 quality select renders PRICE-FIRST/BALANCED/BEST-RATED from the shared map; the two finish tooltips speak the draft model's low per-second rate; the battery tooltip grades "the lowest-priced candidate engines".

## Bugs & vulnerabilities (delta)
- None. Code comments quoting the owner's dated rationale (2026-08-29 "expensive leg") stay by design - comments are not user-facing.
