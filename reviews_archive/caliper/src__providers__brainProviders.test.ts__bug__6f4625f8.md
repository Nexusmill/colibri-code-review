# Review - bug mode

- source: src/providers/brainProviders.test.ts
- reviewer: in-session colibri v0.2.0 (GLM-5.3, full repo context)
- date: 2026-09-06
- mode: bug (delta: the grounded-ceilings test)
- context pack: the six grounded HF values; the isCatalogBrain exclusion.

## Verdict

Shippable. The test pins every grounded value (drift is loud) and enforces
the ceiling-presence invariant for future brain additions.

## Bugs & vulnerabilities

None CONFIRMED.
