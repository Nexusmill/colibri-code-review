<!-- source: tools/ui-harness.mjs | reviewer: zcode-glm-5.3 | sha256: 2369a2cdfdf2329e0f1bec24ad3c393ac6bb9d5c62eecc0fb43e263a95ec4232 | date: 2026-09-15 | mode: bug -->
<!-- context: owner vocabulary ruling 2026-09-15: COST TIERS - Tier 1 = the first combination, Tier 2 = the second; the two parts are the DRAFT MODEL and the FINISHING MODEL. Evidence: tsc 0, vitest 508/508, build OK, fast tier 77/0/7, live panel DOM-verified (banner, both buttons, both slot labels, zero old-vocabulary survivors) + screenshot read. -->

## Verdict
Shippable - the tier assertions pin the owner's vocabulary so the old words cannot return silently.

## Bugs & vulnerabilities (delta)
- None. The doctrine test requires the COST TIERS banner, TIER 1/TIER 2 labels (and presses Tier 1), and both slot labels - the FINISH MODEL half initially survived my rename (caught red by the tier, fixed to FINISHING MODEL); the finish-resolution test presses TIER 2.
