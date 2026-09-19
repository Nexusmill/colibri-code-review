<!-- source: src/components/SettingsConsole.test.tsx | reviewer: zcode-glm-5.3 | sha256: 04eb6bbf14b4947d0d2e28a762ed1c746d29d7e8a7f99c84e035b8250b7f54b6 | date: 2026-09-15 | mode: bug -->
<!-- context: Wave 6 FINAL delta review (post design-adversary remediation). Call sites traced live (curl through :4173, harness PASS 75/0/8, vitest 499/499, tsc 0); FEATURES row `route-intelligence` + docs/reviews/route-intelligence-2026-09-15.md are the contract. -->

## Verdict
Shippable - the suite covers the wave's row end to end with mocked edges, including the armed two-press flows.

## Fixed since last review (this delta)
- **[CONFIRMED|FIXED] mock factory lacked `routePreset`** - added; future preset interactions would have crashed on the missing export.

## Bugs & vulnerabilities (delta)
- None. Health fixtures seed both verdict orders per pick (recency pinned); the armed flows assert no-fire-on-first-press, the armed face text, and the fired calls; the failed row's danger color AND tooltip clause are asserted; shared mocks restored at teardown.
