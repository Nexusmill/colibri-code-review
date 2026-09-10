# colibri bug review - src/components/ModelPicker.tsx (delta)

source: src/components/ModelPicker.tsx · reviewer: ZCode GLM-5.3 in-session · sha256 c8bdd8a9 (full sha in manifest) · 2026-09-05 · mode: bug (delta vs 2cc3289b @ f9c5a4d 2026-08-24)
context: diff 16+6; prior review 2cc3289b carried; the shown-vs-sent class + the stale-response race class.

## Verdict

Shippable - the stale-catalog race guard and enum-without-default seeding in both default-extraction paths.

## Bugs & vulnerabilities

None new. A quick service flip can no longer land the old service's list under the new tab (alive flag); enum-first-option seeding makes the rendered selection the sent value in both the detail-schema and list-schema paths.

## Missing safeguards

- none new.

## Fixed since last review

- (prior had no open findings)
