<!-- source: src/film/autopilot.ts | reviewer: zcode-glm-5.3 | sha256: d5bc2d8e83f71c1a1ddaab231639466f904e29173c43d5f56a06a762f441855b | date: 2026-09-15 | mode: bug -->
<!-- context: owner vocabulary ruling 2026-09-15: COST TIERS - Tier 1 = the first combination, Tier 2 = the second; the two parts are the DRAFT MODEL and the FINISHING MODEL. Post-adversary sweep: the quality dial renders from one QUALITY_LABEL map (cheap->PRICE-FIRST persisted value kept), tooltips speak lowest-priced/low-rate, brain prompt says 'engines ordered price-first'. Evidence: tsc 0, vitest 508/508, build OK, fast tier 77/0/7, live DOM of engines panel + shape pane + settings film-defaults all assert the vocabulary with zero CHEAP survivors; grok-4.3 round 2 = no findings. -->

## Verdict
Shippable - the owner's vocabulary rules end to end, and the quality dial gained ONE name for each mode.

## Fixed since last review (this delta)
- **[adversary round-1 catch] the quality dial's label**: QUALITY_LABEL (cheap->PRICE-FIRST / balanced / BALANCED / best->BEST-RATED) is the single source for the wizard select, the settings dial, and the critique prompt ("engines ordered price-first", was "at cheap engine tier"). The VALUES persist in saved shapes/defaults and keep their historical names - the same containment ruling as the strategy value "cheap-only".
- **[vocabulary] p-video's strengths line** reads "the lowest-rate usable motion at $0.02/s" (was "cheapest usable motion") - same price truth, no banned word.

## Bugs & vulnerabilities (delta)
- None. Tier keys/labels/notes already ruled clean in the first pass this sha supersedes.
