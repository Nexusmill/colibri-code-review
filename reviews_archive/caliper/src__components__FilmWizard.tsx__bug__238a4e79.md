<!-- source: src/components/FilmWizard.tsx | reviewer: zcode-glm-5.3 | sha256: 238a4e7945d8b9d08aa44e87db5e27b16abbbff828094dd2a061b87c0f12efd3 | date: 2026-09-15 | mode: bug -->
<!-- context: owner vocabulary ruling 2026-09-15: COST TIERS - Tier 1 = the first combination, Tier 2 = the second; the two parts are the DRAFT MODEL and the FINISHING MODEL. Evidence: tsc 0, vitest 508/508, build OK, fast tier 77/0/7, live panel DOM-verified (banner, both buttons, both slot labels, zero old-vocabulary survivors) + screenshot read. -->

## Verdict
Shippable - every user-facing string in the panel speaks the owner's vocabulary; the live panel carries zero old-vocabulary survivors.

## Fixed since last review (this delta)
- **[owner ruling 2026-09-15] the panel reads THE COST TIERS - the draft model rehearses, the finishing model delivers**; FINISH MODEL -> FINISHING MODEL (slot label, the FINISH button fallback, its tooltip); the strategy tooltips say Tier 2 and finishing pass; the suggestion line and the finishing-run status speak finishing model.

## Bugs & vulnerabilities (delta)
- None found - the live DOM sweep (panel walk + harness + a dedicated no-old-vocabulary probe) found and fixed the last two stragglers ("finish model" in the suggestion line and the FINISH tooltip fallback).
