# Review - bug mode

- source: tools/ui-harness.mjs
- reviewer: in-session colibri v0.2.0 (GLM-5.3, full repo context)
- date: 2026-09-06
- mode: bug (delta: catalog-brain-rows tier entry)
- context pack: the console-open pattern from optimizer-memory; the
  never-fire-a-download rule (GBs on the owner's line); the live PASS
  (get-it rows with ceilings rendered).

- **[FIXED, adversary round 2] the cold-machine trap** - the test now
  skips honestly with no brain and no key (never OPTIMIZE - that click
  provisions GBs), seats the spawn-free cloud brain through the power API
  when a key exists, and restores both the console and the brain state.

- **[FIXED, adversary round 3] the all-on-shelf skip leaked the seated
  brain** - that path now restores before skipping, like every other exit.



Shippable. DOM-asserts the rows, skips honestly when the whole catalog is
on the shelf, and restores the console state.

## Bugs & vulnerabilities

None CONFIRMED.
