<!-- source: tools/ui-harness.mjs | reviewer: zcode-glm-5.3 | sha256: c4d093ea56eb75d8739375f86d7486c6c960932de5b6cb27a7ca2e5a720572a9 | date: 2026-09-15 | mode: bug -->
<!-- context: Wave 6 FINAL delta review (post design-adversary remediation + adversarial commit gate __proto__ catch). Live evidence: harness PASS 75/0/8 with the __proto__ pin, vitest 499/499, tsc 0. -->

## Verdict
Shippable - five latent defects in the new test were found and fixed this session (four by my review pass, one by the commit gate), all confirmed by the now-PASSing test through the real app.

## Fixed since last review (this delta)
- **[CONFIRMED|FIXED] delete clicked the RESTORE chip** - the delete is the sibling; now walked as the armed DELETE->CONFIRM pair.
- **[CONFIRMED|FIXED] whole-document gone-check false-failed** (status line carries the name) - scoped to chip buttons.
- **[CONFIRMED|FIXED] TS generic in a .mjs evaluate** parsed as a comparison chain - replaced with page.click.
- **[CONFIRMED|FIXED] stranded chips self-heal** - `harness ` AND `__proto__` chips are armed-and-deleted before the test starts.
- **[CONFIRMED|FIXED per commit gate] the __proto__ pollution had no pin** - the test now saves a preset literally named __proto__ and asserts the honest `preset "__proto__" saved` status (the pre-fix server said "replaced" here - red by construction), the chip renders from the server's own list, and the armed delete removes it.

## Bugs & vulnerabilities
- None remaining in the delta.
