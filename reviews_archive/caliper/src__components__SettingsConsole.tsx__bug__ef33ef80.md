<!-- source: src/components/SettingsConsole.tsx | reviewer: zcode-glm-5.3 | sha256: ef33ef80b183cb782f4e8b187670cfe7667b464782b6f425861a16fbf87732ae | date: 2026-09-15 | mode: bug -->
<!-- context: owner vocabulary ruling 2026-09-15: COST TIERS - Tier 1 = the first combination, Tier 2 = the second; the two parts are the DRAFT MODEL and the FINISHING MODEL. Post-adversary sweep: the quality dial renders from one QUALITY_LABEL map (cheap->PRICE-FIRST persisted value kept), tooltips speak lowest-priced/low-rate, brain prompt says 'engines ordered price-first'. Evidence: tsc 0, vitest 508/508, build OK, fast tier 77/0/7, live DOM of engines panel + shape pane + settings film-defaults all assert the vocabulary with zero CHEAP survivors; grok-4.3 round 2 = no findings. -->

## Verdict
Shippable - the FILM DEFAULTS dial speaks the same names as the wizard's (one name per action), and the AUTO leg is price-speak.

## Fixed since last review (this delta - new to this rename)
- The quality select renders from the shared QUALITY_LABEL map (PRICE-FIRST/BALANCED/BEST-RATED); the AUTO option reads "the ladder picks the lowest-priced decent" and its tooltip matches; the dial's own tooltip says "price first, proven balance, or best-rated". Live-verified: no CHEAP anywhere in the FILM DEFAULTS section.

## Bugs & vulnerabilities (delta)
- None. The key-liveness tooltip's "one cheap authenticated read" is a different feature's price fact - out of this commission's scope, left.
